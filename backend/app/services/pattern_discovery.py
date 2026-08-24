import logging
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
import httpx

from app.core.config import settings

logger = logging.getLogger("nexus.pattern_discovery")

_EMBEDDING_MODEL = None

def get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers model ('all-MiniLM-L6-v2')...")
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
            _EMBEDDING_MODEL.encode(["NEXUS warmup string"])
        except ImportError:
            raise RuntimeError(
                "CRITICAL SETUP ERROR: sentence-transformers is mandatory for NEXUS Emergent Pattern Discovery. "
                "Please install `sentence-transformers>=2.2.2`."
            )
    return _EMBEDDING_MODEL

def get_hdbscan_clusterer(min_cluster_size: int = 2):
    """
    HDBSCAN is MANDATORY per spec. Checks for hdbscan or sklearn.cluster.HDBSCAN.
    """
    try:
        from sklearn.cluster import HDBSCAN
        return HDBSCAN(min_cluster_size=min_cluster_size, min_samples=1, allow_single_cluster=True, cluster_selection_epsilon=0.95, metric="euclidean")
    except ImportError:
        try:
            import hdbscan
            return hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=1, allow_single_cluster=True, cluster_selection_epsilon=0.95, metric="euclidean")
        except ImportError:
            raise RuntimeError(
                "CRITICAL SETUP ERROR: HDBSCAN is mandatory for NEXUS Emergent Pattern Discovery. "
                "Please install `hdbscan` or `scikit-learn>=1.3`."
            )

def calculate_pattern_strength_metrics(
    embeddings: List[List[float]],
    categories: List[str],
    timestamps: List[datetime],
    t_max_days: float = 7.0
) -> Tuple[float, float, float, float, float]:
    """
    Pure, independently unit-testable function to compute Pattern Strength and sub-scores.
    Returns: (pattern_strength, cohesion_score, size_score, category_score, temporal_score)
    All scores are normalized to [0, 100].
    """
    count = len(embeddings)
    if count == 0:
        return (0.0, 0.0, 0.0, 0.0, 0.0)

    vecs = np.array(embeddings)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    norm_vecs = vecs / norms
    
    sim_matrix = np.dot(norm_vecs, norm_vecs.T)
    if count > 1:
        mask = ~np.eye(count, dtype=bool)
        avg_cosine = float(np.mean(sim_matrix[mask]))
    else:
        avg_cosine = 1.0

    cohesion_score = round(((avg_cosine + 1.0) / 2.0) * 100.0, 2)

    size_score = round(min(100.0, max(0.0, ((count - 2) / 10.0) * 100.0)), 2)

    distinct_cats = len(set(categories))
    category_score = round(min(100.0, max(0.0, ((distinct_cats - 1) / 4.0) * 100.0)), 2)

    ts_seconds = [t.timestamp() if t.tzinfo else t.replace(tzinfo=timezone.utc).timestamp() for t in timestamps]
    if len(ts_seconds) > 1:
        span_days = (max(ts_seconds) - min(ts_seconds)) / 86400.0
    else:
        span_days = 0.0

    temporal_score = round(max(0.0, (1.0 - (span_days / t_max_days))) * 100.0, 2)

    pattern_strength = round((cohesion_score + size_score + category_score + temporal_score) / 4.0, 2)

    return (pattern_strength, cohesion_score, size_score, category_score, temporal_score)


async def generate_cluster_label(
    complaint_texts: List[str],
    categories: List[str],
    weather_events: List[str]
) -> Tuple[str, str, str]:
    """
    LLM Cluster Summarization (Downstream of detection).
    Returns (name, description, label_source).
    label_source is 'llm' if generated via OpenAI/Anthropic API, or 'fallback' if generated deterministically.
    """
    distinct_cats = list(set(categories))
    cat_str = ", ".join(distinct_cats)
    sample_text = " | ".join([t[:80] for t in complaint_texts[:5]])
    
    if settings.OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                prompt = (
                    f"You are NEXUS, an AI pattern labeler for a society maintenance platform.\n"
                    f"A mathematical cluster was detected across predefined categories: {cat_str}.\n"
                    f"Complaint excerpts:\n{sample_text}\n"
                    f"Weather context: {', '.join(filter(None, set(weather_events))) or 'None'}.\n\n"
                    f"Provide a concise name (3-6 words) and brief description (1-2 sentences) for this emergent pattern.\n"
                    f"Format: NAME: <name>\nDESCRIPTION: <description>"
                )
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 120,
                        "temperature": 0.3
                    },
                    timeout=5.0
                )
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    lines = content.strip().split("\n")
                    name = "Emergent Pattern"
                    desc = "Cross-category operational issue detected."
                    for line in lines:
                        if line.startswith("NAME:"):
                            name = line.replace("NAME:", "").strip()
                        elif line.startswith("DESCRIPTION:"):
                            desc = line.replace("DESCRIPTION:", "").strip()
                    return (name, desc, "llm")
        except Exception as e:
            logger.warning(f"OpenAI LLM labeling call failed: {e}. Utilizing deterministic fallback label.")

    weather_str = next((w for w in weather_events if w), None)
    if weather_str:
        name = f"Emergent Pattern: {weather_str} Impact — ({cat_str})"
        desc = f"Emergent cluster spanning {cat_str} triggered following {weather_str}."
    else:
        name = f"Emergent Cross-Category Pattern ({cat_str})"
        desc = f"Emergent cross-category complaint cluster spanning complaints in {cat_str} identified via vector clustering."

    return (name, desc, "fallback")


async def discover_emergent_patterns(complaints_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Main Pattern Discovery Pipeline:
    Complaints -> Embeddings -> HDBSCAN -> Cross-category Filter (>=2 categories) -> Pattern Strength -> LLM Labeler
    """
    if len(complaints_data) < 3:
        logger.info(f"Insufficient complaints ({len(complaints_data)}) for clustering. Minimum required is 3.")
        return []

    import asyncio
    model = get_embedding_model()
    texts = [c["description"] for c in complaints_data]
    raw_embeddings = await asyncio.to_thread(model.encode, texts)
    
    from sklearn.preprocessing import normalize
    norm_embeddings = normalize(raw_embeddings)
    embeddings = norm_embeddings.tolist()

    min_cluster_size = 2
    clusterer = get_hdbscan_clusterer(min_cluster_size=min_cluster_size)
    cluster_labels = clusterer.fit_predict(norm_embeddings)

    discovered_patterns = []
    unique_clusters = set(cluster_labels)
    unique_clusters.discard(-1)

    for cluster_id in unique_clusters:
        indices = np.where(cluster_labels == cluster_id)[0]
        cluster_complaints = [complaints_data[i] for i in indices]
        cluster_embeddings = [embeddings[i] for i in indices]
        
        cluster_categories = [c["category"] for c in cluster_complaints]
        distinct_categories = set(cluster_categories)

        if len(cluster_complaints) < 3:
            logger.info(f"Cluster {cluster_id} rejected by size filter: contains only {len(cluster_complaints)} complaints (minimum required is 3).")
            continue

        if len(distinct_categories) < 2:
            logger.info(f"Cluster {cluster_id} rejected by cross-category filter: only {len(distinct_categories)} category represented.")
            continue

        cluster_timestamps = [c["created_at"] for c in cluster_complaints]

        pattern_strength, cohesion, size_score, cat_score, temp_score = calculate_pattern_strength_metrics(
            cluster_embeddings,
            cluster_categories,
            cluster_timestamps
        )

        weather_events = [c.get("weather_event") for c in cluster_complaints]
        name, desc, label_source = await generate_cluster_label(
            [c["description"] for c in cluster_complaints],
            cluster_categories,
            weather_events
        )

        complaint_ids = [c["id"] for c in cluster_complaints]

        discovered_patterns.append({
            "name": name,
            "description": desc,
            "strength_score": pattern_strength,
            "cohesion": cohesion,
            "size": size_score,
            "category_spread": cat_score,
            "temporal_concentration": temp_score,
            "complaint_ids": complaint_ids,
            "label_source": label_source,
            "status": "Active"
        })

    return discovered_patterns
