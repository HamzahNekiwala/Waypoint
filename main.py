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

def save_booking(username, flight, hotel):
    """Saves the confirmed booking to users.json (Hamzah's Task)."""
    with open('data/users.json', 'r') as f:
        users = json.load(f)

    # Create the reservation entry
    reservation = {
        "flight_id": flight['id'],
        "hotel_id": hotel['id'],
        "destination": flight['destination'],
        "date": flight['date'],
        "total_price": flight['price'] + hotel['price']
    }

    # Append to user's itinerary
    users[username]['itinerary'].append(reservation)

    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)
    
    print(f"\nSuccessfully booked! Total cost: ${reservation['total_price']}")


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


def dependent_search(data, username):
    """Search and Reservation Logic (Hamzah's Task)."""
    print("--- TRAVEL SEARCH ---")
    dest = input(f"Available: {', '.join(data['destinations'])}\nWhere to? ").capitalize()
    
    if dest not in data['destinations']:
        print("Invalid destination.")
        return

    print("\nHow would you like to start your booking?")
    print("1. Choose Flight First")
    print("2. Choose Hotel First")
    choice = input("Select (1/2): ")

    selected_flight = None
    selected_hotel = None

    if choice == "1":
        # Flight First Flow
        flights = [f for f in data['flights'] if f['destination'] == dest]
        for i, f in enumerate(flights):
            print(f"[{i}] {f['id']}: ${f['price']} on {f['date']}")
        
        f_idx = int(input("Select flight index: "))
        selected_flight = flights[f_idx]
        
        matching_hotels = [h for h in data['hotels'] if h['city'] == dest and selected_flight['date'] in h['available_dates']]
        print(f"\nHotels in {dest} available on {selected_flight['date']}:")
        for i, h in enumerate(matching_hotels):
            print(f"[{i}] {h['name']}: ${h['price']}/night")
        
        h_idx = int(input("Select hotel index: "))
        selected_hotel = matching_hotels[h_idx]

    else:
        # Hotel First Flow
        hotels = [h for h in data['hotels'] if h['city'] == dest]
        for i, h in enumerate(hotels):
            print(f"[{i}] {h['name']} (${h['price']}/night)")
        
        h_idx = int(input("Select hotel index: "))
        selected_hotel = hotels[h_idx]
        
        matching_flights = [f for f in data['flights'] if f['destination'] == dest and f['date'] in selected_hotel['available_dates']]
        print(f"\nFlights to {dest} landing on available hotel dates:")
        for i, f in enumerate(matching_flights):
            print(f"[{i}] Flight {f['id']}: ${f['price']} on {f['date']}")
            
        f_idx = int(input("Select flight index: "))
        selected_flight = matching_flights[f_idx]

    # --- BOOKING SUMMARY (Hamzah's Task) ---
    print("\n--- BOOKING SUMMARY ---")
    print(f"Destination: {dest}")
    print(f"Flight:      {selected_flight['id']} (${selected_flight['price']})")
    print(f"Hotel:       {selected_hotel['name']} (${selected_hotel['price']}/night)")
    print(f"Date:        {selected_flight['date']}")
    print(f"Total Price: ${selected_flight['price'] + selected_hotel['price']}")
    print("-----------------------")

    confirm = input("Confirm booking? (y/n): ").lower()
    if confirm == 'y':
        save_booking(username, selected_flight, selected_hotel)
    else:
        print("Booking discarded.")


def main():
    print("Welcome to Waypoint - Your Central Travel Hub\n")
   
    user = login_system()
    if user:
        catalog_data = load_data()
        dependent_search(catalog_data, user)
        print("\n--- End of Iteration 1 Demo ---")
    else:
        print("Login failed.")


if __name__ == "__main__":
    main()