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
