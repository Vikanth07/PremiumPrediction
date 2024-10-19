import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
from bson.binary import Binary
from datetime import datetime, timedelta
import base64
import joblib
import numpy as np
import re
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Insurance"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    user_health_card_number = session.get('health_card_number')
    user_data = mongo.db.userDetails.find_one({"health_card_number": user_health_card_number})

    # Retrieve medical records for the user
    medical_records = mongo.db.medicalRecords.find({"health_card_number": user_health_card_number})

    if user_data:
        if 'user_photo' in user_data:
            user_data['user_photo'] = base64.b64encode(user_data['user_photo']).decode('utf-8')

        # Convert medical records to a list and format date and time
        medical_records_list = []
        for record in medical_records:
            # Format the date and time
            if 'date' in record and 'time' in record:
                formatted_date = datetime.strptime(record['date'], '%Y-%m-%d').strftime('%d-%m-%Y')
                formatted_time = record['time']  # Keep the time as it is (e.g., "12pm")
                record['formatted_date'] = formatted_date
                record['formatted_time'] = formatted_time
            medical_records_list.append(record)

        return render_template('home.html', user=user_data, medical_records=medical_records_list)

    return redirect(url_for('login'))  # Redirect to login if no user found


@app.route('/check_premium_eligibility')
def check_premium_eligibility():
    user_health_card_number = session.get('health_card_number')
    user_data = mongo.db.userDetails.find_one({"health_card_number": user_health_card_number})
    
    if user_data:
        registration_date_str = user_data.get('registration_date', None)
        if registration_date_str:
            registration_date = datetime.strptime(registration_date_str, "%d-%m-%Y")
            today_date = datetime.now()
            
            # Calculate the difference in months
            months_diff = (today_date.year - registration_date.year) * 12 + today_date.month - registration_date.month

            if months_diff > 3:
                # Fetch medical records for the user
                medical_records = mongo.db.medicalRecords.find({"health_card_number": user_health_card_number})

                # Define fields needed for the prediction
                required_fields = [
                    'Diabetes', 'BloodPressureProblems', 'AnyTransplants',
                    'AnyChronicDiseases', 'KnownAllergies', 'HistoryOfCancerInFamily',
                    'NumberOfMajorSurgeries'
                ]
                
                # Initialize a dictionary with default values as 0
                medical_data = {field: 0 for field in required_fields}
                
                # Update dictionary with actual values from medical records if they exist
                for record in medical_records:
                    for field in required_fields:
                        if field in record:
                            medical_data[field] = record.get(field, 0)
                            print(f'{field}-{record.get(field, 0)}')
                
                # Extract user details for prediction
                age = int(re.sub(r'\D', '', user_data.get('age', '0')))
                height = int(re.sub(r'\D', '', user_data.get('height', '0')))
                weight = int(re.sub(r'\D', '', user_data.get('weight', '0')))
                
                # Add user details to the medical data dictionary
                medical_data['Age'] = age
                medical_data['Height'] = height
                medical_data['Weight'] = weight
                
                # Convert data into a suitable format for prediction
                input_data = pd.DataFrame([medical_data])
                
                # Load the trained RandomForest model
                model = joblib.load('premium_model.pkl')
                
                # Predict the premium
                predicted_premium = model.predict(input_data)[0]
                
                return jsonify({
                    "is_eligible": True,
                    "predicted_premium": predicted_premium
                })
    
    return jsonify({"is_eligible": False})



@app.route('/login', methods=['POST'])
def login():
    health_card_number = request.form.get('healthCardNumber')
    password = request.form.get('password')  # Ensure this line is present

    # Check if health card number exists in the MongoDB collection
    user_data = mongo.db.userDetails.find_one({"health_card_number": health_card_number})

    if user_data:
        # Hash the provided password and compare with stored password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if user_data.get('password') == hashed_password:
            session['health_card_number'] = health_card_number  # Store health card number in session
            return jsonify({"status": "success"}), 200  # Return success status for client-side handling
        else:
            return jsonify({"status": "error", "message": "Invalid password"}), 400  # Return error status
    
    return jsonify({"status": "error", "message": "Health Card Number not found"}), 400  # Return error status



@app.route('/register', methods=['POST'])
def register():
    return redirect(url_for('show_register_form'))

@app.route('/show_register_form')
def show_register_form():
    return render_template('register.html')

@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    user_photo = request.files.get('userPhoto')
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    aadhaar_number = request.form.get('aadhaarNumber')
    password = request.form.get('password')

    if not (name and age and gender and dob and aadhaar_number and user_photo and password):
        flash("Please fill in all required fields.")
        return redirect(url_for('show_register_form'))

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    photo_data = Binary(user_photo.read())
    health_card_number = generate_health_card_number(name, aadhaar_number)
    today_date = datetime.now().strftime("%d-%m-%Y")

    mongo.db.userDetails.insert_one({
        "health_card_number": health_card_number,
        "registration_date": today_date,
        "name": name,
        "age": age,
        "gender": gender,
        "dob": dob,
        "aadhaar_number": aadhaar_number,
        "user_photo": photo_data,
        "password": hashed_password,  # Store the hashed password
    })

    return redirect(url_for('health_card', health_card_number=health_card_number))


@app.route('/health_card/<health_card_number>')
def health_card(health_card_number):
    user_data = mongo.db.userDetails.find_one({"health_card_number": health_card_number})
    if user_data:
        if 'user_photo' in user_data:
            user_data['user_photo'] = base64.b64encode(user_data['user_photo']).decode('utf-8')
        return render_template('health_card.html', user=user_data)
    return "User not found", 404

def generate_health_card_number(name, aadhaar_number):
    combined_string = f"{name}{aadhaar_number}".encode('utf-8')
    hash_object = hashlib.sha256(combined_string)
    hash_int = int(hash_object.hexdigest(), 16)
    health_card_number = str(hash_int)[:14].rjust(14, '0')
    return health_card_number

if __name__ == '__main__':
    app.run(debug=True)
