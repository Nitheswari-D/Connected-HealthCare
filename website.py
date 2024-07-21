from flask import Flask, render_template, request, redirect,session,url_for
import mysql.connector

app = Flask(__name__,static_url_path='/static')
app.secret_key='your_secret_key_here'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Nithu@2003",
    database="hospital"
)

@app.route('/')
def front():
    return render_template('front.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/patientform')
def patient_form():
    return render_template('patientform.html')

@app.route('/doctorform')
def doctor_form():
    return render_template('doctorform.html')

@app.route('/login')
def login():
    return render_template('log.html')

@app.route('/patpage')
def patpage():
    return render_template('patpage.html')

@app.route('/department')
def department():
    return render_template('department.html')

@app.route('/patientappointment')
def patientappointment():
    patient_name = session['username']
    cursor = db.cursor()
    cursor.execute("SELECT * FROM appointment WHERE patient_name = %s", (patient_name,))
    appointments = cursor.fetchall()
    sortedappointments=sorted(appointments,key=lambda x:x[2])
    return render_template('patientappointment.html', appointments=sortedappointments)

@app.route('/docpage')
def docpage():
    doctor_name = session['username']
    cursor = db.cursor()
    cursor.execute("SELECT * FROM appointment WHERE doctor_name = %s", (doctor_name,))
    appointments = cursor.fetchall()

    # Separate approved and pending appointments
    approved_appointments = [appointment for appointment in appointments if appointment[6] == 'approved']
    pending_appointments = [appointment for appointment in appointments if appointment[6] == 'pending']

    # Sort each list by date
    sorted_approved_appointments = sorted(approved_appointments, key=lambda x: x[2])
    sorted_pending_appointments = sorted(pending_appointments, key=lambda x: x[2])

    # Combine the lists with approved appointments first
    sorted_appointments = sorted_approved_appointments + sorted_pending_appointments

    # Count the pending appointments
    cursor.execute("SELECT COUNT(*) FROM appointment WHERE doctor_name = %s AND status = 'pending'", (doctor_name,))
    pending_count = cursor.fetchone()[0]

    return render_template('docpage.html', appointments=sorted_appointments, pending_count=pending_count)


@app.route('/appoint')
def appointment():
    cursor = db.cursor()
    cursor.execute("select name from doctors")
    doctor_names = [row[0] for row in cursor.fetchall()]
    return render_template('appointment.html',doctor_names=doctor_names)

@app.route('/signuppat', methods=['GET', 'POST'])
def signuppat():
    if request.method == 'POST':
        name= request.form['name']
        age= request.form['age']
        gender= request.form['gender']
        email= request.form['mail']
        phone= request.form['no']
        password = request.form['pass']
        confirm_password = request.form['confirm_pass']
        if password == confirm_password:
            cursor = db.cursor()
            insert_query="INSERT INTO patients (name, age, gender, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)" 
            cursor.execute(insert_query,(name,age,gender,email,phone,password))
            db.commit()
            return redirect('/')
        else:
            return "Passwords do not match"
    return render_template('front.html')

@app.route('/signupdoc', methods=['GET', 'POST'])
def signupdoc():
    if request.method == 'POST':
        name= request.form['name']
        age= request.form['age']
        gender= request.form['gender']
        exp=request.form['exp']
        designation= request.form['designation']
        specialization= request.form['specialization']
        email= request.form['mail']
        phone= request.form['no']
        password = request.form['pass']
        confirm_password = request.form['confirm_pass']
        if password == confirm_password:
            cursor = db.cursor()
            cursor.execute("INSERT INTO doctors(name, age, gender, experience, designation, specialization, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, age, gender, exp, designation, specialization, email, phone, password))

            db.commit()
            return redirect('/')
        else:
            return "Passwords do not match"
    return render_template('doctorform.html')

@app.route('/loginform', methods=['POST'])
def loginform():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form.get('userType')
    cursor=db.cursor()
    if user_type == 'doctor':
        cursor.execute("SELECT * FROM doctors WHERE name = %s AND password = %s", (username, password))
    else:
        cursor.execute("SELECT * FROM patients WHERE name = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        session['user_id']=user[0]
        session['username']=username
        session['user_type'] = user_type
        return redirect('/patpage')
    else:
        return "Invalid username or password"

@app.route('/conditional_appointments')
def conditional_appointments():
    if 'user_type' in session:
        if session['user_type'] == 'doctor':
            return redirect(url_for('docpage'))
        elif session['user_type'] == 'patient':
            return redirect(url_for('patientappointment'))
    return "Unauthorized access", 401

@app.route('/app', methods=['POST'])
def appl():
    pname=request.form['patient-name']
    dname = request.form['doctor-name']
    date= request.form['appointment-date']
    time = request.form['appointment-time']
    notes = request.form['patient-notes']
    cursor = db.cursor()
    cursor.execute("INSERT INTO appointment (doctor_name, date, time, notes,patient_name) VALUES (%s, %s, %s, %s, %s)",
                        (dname, date, time, notes,pname))
    db.commit()
    cursor.close()
    session['success_message'] = "Appointment booked successfully and emails sent."
    return redirect('/patpage')

@app.route('/approve/<int:appointment_id>', methods=['POST', 'GET'])
def approve_appointment(appointment_id):
    cursor = db.cursor()
    cursor.execute("UPDATE appointment SET status = 'approved' WHERE appointment_id = %s", (appointment_id,))
    db.commit()
    cursor.close()
        
if __name__ == '__main__':
    app.run(debug=True)
