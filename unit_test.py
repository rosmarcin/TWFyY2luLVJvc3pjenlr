# CASE 1: Tworzenie nowego obiektu
# route: /api/fetcher
# method: POST
# payload: '{"url": "https://httpbin.org/range/15","interval":60}'
# response: HTTP/1.1 200 OK
# response payload: {"id": <int>} Wynik w formacie JSON jako obiekt.

# CASE 2 - Niepoprawne wywołanie (nieprawidłowy klucz):
# route: /api/fetcher
# method: POST
# payload: niepoprawny json '{"xyz": "https://httpbin.org/range/15"}'
# response: status: HTTP/1.1 400 Bad Request 

# CASE 3 - Niepoprawne wywołanie (za duży obiekt):
# route: /api/fetcher
# method: POST
# payload: > 1MB 
# response: status: ' HTTP/1.1 413 Request Entity Too Large 

# CASE 4: Listowanie zapisanych urli 
# route: /api/fetcher
# method: GET
# response: HTTP/1.1 200 OK
# response payload: [{"id": <int>, "url":"http..", "interval":<int>},]

# CASE 5: Aktualizacja obiektu
# route: /api/fetcher/<id>
# method: POST
# payload: '{"url": "https://httpbin.org/range/15","interval":60}'
# response: HTTP/1.1 200 OK
# response payload: {"id": <int>}

# CASE 6: Usuwanie URLa
# route: /api/fetcher/<id>
# method: DELETE
# response: HTTP/1.1 200 OK

# CASE 7: Usuwanie URLa - błędny klucz
# route: /api/fetcher/<err_id>
# method: DELETE
# response: status: HTTP/1.1 400 Bad Request 

# CASE 8: Aktualizacja obiektu
# route: /api/fetcher
# method: GET
# response: HTTP/1.1 200 OK
# response payload: [{"id": <int>, "url":"http..", "interval":<int>},]


# CASE 9: Pobieranie historii pobrań
# route: /api/fetcher/<id>/history
# method: GET
# response: HTTP/1.1 200 OK
# response payload: [
# {
# "response": "abcdefghijklmno",
# "duration": 0.571,
# "created_at": 1559034638.31525,
# },
# {
# "response": null,
# "duration": 5,
# "created_at": 1559034938.623,
# },
# ]


import pytest
from flask import Flask

from .server import app

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

# CASE 1: Tworzenie nowego obiektu
def test_put_new_url(client):
    response = client.post('/api/fetcher', json={'url':'https://httpbin.org/range/15', 'interval':60})
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert isinstance(response.json, dict)
    assert set(response.json.keys()) == {'id'}

def test_put_new_url(client):
    response = client.post('/api/fetcher', json={'url':'https://httpbin.org/range/15'})
    assert response.status_code == 400

def test_put_new_url(client):
    response = client.post('/api/fetcher', json={'url':'https://httpbin.org/range/15', 'interval':'a'})
    assert response.status_code == 400

def test_put_new_url(client):
    response = client.post('/api/fetcher', json={'url1':'https://httpbin.org/range/15', 'interval':2})
    assert response.status_code == 400


# # CASE 2: Aktualizacja obiektu
# def test_update_url(client):
#   response = client.post('/api/fetcher', data=dict(url='https://httpbin.org/range/15', interval=60))
#   assert response.status_code == 200


# CASE 4: Listowanie zapisanych urli 
# route: /api/fetcher
# method: GET
# response: HTTP/1.1 200 OK
# response payload: [{"id": <int>, "url":"http..", "interval":<int>},]

def test_get_all_urls(client):
    response = client.get('/api/fetcher')
    assert response.status_code == 200
    #assert response.content_type == 'application/json'
    # assert isinstance(response.json, dict)
    # assert set(response.json.keys()) == {'id'}


# # CASE 9: Pobieranie historii pobrań
# def test_retrieve_fetch_history(client):
#   response = client.get('/api/fetcher/1/history', data=dict(url='https://httpbin.org/range/15', interval=60))
#   assert response.status_code == 200


@pytest.fixture
def client():
    client = app.test_client()

    return client