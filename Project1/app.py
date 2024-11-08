from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, login_manager
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from flask_migrate import Migrate  
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import xml.etree.ElementTree as ET
import os
import matplotlib.pyplot as plt
import seaborn as sns


with open('patients_json.json') as file:
    json_data = json.load(file)

csv_data = pd.read_csv('patients.csv')
csv_data_json = csv_data.to_dict(orient='records')  

tree = ET.parse('patients.xml')
root = tree.getroot()
xml_data = []
for patient in root.findall('Patient'):
    patient_dict = {}
    for child in patient:
        patient_dict[child.tag] = child.text
    xml_data.append(patient_dict)


excel_data = pd.read_excel('patients.xlsx')
excel_data_json = excel_data.to_dict(orient='records')  

html_data = pd.read_html('patients.html')[0]  
html_data_json = html_data.to_dict(orient='records')  

# Combine all the data into one list
combined_data = json_data + csv_data_json + xml_data + excel_data_json + html_data_json

# Write the combined data to a new JSON file
with open('patients.json', 'w') as outfile:
    json.dump(combined_data, outfile, indent=4)


df = pd.DataFrame(combined_data)

df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce')
weight_mean = df['weight_kg'].mean()

# Use the mean for missing values
df['weight_kg'].fillna(weight_mean, inplace=True)

# Remove duplicate rows
df.drop_duplicates(inplace=True)

# Calculate BMI if not present
df['bmi'] = df.apply(lambda row: row['weight_kg'] / (row['height_cm'] / 100) ** 2 if pd.isnull(row['bmi']) else row['bmi'], axis=1)

# Normalize data
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df['age'] = (df['age'] - df['age'].min()) / (df['age'].max() - df['age'].min())
df['heart_rate_bpm'] = pd.to_numeric(df['heart_rate_bpm'], errors='coerce')
df['heart_rate_bpm'] = (df['heart_rate_bpm'] - df['heart_rate_bpm'].min()) / (df['heart_rate_bpm'].max() - df['heart_rate_bpm'].min())


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # For CSRF protection and session management
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)  # Session expiration time

# Initialize the database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin' or 'user'

# Define the PatientData model (same as your original model)
class PatientData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    location = db.Column(db.String(50))
    date_recorded = db.Column(db.String(50))
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Integer)
    bmi = db.Column(db.Float)
    heart_rate_bpm = db.Column(db.Integer)
    bp_systolic = db.Column(db.Integer)
    bp_diastolic = db.Column(db.Integer)
    steps_count = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    sleep_duration_hours = db.Column(db.Float)
    sleep_quality = db.Column(db.Integer)
    mood = db.Column(db.String(20))
    stress_level = db.Column(db.Integer)
    water_intake_liters = db.Column(db.Float)

@app.route('/')
def home():
    return render_template('home.html')

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration Form with Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=150)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = StringField('Role (admin/user)', validators=[DataRequired()])

# Login Form with Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data.lower())
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Redirect based on role (Admin or User)
    if current_user.role == 'admin':
        patients = PatientData.query.all() 
        return render_template('admin_dashboard.html',patients=patients)  # Admin dashboard
    else:
        data = PatientData.query.filter_by(user_id=current_user.id).all()
        return render_template('user_dashboard.html')  # User dashboard


# Admin route to append and delete data
@app.route('/admin/append', methods=['GET', 'POST'])
@login_required
def append_data():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
       
        new_patient = PatientData(
            user_id=current_user.id, 
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            age=request.form['age'],
            gender=request.form['gender'],
            location=request.form['location'],
            date_recorded=request.form['date_recorded'],
            weight_kg=request.form['weight_kg'],
            height_cm=request.form['height_cm'],
            bmi=request.form['bmi'],
            heart_rate_bpm=request.form['heart_rate_bpm'],
            bp_systolic=request.form['bp_systolic'],
            bp_diastolic=request.form['bp_diastolic'],
            steps_count=request.form['steps_count'],
            calories_burned=request.form['calories_burned'],
            sleep_duration_hours=request.form['sleep_duration_hours'],
            sleep_quality=request.form['sleep_quality'],
            mood=request.form['mood'],
            stress_level=request.form['stress_level'],
            water_intake_liters=request.form['water_intake_liters']
        )

        try:
            db.session.add(new_patient)
            db.session.commit()
            flash('New patient data added successfully!', 'success')
            return redirect(url_for('dashboard'))  
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding patient data: {str(e)}', 'danger')
            return redirect(url_for('append_data'))  

    return render_template('append_data.html') 

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_data(id):
    
    patient_data = PatientData.query.filter_by(id=id, user_id=current_user.id).first()
    if not patient_data:
        flash('You do not have permission to edit this data.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
    
        patient_data.first_name = request.form['first_name']
        patient_data.last_name = request.form['last_name']
        patient_data.age = request.form['age']
        patient_data.gender = request.form['gender']
        patient_data.location = request.form['location']
        patient_data.date_recorded = request.form['date_recorded']
        patient_data.weight_kg = request.form['weight_kg']
        patient_data.height_cm = request.form['height_cm']
        patient_data.bmi = request.form['bmi']
        patient_data.heart_rate_bpm = request.form['heart_rate_bpm']
        patient_data.bp_systolic = request.form['bp_systolic']
        patient_data.bp_diastolic = request.form['bp_diastolic']
        patient_data.steps_count = request.form['steps_count']
        patient_data.calories_burned = request.form['calories_burned']
        patient_data.sleep_duration_hours = request.form['sleep_duration_hours']
        patient_data.sleep_quality = request.form['sleep_quality']
        patient_data.mood = request.form['mood']
        patient_data.stress_level = request.form['stress_level']
        patient_data.water_intake_liters = request.form['water_intake_liters']

        db.session.commit()
        flash('Data updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_user_data.html', data=patient_data)

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_data(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Fetch the patient data by ID
    patient_data = PatientData.query.get(id)
    if not patient_data:
        flash('Patient data not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if isinstance(patient_data.date_recorded, str):
        patient_data.date_recorded = datetime.strptime(patient_data.date_recorded, '%Y-%m-%d')

    if request.method == 'POST':
        # Update the patient_data fields with form data
        patient_data.first_name = request.form['first_name']
        patient_data.last_name = request.form['last_name']
        patient_data.age = request.form['age']
        patient_data.gender = request.form['gender']
        patient_data.location = request.form['location']
        patient_data.date_recorded = request.form['date_recorded']
        patient_data.weight_kg = request.form['weight_kg']
        patient_data.height_cm = request.form['height_cm']
        patient_data.bmi = request.form['bmi']
        patient_data.heart_rate_bpm = request.form['heart_rate_bpm']
        patient_data.bp_systolic = request.form['bp_systolic']
        patient_data.bp_diastolic = request.form['bp_diastolic']
        patient_data.steps_count = request.form['steps_count']
        patient_data.calories_burned = request.form['calories_burned']
        patient_data.sleep_duration_hours = request.form['sleep_duration_hours']
        patient_data.sleep_quality = request.form['sleep_quality']
        patient_data.mood = request.form['mood']
        patient_data.stress_level = request.form['stress_level']
        patient_data.water_intake_liters = request.form['water_intake_liters']

        # Commit changes to the database
        db.session.commit()
        flash('Patient data updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_patient.html', data=patient_data)


@app.route('/admin/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_data(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    patient = PatientData.query.get(id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        flash('Data deleted successfully!', 'success')
    else:
        flash('Data not found.', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/user/dashboard', methods=['GET', 'POST'])
@login_required
def user_access_data():
    patient_data = None
    if request.method == 'POST':
        # Get form data
        user_id = request.form['user_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Find matching data in PatientData table
        patient_data = PatientData.query.filter_by(
            id=user_id,
            first_name=first_name,
            last_name=last_name
        ).first()
        
        if not patient_data:
            flash("Data not found for the provided information.", "danger")
        else:
            flash("Data found! You can now edit your information.", "success")

    return render_template('user_dashboard.html', patient_data=patient_data)

@app.route('/user/update/<int:id>', methods=['POST'])
@login_required
def user_update_data(id):
    patient_data = PatientData.query.get_or_404(id)
    patient_data.age = request.form['age']
    patient_data.first_name = request.form['first_name']
    patient_data.last_name = request.form['last_name']
    patient_data.height_cm = request.form['height_cm']
    patient_data.weight_kg = request.form['weight_kg']
    patient_data.bmi = request.form['bmi']
    patient_data.heart_rate_bpm = request.form['heart_rate_bpm']
    patient_data.bp_systolic = request.form['bp_systolic']
    patient_data.bp_diastolic = request.form['bp_diastolic']
    patient_data.steps_count = request.form['steps_count']
    patient_data.calories_burned = request.form['calories_burned']
    patient_data.sleep_duration_hours = request.form['sleep_duration_hours']
    patient_data.sleep_quality = request.form['sleep_quality']
    patient_data.mood = request.form['mood']
    patient_data.stress_level = request.form['stress_level']
    patient_data.water_intake_liters = request.form['water_intake_liters']
    db.session.commit()
    return redirect(url_for('user_access_data'))

def plot_bmi_distribution(data):
    plt.figure(figsize=(8, 6))
    sns.histplot(data['bmi'], kde=True, bins=20)
    plt.title('Distribution of BMI')
    plt.xlabel('BMI')
    plt.ylabel('Frequency')
    plt.savefig('static/plots/bmi_distribution.png')

def plot_water_intake_vs_mood(data):
    bins = [0.5, 1, 1.5, 2,3]
    labels = ['Very low','Low', 'Moderate', 'High']
    
    data['water_intake_category'] = pd.cut(data['water_intake_liters'], bins=bins, labels=labels)
    
    water_intake_counts = data['water_intake_category'].value_counts()
    
    plt.figure(figsize=(8, 6))
    plt.pie(water_intake_counts, labels=water_intake_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Blues", len(water_intake_counts)))
    plt.title('Water Intake vs Mood Distribution')
    plt.savefig('static/plots/water_intake_vs_mood.png')

def plot_calories_burned_by_gender(data):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='calories_burned', hue='gender', data=data, palette="Set2")
    plt.title('Exercise Frequency by Gender')
    plt.xlabel('Exercise Frequency')
    plt.ylabel('Count')
    plt.legend(title='Gender', loc='upper right')
    plt.savefig('static/plots/exercise_frequency_by_gender.png')


def plot_sleep_quality_vs_mood(data):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=data['sleep_quality'], y=data['mood'])
    plt.title('Sleep Quality vs Mood')
    plt.xlabel('Sleep Quality')
    plt.ylabel('Mood')
    plt.savefig('static/plots/sleep_quality_vs_mood.png')

def plot_correlation_heatmap(data):
    plt.figure(figsize=(8, 6))
    sns.heatmap(data[['bmi', 'heart_rate_bpm', 'steps_count', 'calories_burned', 'sleep_duration_hours', 'stress_level']].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap of Health Metrics')
    plt.savefig('static/plots/correlation_heatmap.png')


def generate_analysis_charts():
    data = pd.read_csv('health_data.csv')  
    plot_bmi_distribution(data)
    plot_water_intake_vs_mood(data)
    plot_calories_burned_by_gender(data)
    plot_sleep_quality_vs_mood(data)
    plot_correlation_heatmap(data)

@app.route('/analysis')
@login_required
def analysis():
    generate_analysis_charts()
    return render_template('analysis.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)