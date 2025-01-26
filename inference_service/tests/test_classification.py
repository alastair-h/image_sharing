from fastapi.testclient import TestClient
from pytest import fixture, mark
from http import HTTPStatus
from src.app import app


@fixture
def client() -> TestClient:
    return TestClient(app)


@mark.skip(reason="This would be an expensive tset to run, and will fail without an API key")
def test_get_caption_image() -> None:
    client = TestClient(app=app)
    sample_cat_image = (
        "https://i.natgeofe.com/n/4cebbf38-5df4-4ed0-864a-4ebeb64d33a4/NationalGeographic_1468962_16x9.jpg"
    )
    user_data = {"image_url": sample_cat_image}
    response = client.post(
        "/caption",
        headers={"content-type": "application/json"},
        json=user_data,
    )
    assert response.status_code == HTTPStatus.OK
    results = response.json()["caption"]
    inference_time = response.json()["inference_time_ms"]
    assert inference_time < 5000.0  # I think that
    # sample response = 'An orange cat in a playful stance.
    # check that somewhere there is the word cat!
    assert "cat" in results.lower()
