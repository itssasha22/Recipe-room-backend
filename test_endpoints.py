#!/usr/bin/env python3
import requests

BASE = "http://localhost:5000/api"

# 1. Register user
print("1. Registering user...")
r = requests.post(f"{BASE}/auth/register", json={
    "username": "testuser",
    "email": "test@test.com",
    "password": "password123"
})
print(r.json())

# 2. Login
print("\n2. Logging in...")
r = requests.post(f"{BASE}/auth/login", json={
    "email": "test@test.com",
    "password": "password123"
})
token = r.json().get('access_token')
print(f"Token: {token[:20]}...")

# 3. Search recipes
print("\n3. Searching recipes...")
r = requests.get(f"{BASE}/recipes/discover")
print(r.json())

# 4. Search by name
print("\n4. Search by name 'pasta'...")
r = requests.get(f"{BASE}/recipes/discover?name=pasta")
print(r.json())

# 5. Rate recipe (needs recipe_id, use 1 for test)
print("\n5. Rating recipe...")
r = requests.post(f"{BASE}/recipes/1/rate", 
    headers={"Authorization": f"Bearer {token}"},
    json={"value": 5}
)
print(r.json())

# 6. Get rating
print("\n6. Getting recipe rating...")
r = requests.get(f"{BASE}/recipes/1/rating")
print(r.json())

# 7. Bookmark recipe
print("\n7. Bookmarking recipe...")
r = requests.post(f"{BASE}/recipes/1/bookmark",
    headers={"Authorization": f"Bearer {token}"}
)
print(r.json())

# 8. Remove bookmark
print("\n8. Removing bookmark...")
r = requests.delete(f"{BASE}/recipes/1/bookmark",
    headers={"Authorization": f"Bearer {token}"}
)
print(r.json())
