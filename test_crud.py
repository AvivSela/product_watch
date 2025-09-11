#!/usr/bin/env python3
"""
Simple test script to verify CRUD operations work correctly.
Run this after starting the FastAPI server.
"""

import requests

BASE_URL = "http://localhost:8000"


def test_crud_operations():
    """Test all CRUD operations"""
    print("Testing CRUD Operations...")

    # Test 1: Create a new item
    print("\n1. Creating a new item...")
    new_item = {
        "name": "Test Product",
        "description": "A test product for CRUD operations",
        "price": 29.99,
    }

    response = requests.post(f"{BASE_URL}/items", json=new_item)
    if response.status_code == 201:
        created_item = response.json()
        print(f"✅ Item created successfully: ID {created_item['id']}")
        item_id = created_item["id"]
    else:
        print(f"❌ Failed to create item: {response.status_code} - {response.text}")
        return

    # Test 2: Read the created item
    print("\n2. Reading the created item...")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    if response.status_code == 200:
        item = response.json()
        print(f"✅ Item retrieved: {item['name']} - ${item['price']}")
    else:
        print(f"❌ Failed to read item: {response.status_code} - {response.text}")

    # Test 3: Update the item
    print("\n3. Updating the item...")
    update_data = {"name": "Updated Test Product", "price": 39.99}

    response = requests.put(f"{BASE_URL}/items/{item_id}", json=update_data)
    if response.status_code == 200:
        updated_item = response.json()
        print(f"✅ Item updated: {updated_item['name']} - ${updated_item['price']}")
    else:
        print(f"❌ Failed to update item: {response.status_code} - {response.text}")

    # Test 4: Test pagination
    print("\n4. Testing pagination...")
    response = requests.get(f"{BASE_URL}/items?page=1&size=5")
    if response.status_code == 200:
        paginated_response = response.json()
        print(
            f"✅ Pagination works: {len(paginated_response['items'])} items on page {paginated_response['page']} of {paginated_response['pages']}"
        )
    else:
        print(f"❌ Failed to test pagination: {response.status_code} - {response.text}")

    # Test 5: Test search
    print("\n5. Testing search...")
    response = requests.get(f"{BASE_URL}/items/search?q=Test&page=1&size=5")
    if response.status_code == 200:
        search_response = response.json()
        print(
            f"✅ Search works: Found {search_response['total']} items matching 'Test'"
        )
    else:
        print(f"❌ Failed to test search: {response.status_code} - {response.text}")

    # Test 6: Delete the item
    print("\n6. Deleting the item...")
    response = requests.delete(f"{BASE_URL}/items/{item_id}")
    if response.status_code == 204:
        print("✅ Item deleted successfully")
    else:
        print(f"❌ Failed to delete item: {response.status_code} - {response.text}")

    # Test 7: Verify item is deleted
    print("\n7. Verifying item is deleted...")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    if response.status_code == 404:
        print("✅ Item successfully deleted (404 Not Found)")
    else:
        print(f"❌ Item still exists: {response.status_code} - {response.text}")

    print("\n🎉 CRUD operations test completed!")


if __name__ == "__main__":
    try:
        test_crud_operations()
    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to the server. Make sure the FastAPI server is running on http://localhost:8000"
        )
    except Exception as e:
        print(f"❌ An error occurred: {e}")
