
def test_disbursement_status(client):
    response = client.get("/api/v1/loan/disbursement/1/status")
    assert response.status_code == 200
    assert response.json()["success"] is True
    
def test_disbursement_confirm(client):
    payload = {
        "loan_id": 1,
        "remarks": "ok"
    }
    response = client.post("/api/v1/loan/disbursement/confirm", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True    