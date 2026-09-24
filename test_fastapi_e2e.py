import pytest
from playwright.sync_api import Playwright, APIRequestContext, expect

# Assuming the FastAPI server is running locally on port 8000
BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> APIRequestContext:
    """
    Sets up a Playwright APIRequestContext for the test session.
    """
    request_context = playwright.request.new_context(base_url=BASE_URL)
    yield request_context
    request_context.dispose()

# Test variables to keep track of state across tests
# NOTE: In a real environment, it's better to keep tests isolated. 
# We're grouping these for a straightforward CRUD flow example.
test_data = {
    "transaction_id": None
}

def test_create_transaction(api_context: APIRequestContext):
    """
    Test CREATE: POST /transactions
    """
    new_transaction = {
        "customer_id": 105,
        "amount": 150.50,
        "date": "2023-10-05",
        "status": "PENDING"
    }
    
    response = api_context.post("/transactions", data=new_transaction)
    
    # Assert successful creation
    assert response.ok
    assert response.status == 201 or response.status == 200
    
    data = response.json()
    assert "id" in data
    
    # Save ID for later tests
    test_data["transaction_id"] = data["id"]
    
    # Verify the returned data matches what we sent
    assert data["customer_id"] == new_transaction["customer_id"]
    assert data["amount"] == new_transaction["amount"]
    assert data["status"] == new_transaction["status"]

def test_read_transaction(api_context: APIRequestContext):
    """
    Test READ: GET /transactions/{id}
    """
    # Ensure we have a transaction ID from the previous test
    transaction_id = test_data["transaction_id"]
    assert transaction_id is not None, "Transaction ID not set from create test"
    
    response = api_context.get(f"/transactions/{transaction_id}")
    
    # Assert successful retrieval
    assert response.ok
    assert response.status == 200
    
    data = response.json()
    assert data["id"] == transaction_id
    assert data["customer_id"] == 105
    assert data["status"] == "PENDING"

def test_update_transaction(api_context: APIRequestContext):
    """
    Test UPDATE: PUT or PATCH /transactions/{id}
    """
    transaction_id = test_data["transaction_id"]
    assert transaction_id is not None
    
    # Update the status
    update_payload = {
        "status": "COMPLETED"
    }
    
    # Assuming the API uses PATCH for partial updates, or PUT.
    response = api_context.patch(f"/transactions/{transaction_id}", data=update_payload)
    
    assert response.ok
    assert response.status == 200
    
    data = response.json()
    assert data["status"] == "COMPLETED"

def test_delete_transaction(api_context: APIRequestContext):
    """
    Test DELETE: DELETE /transactions/{id}
    """
    transaction_id = test_data["transaction_id"]
    assert transaction_id is not None
    
    response = api_context.delete(f"/transactions/{transaction_id}")
    
    # Typically returns 200 OK or 204 No Content
    assert response.ok
    assert response.status in (200, 204)

def test_read_deleted_transaction_returns_404(api_context: APIRequestContext):
    """
    Test READ after DELETE: GET /transactions/{id} should return 404
    """
    transaction_id = test_data["transaction_id"]
    assert transaction_id is not None
    
    response = api_context.get(f"/transactions/{transaction_id}")
    
    # Should not find the deleted record
    assert response.status == 404
