from fastapi.testclient import TestClient
from pytest import fixture

from src.app import app


@fixture
def client() -> TestClient:
    return TestClient(app)

def test_post_image() -> None:
    client = TestClient(app=app)
    sample_cat_image = "https://i.natgeofe.com/n/4cebbf38-5df4-4ed0-864a-4ebeb64d33a4/NationalGeographic_1468962_16x9.jpg"
    user_data = {"image_url": sample_cat_image}
    response = client.post(
        "/classify",
        headers={"content-type": "application/json"},
        json=user_data,
    )
    assert response.status_code == 200
    results = response.json()["results"]
    inference_time = response.json()["inference_time_ms"]
    assert inference_time < 2000.0

    # check that somewhere there is the word cat!
    assert "cat" in str(results).lower()
