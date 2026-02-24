def test_agreement_fetch(client):
    response = client.get("/api/v1/loan/agreement/1")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "pdf_path" in data["data"]