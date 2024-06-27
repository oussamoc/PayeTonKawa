import pytest
from app import app as webshop_app
from distributors_api import app as distributors_app

@pytest.fixture
def client():
    webshop_app.config['TESTING'] = True
    client = webshop_app.test_client()
    yield client

@pytest.fixture
def distributors_client():
    distributors_app.config['TESTING'] = True
    client = distributors_app.test_client()
    yield client

def test_get_products(client):
    rv = client.get('/products', headers={'x-api-key': 'webshop_api_key'})
    assert rv.status_code == 200
    assert b'Coffee A' in rv.data

def test_get_orders(distributors_client):
    rv = distributors_client.get('/orders', headers={'x-api-key': 'distributor_1_key'})
    assert rv.status_code == 200
    assert b'customer_id' in rv.data
