def test_esign_initiate(client):
    payload = {
        "loan_id": 1,
        "aadhar_number": "123412341234"
    }
    response = client.post("/api/v1/loan/esign/initiate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "transaction_id" in data["data"]
    
def test_esign_verify(client):
    # First initiate
    init_payload = {
        "loan_id": 1,
        "aadhar_number": "123412341234"
    }
    init_res = client.post("/api/v1/loan/esign/initiate", json=init_payload)
    txn_id = init_res.json()["data"]["transaction_id"]

    # Now verify
    verify_payload = {
        "transaction_id": txn_id,
        "otp": "123456"
    }

    response = client.post("/api/v1/loan/esign/verify", json=verify_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    