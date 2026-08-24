from datetime import datetime, timezone

CATEGORY_THRESHOLDS_DAYS = {
    "Electrical": 2.0,
    "Plumbing": 3.0,
    "Cosmetic": 7.0,
    "Cleaning": 1.0,
    "General": 4.0
}

DEFAULT_THRESHOLD_DAYS = 3.0

def calculate_overdue_risk_score(created_at: datetime, category: str, status: str) -> float:
    """
    Computes the weighted overdue risk score:
    risk_score = days_open / category_avg_resolution_time
    Returns 0.0 if already Resolved.
    """
    if status == "Resolved":
        return 0.0

    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
        
    days_open = (now - created_at).total_seconds() / 86400.0
    avg_resolution_time = CATEGORY_THRESHOLDS_DAYS.get(category, DEFAULT_THRESHOLD_DAYS)
    
    risk_score = days_open / avg_resolution_time
    return round(risk_score, 2)

def is_complaint_overdue(created_at: datetime, category: str, status: str) -> bool:
    """
    Returns True if an open/in-progress complaint exceeds its category resolution threshold.
    """
    if status == "Resolved":
        return False
        
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    days_open = (now - created_at).total_seconds() / 86400.0
    threshold = CATEGORY_THRESHOLDS_DAYS.get(category, DEFAULT_THRESHOLD_DAYS)
    return days_open > threshold
