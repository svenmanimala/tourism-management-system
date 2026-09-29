import sys
import os
import csv
import hashlib
from datetime import datetime
from getpass import getpass

import mysql.connector
from mysql.connector import errors as mysql_errors
from InquirerPy import inquirer
from prettytable import PrettyTable

# PDF export
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except Exception:
    FPDF_AVAILABLE = False

# -----------------------
# Database connection
# -----------------------
def connect_db():
    cfg = {
        "host": "localhost",
        "user": "root",         # change if needed
        "password": "root",     # change to your MySQL password
        "database": "tourism_db",
    }
    try:
        return mysql.connector.connect(**cfg)
    except mysql_errors.NotSupportedError:
        # Retry with mysql_native_password
        try:
            cfg["auth_plugin"] = "mysql_native_password"
            return mysql.connector.connect(**cfg)
        except Exception as e:
            print("Database connection retry failed:", e)
            raise
    except Exception as e:
        print("Database connection error:", e)
        raise

# -----------------------
# Utilities
# -----------------------
def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def print_table(headers, rows):
    table = PrettyTable(headers)
    for r in rows:
        table.add_row(r)
    print(table)

# Wrapper around InquirerPy select with optional "Back"
def choose_from_list(message, choices, include_back=False, default=None):
    """
    Show an arrow-driven list and return the selected string.
    If include_back=True, a 'Back' choice is appended and returned as 'Back' when chosen.
    """
    choices_list = list(choices)
    if include_back:
        choices_list.append("Back")
    return inquirer.select(message=message, choices=choices_list, default=default).execute()

# Text and secret input via InquirerPy (keeps consistent terminal UI)
def typed_input(message, default=""):
    return inquirer.text(message=message, default=default).execute()

def typed_secret(message):
    # fallback to using getpass if InquirerPy secret isn't desirable in some environments
    try:
        return inquirer.secret(message=message).execute()
    except Exception:
        return getpass(message + ": ")

# Prefilled selection that allows typing manually or skipping
def choose_or_type_prefilled(message, prefilled, allow_skip=True):
    """
    Presents choices: optionally 'Skip', then prefilled items, then 'Type manually', then 'Back'
    Returns:
      - "" when skipped
      - string from prefilled
      - typed string if chosen 'Type manually'
      - "Back" if user chose back (when used with include_back)
    """
    choices = []
    if allow_skip:
        choices.append("Skip")
    choices += prefilled
    choices.append("Type manually")
    # We do not include Back here by default; calling code can wrap choose_from_list if needed
    sel = choose_from_list(message, choices, include_back=True)
    if sel == "Skip":
        return ""
    if sel == "Type manually":
        return typed_input(f"{message} (type manually)")
    if sel == "Back":
        return "Back"
    return sel

# -----------------------
# Authentication
# -----------------------
def register_user():
    db = connect_db(); cur = db.cursor()
    print("\n--- Register ---")
    username = typed_input("Choose a username:")
    if not username:
        print("Username required.")
        cur.close(); db.close(); return
    # masked password
    pwd = typed_secret("Choose a password")
    if not pwd:
        print("Password required.")
        cur.close(); db.close(); return
    hashed = sha256_hex(pwd)
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed, 'user'))
        db.commit()
        print("Registered successfully; please login.")
    except mysql.connector.IntegrityError:
        print("Username already exists.")
    finally:
        cur.close(); db.close()

def login_user():
    db = connect_db(); cur = db.cursor()
    print("\n--- Login ---")
    username = typed_input("Username:")
    pwd = typed_secret("Password")
    hashed = sha256_hex(pwd)
    cur.execute("SELECT user_id, role FROM users WHERE username=%s AND password=%s", (username, hashed))
    row = cur.fetchone()
    cur.close(); db.close()
    if row:
        user_id, role = row
        print(f"Logged in as {username} ({role})")
        return {"user_id": user_id, "username": username, "role": role}
    print("Invalid credentials.")
    return None

# -----------------------
# Admin features
# -----------------------

def admin_view_all_destinations():
    db = connect_db()
    cur = db.cursor()

    cur.execute("""
        SELECT d.dest_id, d.name, c.name, co.name, d.approved
        FROM destinations d
        JOIN countries c ON d.country_id = c.country_id
        JOIN continents co ON c.continent_id = co.continent_id
        ORDER BY d.dest_id
    """)
    rows = cur.fetchall()

    if rows:
        print_table(
            ["ID", "Destination", "Country", "Continent", "Status"],
            [
                (r[0], r[1], r[2], r[3], "Approved" if r[4] == 1 else "Pending")
                for r in rows
            ]
        )
    else:
        print("No destinations found.")

    cur.close()
    db.close()

def admin_add_continent():
    db = connect_db(); cur = db.cursor()
    name = typed_input("Continent name:")
    if not name:
        print("Name required.")
        cur.close(); db.close(); return
    try:
        cur.execute("INSERT INTO continents (name) VALUES (%s)", (name,))
        db.commit()
        print("Continent added.")
    except mysql.connector.IntegrityError:
        print("Continent already exists.")
    finally:
        cur.close(); db.close()

def admin_add_country():
    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT continent_id, name FROM continents ORDER BY name")
    conts = cur.fetchall()
    if not conts:
        print("No continents. Add a continent first.")
        cur.close(); db.close(); return
    choices = [f"{cid}: {cname}" for cid, cname in conts]
    sel = choose_from_list("Select continent for the new country:", choices, include_back=True)
    if sel == "Back":
        cur.close(); db.close(); return
    continent_id = int(sel.split(":")[0])
    country_name = typed_input("Country name:")
    if not country_name:
        print("Country name required.")
        cur.close(); db.close(); return
    try:
        cur.execute("INSERT INTO countries (continent_id, name) VALUES (%s,%s)", (continent_id, country_name))
        db.commit()
        print("Country added.")
    except mysql.connector.IntegrityError:
        print("Country already exists or invalid continent.")
    finally:
        cur.close(); db.close()

def admin_add_destination(admin_user_id):
    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT country_id, name FROM countries ORDER BY name")
    countries = cur.fetchall()
    if not countries:
        print("No countries exist. Add countries first.")
        cur.close(); db.close(); return
    choices = [f"{cid}: {cname}" for cid, cname in countries]
    sel = choose_from_list("Select country for the new destination:", choices, include_back=True)
    if sel == "Back":
        cur.close(); db.close(); return
    country_id = int(sel.split(":")[0])
    name = typed_input("Destination name:")
    best_time = typed_input("Best time (e.g., Apr-Oct):")
    climate = typed_input("Climate:")
    budget_text = typed_input("Average budget (numeric):")
    try:
        budget = int(budget_text)
    except ValueError:
        print("Budget must be a number.")
        cur.close(); db.close(); return
    desc = typed_input("Short description:")
    try:
        cur.execute("""INSERT INTO destinations
                       (country_id, name, best_time, climate, avg_budget, description, approved, created_by, approved_by, approved_at)
                       VALUES (%s,%s,%s,%s,%s,%s,1,%s,%s,NOW())""",
                    (country_id, name, best_time, climate, budget, desc, admin_user_id, admin_user_id))
        db.commit()
        print("Destination added and auto-approved.")
    except Exception as e:
        print("Error adding destination:", e)
    finally:
        cur.close(); db.close()

def admin_view_pending():
    db = connect_db(); cur = db.cursor()
    cur.execute("""SELECT d.dest_id, d.name, c.name AS country, co.name AS continent,
                   d.best_time, d.climate, d.avg_budget, u.username, d.created_at
                   FROM destinations d
                   JOIN countries c ON d.country_id = c.country_id
                   JOIN continents co ON c.continent_id = co.continent_id
                   LEFT JOIN users u ON d.created_by = u.user_id
                   WHERE d.approved = 0
                   ORDER BY d.created_at""")
    rows = cur.fetchall()
    if rows:
        headers = ["ID","Destination","Country","Continent","Best Time","Climate","Budget","Created By","Created At"]
        print_table(headers, rows)
    else:
        print("No pending destinations.")
    cur.close(); db.close()
    return rows

def admin_approve_reject(admin_user_id):
    rows = admin_view_pending()
    if not rows:
        return
    choices = [f"{r[0]}: {r[1]} ({r[2]}, {r[3]})" for r in rows]
    sel = choose_from_list("Select a pending destination to act on:", choices, include_back=True)
    if sel == "Back":
        return
    dest_id = int(sel.split(":")[0])
    action = choose_from_list("Choose action:", ["Approve","Reject","Cancel"], include_back=False)
    db = connect_db(); cur = db.cursor()
    if action == "Approve":
        cur.execute("UPDATE destinations SET approved=1, approved_by=%s, approved_at=NOW() WHERE dest_id=%s", (admin_user_id, dest_id))
        db.commit()
        print("Destination approved.")
    elif action == "Reject":
        cur.execute("DELETE FROM destinations WHERE dest_id=%s AND approved=0", (dest_id,))
        db.commit()
        print("Destination rejected and removed.")
    else:
        print("Action cancelled.")
    cur.close(); db.close()

def admin_delete_destination():
    db = connect_db()
    cur = db.cursor()

    dest_id_text = typed_input("Enter destination ID to delete:")
    try:
        dest_id = int(dest_id_text)
    except ValueError:
        print("Invalid destination ID.")
        cur.close(); db.close()
        return

    # Fetch destination details
    cur.execute("""
        SELECT d.name, c.name, co.name, d.approved
        FROM destinations d
        JOIN countries c ON d.country_id = c.country_id
        JOIN continents co ON c.continent_id = co.continent_id
        WHERE d.dest_id = %s
    """, (dest_id,))
    row = cur.fetchone()

    if not row:
        print("Destination not found.")
        cur.close(); db.close()
        return

    name, country, continent, approved = row

    # Preview
    print("\n--- Destination Found ---")
    print(f"ID        : {dest_id}")
    print(f"Name      : {name}")
    print(f"Country   : {country}")
    print(f"Continent : {continent}")
    print(f"Status    : {'Approved' if approved == 1 else 'Pending'}")

    confirm = choose_from_list(
        "Are you sure you want to permanently delete this destination?",
        ["Delete", "Cancel"],
        include_back=False
    )

    if confirm != "Delete":
        print("Deletion cancelled.")
        cur.close(); db.close()
        return

    # Delete destination
    try:
        cur.execute("DELETE FROM destinations WHERE dest_id = %s", (dest_id,))
        db.commit()
        print("Destination deleted successfully.")
    except Exception as e:
        print("Failed to delete destination:", e)
    finally:
        cur.close()
        db.close()


# -----------------------
# Prefill fetch helpers
# -----------------------
def fetch_continents():
    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT name FROM continents ORDER BY name")
    rows = [r[0] for r in cur.fetchall()]
    cur.close(); db.close()
    return rows

def fetch_countries(continent_name=None):
    db = connect_db(); cur = db.cursor()
    if continent_name:
        cur.execute("""SELECT c.name FROM countries c
                       JOIN continents co ON c.continent_id = co.continent_id
                       WHERE co.name = %s ORDER BY c.name""", (continent_name,))
    else:
        cur.execute("SELECT name FROM countries ORDER BY name")
    rows = [r[0] for r in cur.fetchall()]
    cur.close(); db.close()
    return rows

def fetch_attraction_types():
    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT DISTINCT attraction_type FROM attractions")
    rows = [r[0] for r in cur.fetchall()]
    cur.close(); db.close()
    return rows

# -----------------------
# Search & details
# -----------------------
def search_destinations_interactive():
    # continent
    continents = fetch_continents()
    cont_choice = choose_or_type_prefilled("Filter by continent:", continents, allow_skip=True)
    if cont_choice == "Back":
        return
    # country (dependent if continent chosen)
    countries = fetch_countries(cont_choice if cont_choice else None)
    country_choice = choose_or_type_prefilled("Filter by country:", countries, allow_skip=True)
    if country_choice == "Back":
        return

    # best_time and climate quick choices or type
    best_time_choice = choose_from_list("Best time filter:", ["Skip","Jan-Feb","Mar-May","Jun-Aug","Sep-Nov","Type manually","Back"], include_back=False)
    if best_time_choice == "Back":
        return
    if best_time_choice == "Type manually":
        best_time = typed_input("Enter best time (e.g., Apr-Oct):")
    elif best_time_choice == "Skip":
        best_time = ""
    else:
        best_time = best_time_choice

    climate_choice = choose_from_list("Climate filter:", ["Skip","Tropical","Temperate","Cold","Desert","Type manually","Back"], include_back=False)
    if climate_choice == "Back":
        return
    if climate_choice == "Type manually":
        climate = typed_input("Enter climate:")
    elif climate_choice == "Skip":
        climate = ""
    else:
        climate = climate_choice

    # attractions
    attractions = fetch_attraction_types()
    attraction_choice = choose_or_type_prefilled("Attraction type filter:", attractions, allow_skip=True)
    if attraction_choice == "Back":
        return

    # budget quick choices or manual
    budget_q = choose_from_list("Budget quick filter:", ["Skip","Under 1000","1000-2000","2000-5000","5000+","Type manually","Back"], include_back=False)
    if budget_q == "Back":
        return
    max_budget = None
    if budget_q == "Under 1000":
        max_budget = 999
    elif budget_q == "1000-2000":
        max_budget = 2000
    elif budget_q == "2000-5000":
        max_budget = 5000
    elif budget_q == "5000+":
        max_budget = 99999999
    elif budget_q == "Type manually":
        b = typed_input("Enter max budget (numeric):")
        try:
            max_budget = int(b)
        except ValueError:
            print("Invalid budget entered; ignoring budget filter.")
            max_budget = None
    # build query
    base = """SELECT d.dest_id, d.name, c.name, co.name, d.best_time, d.climate, d.avg_budget
              FROM destinations d
              JOIN countries c ON d.country_id = c.country_id
              JOIN continents co ON c.continent_id = co.continent_id"""
    joins = ""
    where = " WHERE d.approved = 1"
    params = []
    if attraction_choice:
        joins += " JOIN attractions a ON d.dest_id = a.dest_id"
        where += " AND a.attraction_type LIKE %s"; params.append("%" + attraction_choice + "%")
    if cont_choice:
        where += " AND co.name LIKE %s"; params.append("%" + cont_choice + "%")
    if country_choice:
        where += " AND c.name LIKE %s"; params.append("%" + country_choice + "%")
    if best_time:
        where += " AND d.best_time LIKE %s"; params.append("%" + best_time + "%")
    if climate:
        where += " AND d.climate LIKE %s"; params.append("%" + climate + "%")
    if max_budget is not None:
        where += " AND d.avg_budget <= %s"; params.append(max_budget)

    query = base + joins + where + " ORDER BY d.avg_budget ASC"

    db = connect_db(); cur = db.cursor()
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close(); db.close()

    if not rows:
        print("No destinations found for given filters.")
        return

    headers = ["ID","Destination","Country","Continent","Best Time","Climate","Budget"]
    print_table(headers, rows)

    # Post-results actions (Back included)
    result_ids = [str(r[0]) for r in rows]
    actions = ["Back", "Export results (CSV/PDF)"] + result_ids
    sel = choose_from_list("Action - select an ID to view or choose export/back:", actions, include_back=False)
    if sel == "Back":
        return
    if sel == "Export results (CSV/PDF)":
        export_rows = [tuple(r) for r in rows]
        export_results_interactive(headers, export_rows)
        return
    # view details
    try:
        did = int(sel)
        show_destination_details(did)
    except ValueError:
        print("Invalid selection.")

def show_destination_details(dest_id):
    db = connect_db(); cur = db.cursor()
    cur.execute("""SELECT d.name, c.name, co.name, d.best_time, d.climate, d.avg_budget, d.description, d.approved, u.username, d.created_at, d.approved_at
                   FROM destinations d
                   JOIN countries c ON d.country_id = c.country_id
                   JOIN continents co ON c.continent_id = co.continent_id
                   LEFT JOIN users u ON d.created_by = u.user_id
                   WHERE d.dest_id = %s""", (dest_id,))
    row = cur.fetchone()
    cur.close(); db.close()
    if not row:
        print("Destination not found.")
        return
    name, country, continent, best_time, climate, budget, desc, approved, created_by, created_at, approved_at = row
    print("\n--- Destination Details ---")
    print(f"Name: {name}")
    print(f"Country: {country}")
    print(f"Continent: {continent}")
    print(f"Best time: {best_time}")
    print(f"Climate: {climate}")
    print(f"Average budget: {budget}")
    print(f"Approved: {'Yes' if approved == 1 else 'No (Pending)'}")
    print(f"Created by: {created_by}")
    print(f"Created at: {created_at}")
    print(f"Approved at: {approved_at}")
    print(f"\nDescription: {desc}\n")
    # attractions
    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT attraction_type, details FROM attractions WHERE dest_id = %s", (dest_id,))
    atts = cur.fetchall()
    cur.close(); db.close()
    if atts:
        print("Attractions:")
        for a_type, details in atts:
            print(f" - {a_type}: {details}")
    else:
        print("No attractions recorded.")

# -----------------------
# To-Visit list (arrow-driven selections include Back)
# -----------------------
def select_approved_destination(message="Select destination:"):
    db = connect_db(); cur = db.cursor()
    cur.execute("""SELECT d.dest_id, d.name, c.name, co.name FROM destinations d
                   JOIN countries c ON d.country_id = c.country_id
                   JOIN continents co ON c.continent_id = co.continent_id
                   WHERE d.approved = 1
                   ORDER BY co.name, c.name, d.name""")
    rows = cur.fetchall()
    cur.close(); db.close()
    if not rows:
        print("No approved destinations available.")
        return None
    choices = [f"{r[0]}: {r[1]} ({r[2]}, {r[3]})" for r in rows]
    sel = choose_from_list(message, choices, include_back=True)
    if sel == "Back":
        return None
    return int(sel.split(":")[0])

def save_to_visit(user_id):
    dest_id = select_approved_destination("Select destination to add to your To-Visit list:")
    if not dest_id:
        return
    db = connect_db(); cur = db.cursor()
    try:
        cur.execute("INSERT INTO to_visit (user_id, dest_id) VALUES (%s,%s)", (user_id, dest_id))
        db.commit()
        print("Saved to your To-Visit list.")
    except mysql.connector.IntegrityError:
        print("Destination already in your To-Visit list.")
    finally:
        cur.close(); db.close()

def view_to_visit(user_id):
    db = connect_db(); cur = db.cursor()
    cur.execute("""SELECT t.list_id, d.dest_id, d.name, c.name, co.name, t.added_at
                   FROM to_visit t
                   JOIN destinations d ON t.dest_id = d.dest_id
                   JOIN countries c ON d.country_id = c.country_id
                   JOIN continents co ON c.continent_id = co.continent_id
                   WHERE t.user_id = %s
                   ORDER BY co.name, c.name, d.name""", (user_id,))
    rows = cur.fetchall()
    cur.close(); db.close()
    if not rows:
        print("Your To-Visit list is empty.")
        return []
    headers = ["ListID","DestID","Destination","Country","Continent","Added At"]
    print_table(headers, rows)
    return rows

def remove_from_to_visit(user_id):
    rows = view_to_visit(user_id)
    if not rows:
        return
    choices = [f"{r[0]}: {r[2]} ({r[3]}, {r[4]})" for r in rows]
    sel = choose_from_list("Select entry to remove:", choices, include_back=True)
    if sel == "Back":
        return
    list_id = int(sel.split(":")[0])
    db = connect_db(); cur = db.cursor()
    cur.execute("DELETE FROM to_visit WHERE list_id = %s", (list_id,))
    db.commit()
    cur.close(); db.close()
    print("Removed from your To-Visit list.")

# -----------------------
# Export (destinations only)
# -----------------------
def export_results_interactive(headers, rows):
    fmt = choose_from_list("Choose export format:", ["CSV","PDF","Cancel"], include_back=True)
    if fmt == "Back" or fmt == "Cancel":
        print("Export cancelled.")
        return
    filename = typed_input("Filename (no extension):")
    if not filename:
        print("Invalid filename.")
        return
    if fmt == "CSV":
        try:
            with open(filename + ".csv", "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in rows:
                    writer.writerow(r)
            print(f"CSV exported: {os.path.abspath(filename + '.csv')}")
        except Exception as e:
            print("CSV export failed:", e)
    elif fmt == "PDF":
        if not FPDF_AVAILABLE:
            print("FPDF not installed; install via pip install fpdf")
            return
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            # header row
            col_width = max(20, (pdf.w - 2 * pdf.l_margin) / max(1, len(headers)))
            for h in headers:
                pdf.cell(col_width, 8, str(h)[:30], border=1)
            pdf.ln()
            for row in rows:
                for col in row:
                    pdf.cell(col_width, 6, str(col)[:30], border=1)
                pdf.ln()
            pdf.output(filename + ".pdf")
            print(f"PDF exported: {os.path.abspath(filename + '.pdf')}")
        except Exception as e:
            print("PDF export failed:", e)

# -----------------------
# Add destination (user)
# -----------------------
def add_destination_user(user_id):
    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT continent_id, name FROM continents ORDER BY name")
    conts = cur.fetchall()
    cur.close(); db.close()
    if not conts:
        print("No continents. Ask admin to add.")
        return
    cont_choices = [f"{cid}: {cname}" for cid, cname in conts]
    cont_sel = choose_from_list("Select continent:", cont_choices, include_back=True)
    if cont_sel == "Back":
        return
    cont_id = int(cont_sel.split(":")[0])

    db = connect_db(); cur = db.cursor()
    cur.execute("SELECT country_id, name FROM countries WHERE continent_id = %s ORDER BY name", (cont_id,))
    countries = cur.fetchall()
    cur.close(); db.close()
    if not countries:
        print("No countries in the selected continent. Ask admin to add.")
        return
    country_choices = [f"{cid}: {cname}" for cid, cname in countries]
    country_sel = choose_from_list("Select country:", country_choices, include_back=True)
    if country_sel == "Back":
        return
    country_id = int(country_sel.split(":")[0])

    name = typed_input("Destination name:")
    best_time = typed_input("Best time (e.g., Apr-Oct):")
    climate = typed_input("Climate:")
    budget_text = typed_input("Average budget (numeric):")
    try:
        budget = int(budget_text)
    except ValueError:
        print("Budget must be numeric.")
        return
    desc = typed_input("Short description:")
    db = connect_db(); cur = db.cursor()
    try:
        cur.execute("""INSERT INTO destinations (country_id, name, best_time, climate, avg_budget, description, approved, created_by)
                       VALUES (%s,%s,%s,%s,%s,%s,0,%s)""",
                    (country_id, name, best_time, climate, budget, desc, user_id))
        db.commit()
        print("Destination submitted; pending admin approval.")
    except Exception as e:
        print("Error inserting destination:", e)
    finally:
        cur.close(); db.close()

# -----------------------
# Main application
# -----------------------
def main():
    print("Tourist Destination Recommendation System")
    while True:
        main_choice = choose_from_list("Main Menu:", ["Login","Register","Exit"], include_back=False)
        if main_choice == "Register":
            register_user()
            continue
        if main_choice == "Login":
            user = login_user()
            if not user:
                continue
            uid = user["user_id"]
            role = user["role"]
            # Notify admin of pending upon login
            if role == "admin":
                pending = admin_view_pending()
                if pending:
                    print(f"There are {len(pending)} pending destinations awaiting approval.")
            # Post-login menus (arrow-driven)
            if role == "admin":
                while True:
                    admin_choice = choose_from_list("Admin Menu:",
                                                    ["Add Continent",
                                                     "Add Country",
                                                     "Add Destination",
                                                     "View all destinations",
                                                     "View pending destinations",
                                                     "Approve/Reject destinations",
                                                     "Delete destination (by ID)",
                                                     "Logout"],
                                                    include_back=True)
                    if admin_choice == "Back":
                        break
                    if admin_choice == "Add Continent":
                        admin_add_continent()
                    elif admin_choice == "View all destinations":
                        admin_view_all_destinations()
                    elif admin_choice == "Add Country":
                        admin_add_country()
                    elif admin_choice == "Add Destination(auto-approved)":
                        admin_add_destination(uid)
                    elif admin_choice == "View pending destinations":
                        admin_view_pending()
                    elif admin_choice == "Approve/Reject destinations":
                        admin_approve_reject(uid)
                    elif admin_choice == "Delete destination (by ID)":
                        admin_delete_destination()

                    elif admin_choice == "Logout":
                        break
            else:
                while True:
                    user_choice = choose_from_list("User Menu:",
                                                   ["View all destinations","Search destinations",
                                                    "View destination details (type ID)","Add new destination (pending approval)",
                                                    "Manage To-Visit list","Logout"],
                                                   include_back=True)
                    if user_choice == "Back":
                        break
                    if user_choice == "View all destinations":
                        db = connect_db(); cur = db.cursor()
                        cur.execute("""SELECT co.name, c.name, d.dest_id, d.name, d.best_time, d.climate, d.avg_budget
                                       FROM destinations d
                                       JOIN countries c ON d.country_id = c.country_id
                                       JOIN continents co ON c.continent_id = co.continent_id
                                       WHERE d.approved=1 ORDER BY d.dest_id, co.name, c.name, d.name""")
                        rows = cur.fetchall()
                        cur.close(); db.close()
                        headers = ["Continent","Country","ID","Destination","Best Time","Climate","Budget"]
                        print_table(headers, rows)
                    elif user_choice == "Search destinations":
                        search_destinations_interactive()
                    elif user_choice == "View destination details (type ID)":
                        did_text = typed_input("Enter destination ID to view:")
                        try:
                            did = int(did_text)
                            show_destination_details(did)
                        except ValueError:
                            print("Invalid ID.")
                    elif user_choice == "Add new destination (pending approval)":
                        add_destination_user(uid)
                    elif user_choice == "Manage To-Visit list":
                        tv_choice = choose_from_list("To-Visit Menu:", ["View list","Add destination","Remove destination","Back"], include_back=False)
                        if tv_choice == "View list":
                            view_to_visit(uid)
                        elif tv_choice == "Add destination":
                            save_to_visit(uid)
                        elif tv_choice == "Remove destination":
                            remove_from_to_visit(uid)
                        elif tv_choice == "Back":
                            pass
                    elif user_choice == "Logout":
                        break
        elif main_choice == "Exit":
            print("Goodbye.")
            sys.exit(0)

if __name__ == "__main__":
    main()
