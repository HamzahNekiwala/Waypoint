# Waypoint: Your Central Travel Hub

**Waypoint** is a centralized travel planning application designed to turn a "dream trip" into a simple and functional schedule. Developed by team **Cache Me Outside**, this platform allows users to catalogue flights, hotels, and activities in one place rather than searching through fragmented emails and maps.

## Live Demo
* **Web Application:** [https://waypoint-cauu.onrender.com/](https://waypoint-cauu.onrender.com/)
* Note: Web app may take up to 1 minute to start up after inactivity
* **Video Walkthrough:** [YouTube Live Demo](https://www.youtube.com/watch?v=r7pycvvv7OQ)
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

## Tech Stack & Prerequisites

* **Backend:** Python 3.13.3, Flask
* **Frontend:** HTML5, CSS3, Jinja2
* **Database:** JSON-based persistent storage
* **Testing:** Python `unittest` framework, `unittest.mock`
* **Deployment:** Render

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

3. run `app.py` then visit http://127.0.0.1:10000 to access and use Waypoint on your machiene

---

## Project Structure

```text
Waypoint/
├── app.py                 # Flask application & routing logic
├── data/
│   ├── catalog.json       # internal travel database
│   └── users.json         # persistent user itineraries
├── templates/             # Jinja2 HTML templates
└── tests/                 # automated test suite (unit, integration, system)
```

---

## How It Works (Step-by-Step)

Waypoint is designed to be intuitive. Follow these steps to plan your trip:

1.  **Login or Sign Up:** Enter your username and password on the welcome page.
    * Existing travelers should use their registered username and password.
    * New travelers must create an account using the Sign Up tab first. Passwords must be at least 3 characters.
    * Admin access is available through the same login form using `admin` / `admin`.
2.  **Destination Selection:** You will see a list of available countries. Type the name of the country you wish to visit.
3.  **Choose Your Planning Priority:**
    * **Flight First:** Select this if you have specific travel dates. You will pick a flight and your seat, and the app will then show you hotels available for those specific dates.
    * **Hotel First:** Select this if you have a specific resort in mind. You will pick your hotel and room, and the app will then filter for flights that land on your check-in dates.
4.  **Confirm Selection:** The app will present a list of available flights/hotels based on your priority. Select your preferred options by their index.
5.  **View Your "Ticket":** Once selected, the system generates a summary "Ticket" showing your destination, flight ID, hotel ID, and total trip cost.
6.  **Manage Itinerary:** At the end of the session, you can choose to view your **Past Catalog** to see all previously saved trips and itineraries. You may also cancel your trip or export your itenerary to share.

---

## Admin Panel (Step-by-Step)

The admin panel lets you manage the travel catalog and inventory.

1.  **Login as Admin:** Use the standard login form with username `admin` and password `admin`.
2.  **Open the Admin Console:** Click on the admin dashboard option.
3.  **Add a Flight:** Fill in Flight ID, destination, price, date, and available seats. Submit to add the flight to the catalog.
4.  **Add a Hotel:** Fill in Hotel ID, name, city, price, available dates, and room inventory. Submit to add the hotel to the catalog.
5.  **Update Existing Items:** Choose a flight or hotel ID, then adjust price, available seats, available rooms, or available dates.
6.  **Save Catalog Changes:** Each admin form submission updates `catalog.json` immediately.

---

## Testing & Quality Assurance

The project maintains high reliability through an automated testing suite. We achieved a 100% pass rate across 14 tests covering:

* **Unit Tests:** Data I/O validation and username normalization.
* **Integration Tests:** Multi-step route redirection and data persistence.
* **System Tests:** End-to-end user workflows from login to booking confirmation.

To run the tests:

```bash
py -m unittest discover tests
```
