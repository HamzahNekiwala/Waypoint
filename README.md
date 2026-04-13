# Waypoint: Your Central Travel Hub

**Waypoint** is a centralized travel planning application designed to turn a "dream trip" into a simple and functional schedule. Developed by team **Cache Me Outside**, this platform allows users to catalogue flights, hotels, and activities in one place rather than searching through fragmented emails and maps.

---

## The Team: Cache Me Outside

| Member | Role | Specific Task for Travel Planning Domain |
| :--- | :--- | :--- |
| **Gibran Alam** | Project Manager | Primary contact for stakeholders and lead on user authentication. |
| **Ayan Malik** | Technical Manager | Lead architectural designer of the internal data catalog and JSON structures. |
| **Salahuddin Patel** | Front-End Lead | Responsible for UI/UX design and search/discovery visual patterns. |
| **Hamzah Nekiwala** | Back-End Lead | Manager of core application logic, booking engine, and file I/O operations. |
| **Zaid Patel** | Quality Lead | Lead on competitor audits and testing edge cases like conflicting booking dates. |

---

## Key Features (MVP)

* **Persistent Authentication:** Users log in with a username to save their specific itinerary to a persistent JSON file.
* **Dependent Search Logic:** A smart search system where flight choices automatically filter available hotel dates (and vice-versa) to ensure itinerary alignment.
* **Internal Data Catalog:** A curated internal JSON database ensures 100% uptime and a predictable testing environment.
* **Itinerary Management:** A centralized view that summarizes all booked items in one list.

---

## Getting Started

### Prerequisites
* **Python 3.3**
* **Standard Libraries:** `json`, `os`, `csv`.

### Installation & Directory Setup
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/HamzahNekiwala/Waypoint.git](https://github.com/HamzahNekiwala/Waypoint.git)
    cd Waypoint
    ```
2.  **Verify Data Folders:** Ensure your root directory contains a `data/` folder with `catalog.json` and `users.json`.

---

## How It Works (Step-by-Step)

Waypoint is designed to be intuitive. Follow these steps to plan your trip:

1.  **Login:** Enter your unique username. If you are a new traveler, the system will automatically initialize a new profile for you.
2.  **Destination Selection:** You will see a list of available countries. Type the name of the country you wish to visit.
3.  **Choose Your Planning Priority:**
    * **Flight First:** Select this if you have specific travel dates. You will pick a flight, and the app will then show you hotels available for those specific dates.
    * **Hotel First:** Select this if you have a specific resort in mind. You will pick your hotel, and the app will then filter for flights that land on your check-in dates.
4.  **Confirm Selection:** The app will present a list of available flights/hotels based on your priority. Select your preferred options by their index.
5.  **View Your "Ticket":** Once selected, the system generates a summary "Ticket" showing your destination, flight ID, hotel ID, and total trip cost.
6.  **Manage Itinerary:** At the end of the session, you can choose to view your **Past Catalog** to see all previously saved trips and itineraries.

## Live Demo Of Waypoint ([https://waypoint-cauu.onrender.com/](url))

