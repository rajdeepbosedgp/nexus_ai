import pytest
from datetime import datetime, timedelta, timezone
from app.services.pattern_discovery import (
    calculate_pattern_strength_metrics,
    discover_emergent_patterns
)

def test_pure_scoring_function_equal_weights():
    # Test case: 10 complaints, 4 categories, zero time span, perfect vectors
    embeddings = [[1.0, 0.0, 0.0] for _ in range(10)]
    categories = ["Plumbing", "Cleaning", "General", "Electrical"] * 2 + ["Plumbing", "Cleaning"]
    now = datetime.now(timezone.utc)
    timestamps = [now for _ in range(10)]

    strength, cohesion, size_score, category_score, temporal_score = calculate_pattern_strength_metrics(
        embeddings, categories, timestamps
    )

    assert cohesion == 100.0  # perfect similarity
    assert size_score == 80.0  # (10-2)/10 * 100
    assert category_score == 75.0  # (4-1)/4 * 100
    assert temporal_score == 100.0  # 0 span
    assert strength == round((100.0 + 80.0 + 75.0 + 100.0) / 4.0, 2)  # 88.75

def test_cosine_normalization_bounds():
    # Negative cosine similarity vectors (-1)
    embeddings = [[1.0, 0.0], [-1.0, 0.0]]
    categories = ["Plumbing", "Electrical"]
    now = datetime.now(timezone.utc)
    timestamps = [now, now]

    strength, cohesion, size_score, category_score, temporal_score = calculate_pattern_strength_metrics(
        embeddings, categories, timestamps
    )

    assert cohesion == 0.0  # (-1 + 1)/2 * 100 = 0
    assert 0.0 <= strength <= 100.0

@pytest.mark.asyncio
async def test_single_category_filter():
    # 6 complaints all in Plumbing -> Must yield 0 patterns due to >=2 category requirement
    now = datetime.now(timezone.utc)
    complaints = [
        {
            "id": f"c_{i}",
            "category": "Plumbing",
            "description": f"Water leak in pipe number {i}",
            "created_at": now,
            "weather_event": None
        }
        for i in range(6)
    ]
    patterns = await discover_emergent_patterns(complaints)
    assert len(patterns) == 0  # Fails cross-category filter

@pytest.mark.asyncio
async def test_insufficient_data_filter():
    # 2 complaints -> Skipped
    now = datetime.now(timezone.utc)
    complaints = [
        {"id": "1", "category": "Plumbing", "description": "Leak A", "created_at": now, "weather_event": None},
        {"id": "2", "category": "Electrical", "description": "Spark B", "created_at": now, "weather_event": None}
    ]
    patterns = await discover_emergent_patterns(complaints)
    assert len(patterns) == 0

@pytest.mark.asyncio
async def test_duplicate_complaints_same_category():
    # Identical text in same category -> 0 patterns detected (fails cross-category filter)
    now = datetime.now(timezone.utc)
    complaints = [
        {"id": f"dup_{i}", "category": "Plumbing", "description": "Water leaking from main kitchen pipe duct", "created_at": now, "weather_event": None}
        for i in range(5)
    ]
    patterns = await discover_emergent_patterns(complaints)
    assert len(patterns) == 0

@pytest.mark.asyncio
async def test_strong_pattern_discovery_behavior():
    # 10 complaints across 4 categories during Heavy Rain -> Behavioral pattern check
    now = datetime.now(timezone.utc)
    strong_items = [
        ("Plumbing", "Water collecting and pooling near C-204 ceiling joint after heavy rain", "Heavy Rain"),
        ("Plumbing", "Water seepage through outer wall in C-205 hallway following rainfall", "Heavy Rain"),
        ("Cleaning", "Damp wall after rainfall causing ceiling mold and water stains", "Heavy Rain"),
        ("Cleaning", "Floor requires repeated cleaning due to rainwater dripping from corridor beam", "Heavy Rain"),
        ("General", "Moisture appearing near Block C stairwell and plaster peeling post rain", "Heavy Rain"),
        ("General", "Wall stain and damp patch forming after heavy rain near elevator shaft C", "Heavy Rain"),
        ("Electrical", "Water seepage near Block C electric distribution box causing short circuit risk", "Heavy Rain"),
        ("Electrical", "Dampness leaking into corridor light fixture near Block C 2nd floor post rainfall", "Heavy Rain"),
        ("Plumbing", "Water trickling down Block C pipe duct shaft after heavy rain", "Heavy Rain"),
        ("Cleaning", "Persistent water puddle and moisture smell in Block C lobby post heavy rain", "Heavy Rain"),
    ]
    complaints = [
        {
            "id": f"strong_{i}",
            "category": cat,
            "description": desc,
            "created_at": now - timedelta(hours=i * 0.1),
            "weather_event": weather
        }
        for i, (cat, desc, weather) in enumerate(strong_items)
    ]
    patterns = await discover_emergent_patterns(complaints)
    assert len(patterns) >= 1
    p = patterns[0]
    assert p["strength_score"] > 0.0
    assert 0.0 <= p["strength_score"] <= 100.0
    assert len(p["complaint_ids"]) >= 3

