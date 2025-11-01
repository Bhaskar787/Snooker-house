from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'T#0000@black',
    'database': 'Snooker_House_Dibash'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


# Serve homepage
@app.route('/')
def home():
    return render_template('home.html')


# Serve booking page
@app.route('/booking')
def booking_page():
    return render_template('booking.html')

# Serve events page
@app.route('/events')
def events_page():
    return render_template('events.html')

# Serve contact page
@app.route('/contact')
def contact_page():
    return render_template('contact.html')


# --- Tables CRUD ---

@app.route('/tables', methods=['GET'])
def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tables)

@app.route('/tables', methods=['POST'])
def add_table():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    price_per_hour = data.get('price_per_hour', 0)

    if not name:
        return jsonify({'error': 'Table name is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tables (name, description, price_per_hour) VALUES (%s, %s, %s)",
        (name, description, price_per_hour)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Table added successfully'}), 201

@app.route('/tables/<int:table_id>', methods=['PUT'])
def update_table(table_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    price_per_hour = data.get('price_per_hour', 0)

    if not name:
        return jsonify({'error': 'Table name is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tables SET name=%s, description=%s, price_per_hour=%s WHERE id=%s",
        (name, description, price_per_hour, table_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Table updated successfully'})

@app.route('/tables/<int:table_id>', methods=['DELETE'])
def delete_table(table_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tables WHERE id=%s", (table_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Table deleted successfully'})


# --- Bookings CRUD ---

@app.route('/bookings', methods=['GET'])
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.id, b.customer_name, b.booking_date, b.start_time, b.duration_hours, t.name AS table_name
        FROM bookings b
        JOIN tables t ON b.table_id = t.id
    """)
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(bookings)

@app.route('/bookings', methods=['POST'])
def add_booking():
    data = request.get_json()
    table_id = data.get('table_id')
    customer_name = data.get('customer_name')
    booking_date = data.get('booking_date')
    start_time = data.get('start_time')
    duration_hours = data.get('duration_hours')

    if not (table_id and customer_name and booking_date and start_time and duration_hours):
        return jsonify({'error': 'All booking fields are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (table_id, customer_name, booking_date, start_time, duration_hours)
        VALUES (%s, %s, %s, %s, %s)
    """, (table_id, customer_name, booking_date, start_time, duration_hours))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Booking added successfully'}), 201


# --- Events CRUD ---

@app.route('/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(events)

@app.route('/events', methods=['POST'])
def add_event():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    event_date = data.get('event_date')

    if not (title and event_date):
        return jsonify({'error': 'Event title and date are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, description, event_date) VALUES (%s, %s, %s)",
        (title, description, event_date)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Event added successfully'}), 201


# --- Contact Message API ---

@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'All fields are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Contact message received successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
