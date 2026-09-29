# 🌍 Tourist Destination Recommendation & Management System

A data-driven CLI application designed for discovering, filtering, and managing global travel destinations. Built with **Python 3** and backed by a relational **MySQL** database, the system implements role-based access control (RBAC), multi-criteria search filtering, administrative approval workflows, and report exports to CSV and PDF.

---

## ✨ Features

### 👤 User Module
* **Interactive Terminal UI:** Powered by `InquirerPy` for intuitive arrow-key navigation and masked credential entry.
* **Authentication:** User registration and login secured with client-side **SHA-256** password hashing.
* **Multi-Criteria Search:** Filter destinations dynamically across:
  * Continents & Countries (hierarchical dependent dropdowns)
  * Climate & Best Season to Visit
  * Maximum Average Budget thresholds
  * Specific Attraction Types (Historical, Beach, Adventure, Nature, Modern)
* **Custom To-Visit List:** Bookmark destinations into a personal travel bucket list with full CRUD support.
* **Community Submissions:** Normal users can propose new destinations (sent to an approval queue).

### 🛠️ Admin Module
* **Destination Approval Workflow:** Review pending user-submitted destinations with granular Approve/Reject controls before public listing.
* **Master Data Management:** Add new continents, countries, and auto-approved destinations.
* **Administrative Deletions:** Safe removal of destination records with foreign key cascade handling.

### 📄 Export & Reporting
* Export filtered destination queries directly to **CSV** or formatted **PDF** documents (via `fpdf`).
* Clean tabular console displays using `PrettyTable`.

---

## 🗄️ Database Architecture

The system uses a normalized relational schema (`tourism_db`) with enforced foreign keys:
* **`users`**: User identities, roles (`admin` / `user`), and SHA-256 hashed credentials.
* **`continents` & `countries`**: Geographic hierarchy enforcing cascading constraints.
* **`destinations`**: Comprehensive travel data including climates, season timelines, average budgets, and approval status (`approved` flag).
* **`attractions`**: One-to-many relationship linking specific points of interest to destinations.
* **`to_visit`**: Relational junction table linking user bookmarks to destinations.

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python 3.8+**
* **MySQL Server** running locally

### 2. Database Setup
Log into your MySQL terminal and run the schema setup script:
`mysql -u root -p < tourism_db.sql`

### 3. Database Configuration
In main.py, verify your MySQL credentials in connect_db():
`cfg = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "tourism_db",
}`

### 4. Run the application
`python main.py`

## 🔑 Default Credentials (Seed Data)

| Role  | Username | Default Password    |
| ----- | -------- | ------------------- |
| Admin | admin    | admin               |
| User  | alice    | aliceinwonderland   |
| User  | bob      | bobbybob            |


### SQL tables: 
<img width="958" height="967" alt="1" src="https://github.com/user-attachments/assets/7ff091a9-7232-4ee6-8c0a-1b36ad323105" />

### Admin login: 
<img width="1407" height="514" alt="2" src="https://github.com/user-attachments/assets/223ee33e-5c17-4efc-bd74-9a039e85d7a2" />

### Approving destinations: 
<img width="1398" height="232" alt="3" src="https://github.com/user-attachments/assets/8ef7817d-8594-4d8a-afb9-69119b531bea" />

### Registering as a new user: 
<img width="506" height="488" alt="4" src="https://github.com/user-attachments/assets/58c21d64-f8b9-4e0e-8d16-cab23e1f9610" />

### Logging in as a normal user: 
<img width="447" height="352" alt="5" src="https://github.com/user-attachments/assets/15aa9531-79ef-4c47-aa9e-a824a3048ee7" />

### Viewing all destinations:  
<img width="858" height="920" alt="6" src="https://github.com/user-attachments/assets/5f810b41-1299-47dc-b989-166d7cd70068" />

### Searching for a destination: 
<img width="1110" height="517" alt="7" src="https://github.com/user-attachments/assets/43e81113-9648-4c47-a172-e4ffb28f4bae" />

### Exporting the results to a PDF/CSV:  
<img width="968" height="234" alt="8" src="https://github.com/user-attachments/assets/5986934d-c923-451e-ab10-ea69d490c154" />

### Managing To-Visit list: 
<img width="1147" height="836" alt="9" src="https://github.com/user-attachments/assets/3587de5c-3f2d-479a-aca0-8bad88768f27" />

### Adding a destination to the To-Visit list: 
<img width="1144" height="420" alt="10" src="https://github.com/user-attachments/assets/94f289b9-929c-4532-b97e-e39f51d73301" />

### Viewing destination details:  
<img width="580" height="376" alt="11" src="https://github.com/user-attachments/assets/793e0329-99b8-4de5-8fd4-8490da08dc2a" />

### Approving destinations added by user as admin:  
<img width="1346" height="416" alt="12" src="https://github.com/user-attachments/assets/5eb5f2f8-853c-4e32-b4f2-88982c68edb5" />

### Verifying the added destination:  
<img width="914" height="421" alt="13" src="https://github.com/user-attachments/assets/3ff85be9-8ffa-46fc-9e05-c21d9ec42cd7" />
