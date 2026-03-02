import json
import os

def load_data():
    """Loads the internal travel catalog (Ayan's Task)."""
    try:
        # Assumes catalog is in a folder named 'data'
        with open('data/catalog.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: catalog.json not found in /data folder.")
        return {"flights": [], "hotels": []}

def login_skeleton():
    """Basic Auth System Skeleton (Gibran's Task)."""
    print("--- WAYPOINT LOGIN ---")
    username = input("Enter username: ")
    # Simple check for demo purposes
    if username:
        print(f"Successfully logged in as: {username}\n")
        return username
    return None

def search_skeleton(data):
    """Basic Search Logic (Salahuddin's Task)."""
    print("--- TRAVEL SEARCH ---")
    query = input("Enter destination (e.g., London, Tokyo): ").capitalize()
    
    # Filter flights by destination
    flights = [f for f in data['flights'] if f['destination'] == query]
    # Filter hotels by city
    hotels = [h for h in data['hotels'] if h['city'] == query]

    print(f"\nResults for {query}:")
    print(f"Flights found: {len(flights)}")
    for f in flights:
        print(f" - Flight {f['id']}: ${f['price']} on {f['date']}")
        
    print(f"Hotels found: {len(hotels)}")
    for h in hotels:
        print(f" - {h['name']}: ${h['price_per_night']}/night")

def main():
    print("Welcome to Waypoint - Your Central Travel Hub\n")
    
    user = login_skeleton()
    if user:
        catalog_data = load_data()
        search_skeleton(catalog_data)
        print("\n--- End of Iteration 1 Demo ---")
    else:
        print("Login failed.")

if __name__ == "__main__":
    main()