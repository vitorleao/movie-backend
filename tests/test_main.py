from fastapi.testclient import TestClient # type: ignore
from app.main import app, db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Status": "Online"}

def test_read_search_valid():
    response = client.get("/movies/search?user=usuario&movie=The Hobbit Series")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json() is not None
    assert db["external_data"].find_one() is not None

def test_read_search_invalid():
    response = client.get("/movies/search")
    assert response.status_code == 400
    assert response.json() == {"Error": "Please, inform a valid movie name."}

def test_read_history_valid():
    response = client.get("/movies/history")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json() is not None