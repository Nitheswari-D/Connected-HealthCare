from flask import Flask, render_template, request, redirect,session,url_for,jsonify
import os
import json
import base64
import mysql.connector
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email.mime.text
import email.mime.multipart
import logging
# from datetime import datetime
# from zoomus import ZoomOAuth
# import requests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

app = Flask(__name__,static_url_path='/static')
app.secret_key='your_secret_key_here'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Nithu@2003",
    database="hospital"
)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'monikhasrikanth@gmail.com'
app.config['MAIL_PASSWORD'] = 'MonikhaS@28'
app.config['MAIL_DEFAULT_SENDER'] = 'monikhasrikanth@gmail.com'

# Zoom OAuth credentials
# ZOOM_CLIENT_ID = '2q4IGYe1T0uh_9ah7hKDZA'
# ZOOM_CLIENT_SECRET = 'HoTmEyP8TDtPJRv2avJXPr4Ksb4qgRjs'
# ZOOM_REDIRECT_URI = 'http://localhost:5000/zoom/callback'

# zoom_oauth = ZoomOAuth(client_id='2q4IGYe1T0uh_9ah7hKDZA', client_secret='HoTmEyP8TDtPJRv2avJXPr4Ksb4qgRjs')


#authorization for google api mail sending
def authorize():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    logging.debug(f'Authorization URL: {authorization_url}')
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    session['credentials'] = creds.to_json()
    logging.debug('Credentials stored in session.')

    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    logging.debug('Credentials stored in token.json file.')
    return redirect(url_for('index'))

def get_credentials():
    logging.debug("Retrieving credentials")
    if 'credentials' in session:
        logging.debug('Credentials found in session.')
        creds_dict = json.loads(session['credentials'])
        return Credentials.from_authorized_user_info(creds_dict, SCOPES)
    elif os.path.exists('token.json'):
        logging.debug('Credentials found in token.json file.')
        with open('token.json', 'r') as token:
            creds_dict = json.load(token)
            return Credentials.from_authorized_user_info(creds_dict, SCOPES)
    logging.debug('No credentials found.')
    return None

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
            return "registered successfully"
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
    cursor = db.cursor()
    cursor.execute("SELECT email FROM patients WHERE name = %s", (pname,))
    patient_email = cursor.fetchone()[0]

    cursor.execute("SELECT email FROM doctors WHERE name = %s", (dname,))
    doctor_email = cursor.fetchone()[0]

    patient_msg = f'Your appointment with Dr. {dname} has been confirmed for {date} at {time}.'
    doctor_msg = f'You have a new appointment with patient {pname} on {date} at {time}.'
    logging.debug(patient_msg)
    logging.debug(doctor_msg)

    credentials = get_credentials()
    if not credentials:
        return authorize()
    
    send_patemail(patient_email, 'Appointment Confirmation', dname,date,time)
    send_docemail(doctor_email, 'New Appointment Notification', pname,date,time)

    cursor.close()
    
    session['success_message'] = "Appointment booked successfully and emails sent."
    return redirect('/patpage')

@app.route('/approve/<int:appointment_id>', methods=['POST', 'GET'])
def approve_appointment(appointment_id):
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            # Update the appointment status to 'approved' for the given appointment_id
            cursor.execute("UPDATE appointment SET status = 'approved' WHERE appointment_id = %s", (appointment_id,))
            db.commit()

            # Retrieve necessary details from the appointment for email notification
            cursor.execute("SELECT patient_name, date, time, doctor_name FROM appointment WHERE appointment_id = %s", (appointment_id,))
            appointment = cursor.fetchone()
            if appointment:
                pname = appointment[0]  # Assuming index 0 is patient_name
                date = appointment[1]   # Assuming index 1 is date
                time = appointment[2]   # Assuming index 2 is time
                dname = appointment[3]  # Assuming index 3 is doctor_name

                # Fetch patient's email based on their name
                cursor.execute("SELECT email FROM patients WHERE name = %s", (pname,))
                patient_email = cursor.fetchone()[0]

                # Close cursor after use
                cursor.close()

                # Send email if credentials are available
                credentials = get_credentials()
                if credentials:
                    send_patemail(patient_email, 'Appointment Approved', dname, date, time)
                    return '', 200  # Return success status
                else:
                    return authorize()  # Reauthorize if credentials are not available
            else:
                cursor.close()
                return "Appointment not found", 404

        except Exception as e:
            cursor.close()
            return f"Error approving appointment: {str(e)}", 500

    else:
        return "Method not allowed", 405

def send_patemail(to, subject, dname, date, time):
    credentials = get_credentials()
    if credentials:
        logging.debug('Credentials successfully retrieved.')
        service = build('gmail', 'v1', credentials=credentials)

        # Create the email content with HTML
        html_content = f"""
        <html>
        <body>
            <h2 style="text-align: center;">Appointment Confirmation</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border:0;">
                    <th style="padding: 8px; text-align: left;">Doctor Name</th>
                    <td style="padding: 8px; text-align: left;">{dname}</td>
                </tr>
                <tr style="border:0;">
                    <th style="padding: 8px; text-align: left;">Date</th>
                    <td style="padding: 8px; text-align: left;">{date}</td>
                </tr>
                <tr style="border:0;">
                    <th style="padding: 8px; text-align: left;">Time</th>
                    <td style="padding: 8px; text-align: left;">{time}</td>
                </tr>
            </table>
            <footer style="text-align: center; margin-top: 20px;">
                <p>&copy; 2024 Pinnacle Hospial. All rights reserved.</p>
                <p>Contact us: info@pinnacle.com | +1 (123) 456-7890</p>
            </footer>
        </body>
        </html>
        """

        # Create the email message
        message = email.mime.multipart.MIMEMultipart()
        message['to'] = to
        message['from'] = 'monikhasrikanth@gmail.com'
        message['subject'] = subject
        msg = email.mime.text.MIMEText(html_content, 'html')
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        try:
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            logging.debug(f'Email sent to {to}')
        except HttpError as error:
            logging.error(f'An error occurred while sending email: {error}')

def send_docemail(to, subject, pname, date, time):
    credentials = get_credentials()
    if credentials:
        logging.debug('Credentials successfully retrieved.')
        service = build('gmail', 'v1', credentials=credentials)

        # Create the email content with HTML
        html_content = f"""
        <html>
        <body>
            <h2 style="text-align: center;">Appointment Confirmation</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border:0;">
                    <th style="padding: 8px; text-align: left;">Patient Name</th>
                    <td style="padding: 8px; text-align: left;">{pname}</td>
                </tr>
                <tr style="border:0;">
                    <th style="padding: 8px; text-align: left;">Date</th>
                    <td style="padding: 8px; text-align: left;">{date}</td>
                </tr>
                <tr style="border:0;">
                    <th style="padding: 8px; text-align: left;">Time</th>
                    <td style="padding: 8px; text-align: left;">{time}</td>
                </tr>
            </table>
            <footer style="text-align: center; margin-top: 20px;">
                <p>&copy; 2024 Pinnacle Hospial. All rights reserved.</p>
                <p>Contact us: info@pinnacle.com | +1 (123) 456-7890</p>
            </footer>
        </body>
        </html>
        """

        # Create the email message
        message = email.mime.multipart.MIMEMultipart()
        message['to'] = to
        message['from'] = 'monikhasrikanth@gmail.com'
        message['subject'] = subject
        msg = email.mime.text.MIMEText(html_content, 'html')
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        try:
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            logging.debug(f'Email sent to {to}')
        except HttpError as error:
            logging.error(f'An error occurred while sending email: {error}')


# @app.route('/create_zoom_meeting', methods=['POST'])
# def create_zoom_meeting():
#     appointment_id = request.form['appointment_id']
#     cursor = db.cursor()
#     cursor.execute("SELECT patient_name, doctor_name, date, time FROM appointment WHERE appointment_id = %s", (appointment_id,))
#     appointment = cursor.fetchone()
    
#     if appointment:
#         pname, dname, date, time = appointment
#         meeting_time = f"{date}T{time}:00Z"

#         meeting_details = {
#             'topic': f'Appointment with {dname}',
#             'type': 2,
#             'start_time': meeting_time,
#             'duration': 30,
#             'timezone': 'UTC',
#             'agenda': 'Telehealth Consultation'
#         }
#         response = zoom_client.meeting.create(user_id='me', **meeting_details)
#         meeting_data = response.json()

#         cursor.execute("UPDATE appointment SET zoom_meeting_id = %s, zoom_join_url = %s WHERE appointment_id = %s",
#                        (meeting_data['id'], meeting_data['join_url'], appointment_id))
#         db.commit()
#         cursor.close()

#         return jsonify({'join_url': meeting_data['join_url']})
#     else:
#         return "Appointment not found", 404

# @app.route('/join_zoom_meeting/<int:appointment_id>')
# def join_zoom_meeting(appointment_id):
#     cursor = db.cursor()
#     cursor.execute("SELECT zoom_join_url FROM appointment WHERE appointment_id = %s", (appointment_id,))
#     zoom_join_url = cursor.fetchone()[0]
#     cursor.close()
    
#     if zoom_join_url:
#         return redirect(zoom_join_url)
#     else:
#         return "Meeting not found", 404
    

if __name__ == '__main__':
    app.run(debug=True)
