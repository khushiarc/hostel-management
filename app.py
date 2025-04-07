from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For alert messages

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="khushi2506",  # Change to your MySQL password
    database="hostel_db"
)
cursor = mydb.cursor()   #cursor allows you to run SQL commands

# dashboard 
@app.route('/')
def dashboard():
    return render_template('dashboard.html')
  

 

# View All Students
@app.route('/students')
def students():
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    return render_template('students.html', students=students)

# Add Student
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']

    cursor.execute("SELECT id FROM rooms WHERE status = 'vacant' LIMIT 1")
    room = cursor.fetchone()
    if room:
        room_id = room[0]
        cursor.execute("INSERT INTO students (name, age, room_no) VALUES (%s, %s, %s)", (name, age, room_id))
        cursor.execute("UPDATE rooms SET status = 'occupied' WHERE id = %s", (room_id,))
        mydb.commit()
        flash('Student added successfully!', 'success')
    else:
        flash('No vacant rooms available!', 'danger')
    return redirect(url_for('students'))

# Delete Student
@app.route('/delete_student/<int:id>')
def delete_student(id):
    cursor.execute("SELECT room_no FROM students WHERE id = %s", (id,))
    room = cursor.fetchone()
    if room:
        cursor.execute("UPDATE rooms SET status = 'vacant' WHERE id = %s", (room[0],))
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    mydb.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students'))

# Show update form
@app.route('/edit_student/<int:id>')
def edit_student(id):
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()
    return render_template('update_student.html', student=student)

# Update student info
@app.route('/update_student/<int:id>', methods=['POST'])
def update_student(id):
    name = request.form['name']
    age = request.form['age']
    room_no = request.form['room_no']
    cursor.execute("UPDATE students SET name = %s, age = %s, room_no = %s WHERE id = %s", (name, age, room_no, id))
    mydb.commit()
    flash('Student updated successfully!', 'success')
    return redirect(url_for('students'))
  
  

# -------------------- ROOMS ROUTES --------------------
@app.route('/rooms')
def rooms():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM rooms")
    rooms_data = cursor.fetchall()
    cursor.close()
    return render_template('rooms.html', rooms=rooms_data)

@app.route('/add_room', methods=['POST'])
def add_room():
    status = request.form['status']
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO rooms (status) VALUES (%s)", (status,))
    mydb.commit()
    cursor.close()
    flash('Room added successfully!', 'success')
    return redirect(url_for('rooms'))

@app.route('/toggle_room_status/<int:room_id>', methods=['POST'])
def toggle_room_status(room_id):
    cursor = mydb.cursor()
    cursor.execute("SELECT status FROM rooms WHERE id = %s", (room_id,))
    current_status = cursor.fetchone()[0]
    new_status = 'occupied' if current_status == 'vacant' else 'vacant'
    cursor.execute("UPDATE rooms SET status = %s WHERE id = %s", (new_status, room_id))
    mydb.commit()
    cursor.close()
    flash('Room status updated!', 'info')
    return redirect(url_for('rooms'))

@app.route('/delete_room/<int:room_id>')
def delete_room(room_id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
    mydb.commit()
    cursor.close()
    flash('Room deleted successfully!', 'danger')
    return redirect(url_for('rooms'))

# -------------------- HOME --------------------
@app.route('/')
def home():
    return redirect(url_for('rooms'))
  
# === PAYMENTS MODULE ===

@app.route('/payments')
def payments():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()
    cursor.close()
    return render_template('payments.html', payments=payments)

@app.route('/add_payment', methods=['POST'])
def add_payment():
    student_id = request.form['student_id']
    amount = request.form['amount']
    status = request.form['status']
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO payments (student_id, amount, status) VALUES (%s, %s, %s)", (student_id, amount, status))
    mydb.commit()
    cursor.close()
    flash('Payment added successfully!', 'success')
    return redirect('/payments')

@app.route('/delete_payment/<int:id>')
def delete_payment(id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM payments WHERE id = %s", (id,))
    mydb.commit()
    cursor.close()
    flash('Payment deleted.', 'danger')
    return redirect('/payments')

@app.route('/toggle_payment_status/<int:id>', methods=['POST'])
def toggle_payment_status(id):
    cursor = mydb.cursor()
    cursor.execute("SELECT status FROM payments WHERE id = %s", (id,))
    current_status = cursor.fetchone()[0]
    new_status = 'completed' if current_status == 'pending' else 'pending'
    cursor.execute("UPDATE payments SET status = %s WHERE id = %s", (new_status, id))
    mydb.commit()
    cursor.close()
    flash('Payment status updated.', 'info')
    return redirect('/payments')


# === REQUESTS MODULE ===

@app.route('/requests')
def requests_view():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()
    cursor.close()
    return render_template('requests.html', requests=requests)

@app.route('/add_request', methods=['POST'])
def add_request():
    student_id = request.form['student_id']
    status = request.form['status']
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO requests (student_id, status) VALUES (%s, %s)", (student_id, status))
    mydb.commit()
    cursor.close()
    flash('Request added successfully!', 'success')
    return redirect('/requests')

@app.route('/delete_request/<int:id>')
def delete_request(id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM requests WHERE id = %s", (id,))
    mydb.commit()
    cursor.close()
    flash('Request deleted.', 'danger')
    return redirect('/requests')

@app.route('/toggle_request_status/<int:id>', methods=['POST'])
def toggle_request_status(id):
    cursor = mydb.cursor()
    cursor.execute("SELECT status FROM requests WHERE id = %s", (id,))
    current = cursor.fetchone()[0]
    new = 'approved' if current == 'new' else ('rejected' if current == 'approved' else 'new')
    cursor.execute("UPDATE requests SET status = %s WHERE id = %s", (new, id))
    mydb.commit()
    cursor.close()
    flash('Request status updated.', 'info')
    return redirect('/requests')

# === MAINTENANCE MODULE ===

@app.route('/maintenance')
def maintenance_view():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM maintenance")
    maintenance = cursor.fetchall()
    cursor.close()
    return render_template('maintenance.html', maintenance=maintenance)

@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    description = request.form['description']
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO maintenance (description) VALUES (%s)", (description,))
    mydb.commit()
    cursor.close()
    flash('Maintenance request added!', 'success')
    return redirect('/maintenance')

@app.route('/delete_maintenance/<int:id>')
def delete_maintenance(id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM maintenance WHERE id = %s", (id,))
    mydb.commit()
    cursor.close()
    flash('Maintenance request deleted.', 'danger')
    return redirect('/maintenance')

@app.route('/toggle_maintenance_status/<int:id>', methods=['POST'])
def toggle_maintenance_status(id):
    cursor = mydb.cursor()
    cursor.execute("SELECT status FROM maintenance WHERE id = %s", (id,))
    current = cursor.fetchone()[0]
    new = 'resolved' if current == 'pending' else 'pending'
    cursor.execute("UPDATE maintenance SET status = %s WHERE id = %s", (new, id))
    mydb.commit()
    cursor.close()
    flash('Maintenance status updated.', 'info')
    return redirect('/maintenance')


# === CHECKOUTS MODULE ===

@app.route('/checkouts')
def checkouts_view():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM checkouts")
    checkouts = cursor.fetchall()
    cursor.close()
    return render_template('checkouts.html', checkouts=checkouts)

@app.route('/add_checkout', methods=['POST'])
def add_checkout():
    student_id = request.form['student_id']
    date = request.form['date']
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO checkouts (student_id, date) VALUES (%s, %s)", (student_id, date))
    mydb.commit()
    cursor.close()
    flash('Checkout recorded successfully!', 'success')
    return redirect('/checkouts')

@app.route('/delete_checkout/<int:id>')
def delete_checkout(id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM checkouts WHERE id = %s", (id,))
    mydb.commit()
    cursor.close()
    flash('Checkout record deleted.', 'danger')
    return redirect('/checkouts')
  
# Home Page
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

