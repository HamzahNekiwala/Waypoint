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

def login_system():
    """Persistent Auth: Loads/Saves users to a JSON file."""
    if not os.path.exists('data/users.json'):
        with open('data/users.json', 'w') as f:
            json.dump({}, f)

    with open('data/users.json', 'r') as f:
        users = json.load(f)

    print("--- WAYPOINT LOGIN ---")
    username = input("Enter username: ").lower().strip()
    
    if username in users:
        print(f"Welcome back, {username}!")
    else:
        print(f"New user detected. Creating profile for {username}...")
        users[username] = {"itinerary": []}
        with open('data/users.json', 'w') as f:
            json.dump(users, f, indent=4)
            
    return username

# def search_skeleton(data):
#     """Basic Search Logic (Salahuddin's Task)."""
#     print("--- TRAVEL SEARCH ---")
#     query = input("Enter destination (e.g., London, Tokyo): ").capitalize()
    
#     # Filter flights by destination
#     flights = [f for f in data['flights'] if f['destination'] == query]
#     # Filter hotels by city
#     hotels = [h for h in data['hotels'] if h['city'] == query]

#     print(f"\nResults for {query}:")
#     print(f"Flights found: {len(flights)}")
#     for f in flights:
#         print(f" - Flight {f['id']}: ${f['price']} on {f['date']}")
        
#     print(f"Hotels found: {len(hotels)}")
#     for h in hotels:
#         print(f" - {h['name']}: ${h['price']}/night")
def dependent_search(data):
    print("--- TRAVEL SEARCH ---")
    dest = input(f"Available: {', '.join(data['destinations'])}\nWhere to? ").capitalize()
    
    print("\nHow would you like to start your booking?")
    print("1. Choose Flight First")
    print("2. Choose Hotel First")
    choice = input("Select (1/2): ")

    if choice == "1":
        # Flight First Flow
        flights = [f for f in data['flights'] if f['destination'] == dest]
        for i, f in enumerate(flights):
            print(f"[{i}] {f['id']}: ${f['price']} on {f['date']}")
        
        f_idx = int(input("Select flight index: "))
        selected_date = flights[f_idx]['date']
        
        print(f"\nHotels in {dest} available on {selected_date}:")
        matching_hotels = [h for h in data['hotels'] if h['city'] == dest and selected_date in h['available_dates']]
        for h in matching_hotels:
            print(f" - {h['name']}: ${h['price']}/night")

    else:
        # Hotel First Flow
        hotels = [h for h in data['hotels'] if h['city'] == dest]
        for i, h in enumerate(hotels):
            print(f"[{i}] {h['name']} (${h['price']}/night)")
        
        h_idx = int(input("Select hotel index: "))
        available_days = hotels[h_idx]['available_dates']
        
        print(f"\nFlights to {dest} landing on available hotel dates ({', '.join(available_days)}):")
        matching_flights = [f for f in data['flights'] if f['destination'] == dest and f['date'] in available_days]
        for f in matching_flights:
            print(f" - Flight {f['id']}: ${f['price']} on {f['date']}")

def main():
    print("Welcome to Waypoint - Your Central Travel Hub\n")
    
    user = login_system()
    if user:
        catalog_data = load_data()
        dependent_search(catalog_data)
        print("\n--- End of Iteration 1 Demo ---")
    else:
        print("Login failed.")

if __name__ == "__main__":
    main()