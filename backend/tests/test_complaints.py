from datetime import datetime, timedelta, timezone
from app.services.overdue import calculate_overdue_risk_score, is_complaint_overdue

def test_overdue_risk_score_calculation():
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(days=4)
    risk_score = calculate_overdue_risk_score(created_at, "Electrical", "Open")
    assert risk_score == 2.0
    assert is_complaint_overdue(created_at, "Electrical", "Open") is True

def test_resolved_complaint_zero_risk():
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(days=10)
    risk_score = calculate_overdue_risk_score(created_at, "Electrical", "Resolved")
    assert risk_score == 0.0
    assert is_complaint_overdue(created_at, "Electrical", "Resolved") is False
