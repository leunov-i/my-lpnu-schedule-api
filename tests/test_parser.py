from app.parser import get_schedule_data

def test_schedule_parsing():
    data = get_schedule_data("КН-123")
    assert isinstance(data, list)
    assert all("dayOfWeek" in day for day in data)