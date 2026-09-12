from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Create database and table
def create_database():
    connection = sqlite3.connect("salon.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Add status column if the old table does not have it
    try:
        cursor.execute("""
            ALTER TABLE appointments
            ADD COLUMN status TEXT DEFAULT 'Pending'
        """)
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/booking")
def booking():
    selected_service = request.args.get("service", "")
    return render_template(
        "booking.html",
        selected_service=selected_service
    )

@app.route("/book", methods=["POST"])
def book():
    name = request.form["name"]
    phone = request.form["phone"]
    service = request.form["service"]
    date = request.form["date"]
    time = request.form["time"]

    connection = sqlite3.connect("salon.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO appointments
        (name, phone, service, date, time)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, service, date, time))

    connection.commit()
    connection.close()

    return render_template("success.html")


@app.route("/admin")
def admin():
    connection = sqlite3.connect("salon.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    connection.close()

    return render_template("admin.html", appointments=appointments)


# Confirm or cancel appointment
@app.route("/update_status/<int:appointment_id>/<status>")
def update_status(appointment_id, status):

    if status not in ["Confirmed", "Cancelled"]:
        return "Invalid status"

    connection = sqlite3.connect("salon.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE appointments
        SET status = ?
        WHERE id = ?
    """, (status, appointment_id))

    connection.commit()
    connection.close()

    return redirect("/admin")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)