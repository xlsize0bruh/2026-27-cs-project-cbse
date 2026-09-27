import mysql.connector

STAFF_PASSWORD = "springdale2026-27"

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pratyush"
)

cursor = con.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS voicebox")
cursor.execute("USE voicebox")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        issue_id INT AUTO_INCREMENT PRIMARY KEY,
        student_name VARCHAR(100),
        student_class VARCHAR(10),
        title VARCHAR(150) NOT NULL,
        description TEXT NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

con.commit()

# user input func 
def read_text(message, maximum):
    while True:
        text = input(message).strip()

        if text != "" and len(text) <= maximum:
            return text

        print("Enter between 1 and", maximum, "characters.")


def submit_issue():
    print("\n--- Submit an Issue ---")

    anonymous = input("Submit anonymously? (y/n): ").strip().lower()

    while anonymous not in ("y", "n"):
        anonymous = input("Enter y or n: ").strip().lower()

    if anonymous == "y":
        name = None
        student_class = None
        print("Your name and class will not be stored.")
    else:
        name = read_text("Your name: ", 100)
        student_class = read_text("Class and section: ", 10)

    title = read_text("Title: ", 150)
    description = read_text("Describe your issue or suggestion: ", 2000)

    query = """
        INSERT INTO issues
        (student_name, student_class, title, description)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (name, student_class, title, description))
    con.commit()

    print("Submitted successfully!")
    print("Your issue ID is:", cursor.lastrowid)
    print("Use this ID to check progress.")


def track_issue():
    print("\n--- Track Progress ---")

    issue_id = input("Enter issue ID: ").strip()

    if not issue_id.isdigit():
        print("Enter a numeric ID.")
        return

    cursor.execute(
        "SELECT status FROM issues WHERE issue_id = %s",
        (issue_id,)
    )

    row = cursor.fetchone()

    if row is None:
        print("Issue not found.")
    else:
        print("Current status:", row[0])


def view_issues():
    cursor.execute("""
        SELECT issue_id, student_name, student_class,
               title, description, status
        FROM issues
        ORDER BY issue_id DESC
    """)

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No submissions yet.")
        return

    for row in rows:
        print("\n----------------------------")
        print("Issue ID:", row[0])

        if row[1] is None:
            print("Name: Anonymous")
        else:
            print("Name:", row[1])
            print("Class:", row[2])

        print("Title:", row[3])
        print("Description:", row[4])
        print("Status:", row[5])


def update_issue():
    issue_id = input("Enter issue ID: ").strip()

    if not issue_id.isdigit():
        print("Enter a numeric ID.")
        return

    cursor.execute(
        "SELECT status FROM issues WHERE issue_id = %s",
        (issue_id,)
    )

    row = cursor.fetchone()

    if row is None:
        print("Issue not found.")
        return

    print("Current status:", row[0])

    statuses = [
        "Pending",
        "In Progress",
        "Resolved",
        "Closed",
        "Reopened"
    ]

    for i in range(len(statuses)):
        print(i + 1, statuses[i])

    choice = input("Choose new status: ").strip()

    if choice not in ("1", "2", "3", "4", "5"):
        print("Invalid choice.")
        return

    new_status = statuses[int(choice) - 1]

    if new_status == "Closed":
        if row[0] != "Resolved":
            print("The issue must be Resolved before it can be Closed.")
            return

        verified = input("Have you verified the resolution? (y/n): ")

        if verified.strip().lower() != "y":
            print("Issue has not been closed.")
            return

    cursor.execute(
        "UPDATE issues SET status = %s WHERE issue_id = %s",
        (new_status, issue_id)
    )

    con.commit()
    print("Status updated successfully!")


def staff_login():

    password = input("Enter staff password: ")

    if password != STAFF_PASSWORD:
        print("Incorrect password.")
        return

    while True:
        print("\n--- Staff Menu ---")
        print("1. View submissions")
        print("2. Update status")
        print("3. Log out")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_issues()
        elif choice == "2":
            update_issue()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")


while True:
    print("\n--- VoiceBox ---")
    print("1. Submit an issue/ a suggestion")
    print("2. Track progress")
    print("3. Staff login")
    print("4. Exit")

    choice = input("Enter your choice: ").strip()

    try:
        if choice == "1":
            submit_issue()
        elif choice == "2":
            track_issue()
        elif choice == "3":
            staff_login()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

    except mysql.connector.Error as error:
        con.rollback()
        print("Database error:", error)

cursor.close()
con.close()

print("Thank you for using VoiceBox!")