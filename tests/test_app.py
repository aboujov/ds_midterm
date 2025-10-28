import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.server import app

def test_health():
    client = app.test_client()
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"

def test_echo():
    client = app.test_client()
    payload = {"msg": "pytest"}
    res = client.post('/echo', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["received"] == payload
    assert data["ok"] is True
