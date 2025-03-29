from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room
from flask import request, jsonify


app = Flask(__name__)


# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/health_centre'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the server
app.config['SESSION_PERMANENT'] = False

app.secret_key = "Mikisi$100" 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Database
db = SQLAlchemy(app)
socketio = SocketIO(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    doctor_number = db.Column(db.String(10), unique=True, nullable=True)
    patient_number = db.Column(db.String(10), unique=True, nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('Patient', 'Doctor', 'Receptionist'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    patient_number = db.Column(db.String(10), unique=True, nullable=False)


class Doctor(db.Model):
    __tablename__ = 'doctor'

    id = db.Column(db.Integer, primary_key=True)
    doctor_number = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id', ondelete="CASCADE"), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('Scheduled', 'Cancelled', 'Completed', 'Checked-In'), default="Scheduled", nullable=False)
    outcome = db.Column(db.Text, nullable=True)


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id', ondelete="CASCADE"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id', ondelete="CASCADE"), nullable=False)
    prescription_details = db.Column(db.Text, nullable=False)
    outcome = db.Column(db.Text, nullable=True)  # ✅ New column to store treatment results


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Emit new messages in real time
@socketio.on('send_message')
def handle_send_message(data):
    sender_id = current_user.id
    recipient_id = data['recipient_id']
    message_text = data['message']

    # Save message to database
    new_message = Message(sender_id=sender_id, recipient_id=recipient_id, message=message_text)
    db.session.add(new_message)
    db.session.commit()

    # Emit the message to the recipient
    emit('receive_message', {
        'sender': current_user.username,
        'message': message_text
    }, room=str(recipient_id))

@socketio.on('join_chat')
def join_chat():
    join_room(str(current_user.id))




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        # Allow login using patient_number, doctor_number, or username
        user = User.query.filter(
            (User.username == identifier) | 
            (User.doctor_number == identifier) | 
            (User.patient_number == identifier)
        ).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password"

    return render_template('login.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Patient':
        return redirect(url_for('patient_dashboard'))
    elif current_user.role == 'Doctor':
        return redirect(url_for('doctor_dashboard'))
    elif current_user.role == 'Receptionist':
        return redirect(url_for('receptionist_dashboard'))
    return "Unauthorized access"


@app.route('/receptionist_dashboard')
@login_required
def receptionist_dashboard():
    if current_user.role != 'Receptionist':
        return "Access Denied"

    # Get all available doctors
    doctors = Doctor.query.all()

    return render_template('receptionist_dashboard.html', doctors=doctors)



@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'Doctor':
        return "Access Denied"

    # Get doctor details using doctor_number
    doctor = Doctor.query.filter_by(doctor_number=current_user.doctor_number).first()

    if not doctor:
        return "Doctor profile not found."

    # Fetch only this doctor's scheduled or checked-in appointments
    appointments = db.session.query(Appointment, Patient).\
        join(Patient, Appointment.patient_id == Patient.id).\
        filter(Appointment.doctor_id == doctor.id).\
        filter(Appointment.status.in_(["Scheduled", "Checked-In"])).\
        order_by(Appointment.appointment_date).all()

    return render_template('doctor_dashboard.html', appointments=appointments)



# Route to Display the Registration Form & Handle Submission
@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']

        # Generate a unique patient number
        last_patient = Patient.query.order_by(Patient.id.desc()).first()
        patient_number = f"P{1001 if last_patient is None else (int(last_patient.patient_number[1:]) + 1)}"

        new_patient = Patient(
            name=name, dob=dob, address=address, phone=phone, email=email, patient_number=patient_number
        )
        db.session.add(new_patient)
        db.session.commit()

        # Auto-create user account for the patient
        new_user = User(
            username=patient_number,
            password="password123",  # Default password
            role="Patient",
            patient_number=patient_number,
            patient_id=new_patient.id
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('list_patients'))

    return render_template('register_patient.html')

# Route to List All Patients
@app.route('/patients')
def list_patients():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

# Route to Edit a Patient
@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    if current_user.role not in ["Receptionist", "Doctor"]:
        return "Access Denied"

    patient = Patient.query.get_or_404(id)

    if request.method == 'POST':
        patient.name = request.form['name']
        patient.dob = request.form['dob']
        patient.address = request.form['address']
        patient.phone = request.form['phone']
        patient.email = request.form['email']
        
        db.session.commit()
        return redirect(url_for('list_patients'))

    return render_template('edit_patient.html', patient=patient)


@app.route('/delete_patient/<int:id>', methods=['POST'])
@login_required
def delete_patient(id):
    if current_user.role not in ["Receptionist", "Doctor"]:
        return "Access Denied"

    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    
    return redirect(url_for('list_patients'))


@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialty = request.form['specialty']
        email = request.form['email']

        # Generate a unique doctor number
        last_doctor = Doctor.query.order_by(Doctor.id.desc()).first()
        doctor_number = f"D{1001 if last_doctor is None else (int(last_doctor.doctor_number[1:]) + 1)}"

        new_doctor = Doctor(doctor_number=doctor_number, name=name, specialty=specialty, email=email)
        db.session.add(new_doctor)
        db.session.commit()

        # Auto-create user account for the doctor
        new_user = User(
            username=doctor_number,
            password="password123",  # Default password
            role="Doctor",
            doctor_number=doctor_number,
            doctor_id=new_doctor.id
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('list_doctors'))

    return render_template('add_doctor.html')


@app.route('/doctors')
def list_doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)




@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    doctors = Doctor.query.all()

    # If the user is a Receptionist, fetch all patients
    patients = Patient.query.all() if current_user.role == "Receptionist" else None

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        appointment_date = request.form['appointment_date']

        # If the user is a Patient, use their ID
        if current_user.role == "Patient":
            patient_id = current_user.patient_id
        else:
            patient_id = request.form['patient_id']  # Receptionist selects patient

        # Create appointment
        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=datetime.strptime(appointment_date, "%Y-%m-%dT%H:%M"),
            status="Scheduled"
        )

        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment successfully booked!", "success")

        return redirect(url_for('list_appointments'))

    return render_template('book_appointment.html', patients=patients, doctors=doctors)

@app.route('/appointment')
@login_required
def list_appointments():
    if current_user.role == "Patient" and current_user.patient_id:
        # Patients only see their own appointments
        appointments = db.session.query(Appointment, Patient, Doctor).\
            join(Patient, Appointment.patient_id == Patient.id).\
            join(Doctor, Appointment.doctor_id == Doctor.id).\
            filter(Appointment.patient_id == current_user.patient_id).all()

    elif current_user.role == "Doctor" and current_user.doctor_id:
        # Doctors only see their scheduled appointments
        appointments = db.session.query(Appointment, Patient, Doctor).\
            join(Patient, Appointment.patient_id == Patient.id).\
            join(Doctor, Appointment.doctor_id == Doctor.id).\
            filter(Appointment.doctor_id == current_user.doctor_id).all()

    else:
        # Receptionists and other roles see all appointments
        appointments = db.session.query(Appointment, Patient, Doctor).\
            join(Patient, Appointment.patient_id == Patient.id).\
            join(Doctor, Appointment.doctor_id == Doctor.id).all()

    return render_template('appointments.html', appointments=appointments)



@app.route('/cancel_appointment/<int:id>', methods=['POST'])
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = "Cancelled"
    db.session.commit()
    return redirect(url_for('list_appointments'))


@app.route('/check_in', methods=['GET', 'POST'])
@login_required
def check_in():
    message = None

    if request.method == 'POST':
        patient_number = request.form['patient_number']
        patient = Patient.query.filter_by(patient_number=patient_number).first()

        if patient:
            appointment = Appointment.query.filter_by(patient_id=patient.id, status="Scheduled").first()

            if appointment:
                print(f"Before Update: ID={appointment.id}, Status={appointment.status}")
                appointment.status = "Checked-In"
                db.session.commit()
                print(f"After Update: ID={appointment.id}, Status={appointment.status}")
                message = f"Checked in successfully for appointment on {appointment.appointment_date}."
            else:
                message = "No scheduled appointments found for this patient."
        else:
            message = "Patient not found. Please enter a valid patient number."

    # 🔹 Get doctor details
    doctor = Doctor.query.filter_by(doctor_number=current_user.doctor_number).first()

    if current_user.role == "Receptionist":
        # Receptionist sees all scheduled appointments (including doctor details)
        appointments = db.session.query(Appointment, Patient, Doctor).\
            join(Patient, Appointment.patient_id == Patient.id).\
            join(Doctor, Appointment.doctor_id == Doctor.id).\
            filter(Appointment.status == "Scheduled").all()

    elif current_user.role == "Doctor" and doctor:
        # Doctor sees only their own scheduled appointments
        appointments = db.session.query(Appointment, Patient, Doctor).\
            join(Patient, Appointment.patient_id == Patient.id).\
            join(Doctor, Appointment.doctor_id == Doctor.id).\
            filter(Appointment.status == "Scheduled", Appointment.doctor_id == doctor.id).all()

    else:
        appointments = []

    print(f"Appointments Found: {len(appointments)}")  # Debugging

    return render_template('check_in.html', message=message, appointments=appointments)






@app.route('/record_outcome/<int:id>', methods=['GET', 'POST'])
@login_required
def record_outcome(id):
    if current_user.role != 'Doctor':
        return "Access Denied"

    appointment = Appointment.query.get_or_404(id)

    if request.method == 'POST':
        outcome = request.form['outcome']
        prescription = request.form['prescription']

        # Ensure outcome is saved
        appointment.status = "Completed"
        appointment.outcome = outcome.strip() if outcome.strip() else "No outcome provided"

        # Save prescription if provided
        if prescription.strip():
            new_prescription = Prescription(
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                appointment_id=appointment.id,
                prescription_details=prescription.strip()
            )
            db.session.add(new_prescription)

        db.session.commit()
        
        # ✅ FIX: Redirect doctors to `doctor_dashboard` after recording outcome
        return redirect(url_for('doctor_dashboard'))

    return render_template('record_outcome.html', appointment=appointment)




@app.route('/patient_history', methods=['GET','POST'])
@login_required
def patient_history():
    # Ensure only patients and doctors can access this page
    if current_user.role == "Patient":
        patient = Patient.query.filter_by(id=current_user.patient_id).first()
    elif current_user.role == "Doctor":
        patient_id = request.args.get("patient_id")
        patient = Patient.query.filter_by(id=patient_id).first()
    else:
        return "Unauthorized access.", 403

    if not patient:
        return "Patient record not found."

    # Get the patient's appointment history
    appointments = db.session.query(Appointment, Doctor).\
        join(Doctor, Appointment.doctor_id == Doctor.id).\
        filter(Appointment.patient_id == patient.id).all()

    # Get the patient's prescriptions along with their doctors
    prescriptions = db.session.query(Prescription, Doctor).\
        join(Doctor, Prescription.doctor_id == Doctor.id).\
        filter(Prescription.patient_id == patient.id).all()


    # If the logged-in user is a Doctor or Receptionist, show a search form
    if request.method == 'POST':
        patient_number = request.form['patient_number']

        # Find the patient by patient number
        patient = Patient.query.filter_by(patient_number=patient_number).first()

        if patient:
            appointments = db.session.query(Appointment, Doctor).\
                join(Doctor, Appointment.doctor_id == Doctor.id).\
                filter(Appointment.patient_id == patient.id).all()

            prescriptions = db.session.query(Prescription, Doctor).\
                join(Doctor, Prescription.doctor_id == Doctor.id).\
                filter(Prescription.patient_id == patient.id).all()
        else:
            return "Patient not found. Please enter a valid patient number."

    return render_template('patient_history.html', patient=patient, appointments=appointments, prescriptions=prescriptions)


@app.route('/list_prescriptions')
@login_required
def list_prescriptions():
    if current_user.role != 'Receptionist':
        return "Access Denied"

    prescriptions = db.session.query(Prescription, Patient, Doctor).\
        join(Patient, Prescription.patient_id == Patient.id).\
        join(Doctor, Prescription.doctor_id == Doctor.id).all()

    return render_template('prescriptions.html', prescriptions=prescriptions)

@app.route('/list_my_outcomes')
@login_required
def list_my_outcomes():
    if current_user.role != 'Doctor':
        return "Access Denied"

    # Fetch outcomes and prescriptions recorded by the logged-in doctor
    outcomes = db.session.query(Appointment, Patient, Prescription).\
        join(Patient, Appointment.patient_id == Patient.id).\
        outerjoin(Prescription, Appointment.id == Prescription.appointment_id).\
        filter(Appointment.doctor_id == current_user.doctor_id, Appointment.status == "Completed").\
        order_by(Appointment.appointment_date.desc()).all()

    return render_template('doctor_outcomes.html', outcomes=outcomes)



@app.route('/conversation/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def conversation(recipient_id):
    """ Show a single conversation and handle message sending """
    recipient = User.query.get_or_404(recipient_id)

    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            new_message = Message(sender_id=current_user.id, recipient_id=recipient_id, message=message_text)
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('conversation', recipient_id=recipient_id))  # Reload page after sending

    messages = db.session.query(Message).\
        filter(((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
               ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))).\
        order_by(Message.timestamp.asc()).all()

    return render_template('conversation.html', recipient=recipient, messages=messages)


@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """ Handle sending messages via AJAX """
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    message_text = data.get('message')

    if not recipient_id or not message_text:
        print("Error: Missing recipient_id or message_text")  # Debugging output
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

    # Save message to the database
    new_message = Message(sender_id=current_user.id, recipient_id=recipient_id, message=message_text)
    db.session.add(new_message)
    db.session.commit()

    # Emit real-time message update
    socketio.emit('receive_message', {
        'sender': current_user.username,
        'message': message_text,
        'recipient_id': recipient_id
    }, room=str(recipient_id))

    print(f"Message sent: {message_text} to {recipient_id}")  # Debugging output
    return jsonify({'status': 'success', 'message': message_text})


@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != "Patient":
        return "Access Denied"

    # Fetch all appointments for the logged-in patient
    appointments = db.session.query(Appointment, Doctor).\
        join(Doctor, Appointment.doctor_id == Doctor.id).\
        filter(Appointment.patient_id == current_user.id).\
        order_by(Appointment.appointment_date.desc()).all()

    return render_template('patient_dashboard.html', patient=current_user, appointments=appointments)


@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if current password is correct
        if current_user.password != current_password:
            flash("Incorrect current password.", "danger")
            return redirect(url_for('reset_password'))

        # Check if new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for('reset_password'))

        # Update password
        current_user.password = new_password  # Save as plain text
        db.session.commit()
        flash("Password updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('reset_password.html')







@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """ Show past conversations and allow starting new ones """

    # Fetch distinct conversations (unique recipients)
    conversations = db.session.query(User).\
        join(Message, ((Message.sender_id == User.id) | (Message.recipient_id == User.id))).\
        filter((Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)).\
        filter(User.id != current_user.id).distinct().all()  # Exclude self from list

    # Handle starting a new conversation
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        recipient_number = request.form.get('recipient_number')

        # If recipient_id is selected
        if recipient_id:
            return redirect(url_for('conversation', recipient_id=recipient_id))

        # If recipient_number is entered manually
        if recipient_number:
            recipient = User.query.filter_by(phone_number=recipient_number).first()
            if recipient:
                return redirect(url_for('conversation', recipient_id=recipient.id))
            flash("No user found with that number.", "error")

    # Determine possible recipients based on user role
    if current_user.role == "Doctor":
        recipients = User.query.filter(User.role.in_(['Patient', 'Receptionist', 'Doctor']), User.id != current_user.id).all()
    elif current_user.role == "Receptionist":
        recipients = User.query.filter(User.role.in_(['Doctor', 'Patient']), User.id != current_user.id).all()
    elif current_user.role == "Patient":
        assigned_doctor = User.query.filter_by(id=current_user.doctor_id).first()  # Get assigned doctor
        receptionist = User.query.filter_by(role="Receptionist").first()  # Get receptionist
        recipients = [r for r in [assigned_doctor, receptionist] if r]  # Remove None values

    return render_template('chat.html', conversations=conversations, recipients=recipients)


@app.route('/search_recipients')
@login_required
def search_recipients():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify([])

    # Patients can only message Doctors & Receptionists
    if current_user.role == "Patient":
        possible_recipients = User.query.filter(
            (User.role.in_(['Doctor', 'Receptionist'])) &
            (User.username.ilike(f"%{query}%"))
        ).all()

    # Doctors & Receptionists can message anyone except themselves
    else:
        possible_recipients = User.query.filter(
            (User.username.ilike(f"%{query}%")) &
            (User.id != current_user.id)  # Exclude self
        ).all()

    # Convert to JSON-friendly response
    recipients_data = [{"id": user.id, "username": user.username, "role": user.role} for user in possible_recipients]

    return jsonify(recipients_data)




if __name__ == '__main__':
    app.run(debug=True)
