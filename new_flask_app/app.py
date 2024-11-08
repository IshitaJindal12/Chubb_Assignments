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


with open('feedback_data.json') as file:
    json_data = json.load(file)

csv_data = pd.read_csv('feedback_data.csv')
csv_data_json = csv_data.to_dict(orient='records')

tree = ET.parse('feedback_data.xml')
root = tree.getroot()
xml_data = []
for entry in root.findall('FeedbackEntry'):
    entry_dict = {}
    for child in entry:
        entry_dict[child.tag] = child.text
    xml_data.append(entry_dict)


excel_data = pd.read_excel('feedback_data.xlsx')
excel_data_json = excel_data.to_dict(orient='records')


html_data = pd.read_html('feedback_data.html')[0]
html_data_json = html_data.to_dict(orient='records')

# Combine all data into one list
combined_data = json_data + csv_data_json + xml_data + excel_data_json + html_data_json

# Write combined data to a new JSON file
with open('combined_feedback_data.json', 'w') as outfile:
    json.dump(combined_data, outfile, indent=4)



df = pd.DataFrame(combined_data)

df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
sentiment_score_mean = df['sentiment_score'].mean()
df['sentiment_score'].fillna(sentiment_score_mean, inplace=True)

df['positive_feedback_count'] = pd.to_numeric(df['positive_feedback_count'], errors='coerce')
df['neutral_feedback_count'] = pd.to_numeric(df['neutral_feedback_count'], errors='coerce')
df['negative_feedback_count'] = pd.to_numeric(df['negative_feedback_count'], errors='coerce')

# Replace missing counts with zero if necessary
df['positive_feedback_count'].fillna(0, inplace=True)
df['neutral_feedback_count'].fillna(0, inplace=True)
df['negative_feedback_count'].fillna(0, inplace=True)

# Remove duplicate rows
df.drop_duplicates(inplace=True)

# Calculate average sentiment score if not present
df['average_sentiment_score'] = df.apply(
    lambda row: (row['positive_feedback_count'] - row['negative_feedback_count']) / max(1, row['total_feedback'])
    if pd.isnull(row['average_sentiment_score']) else row['average_sentiment_score'],
    axis=1
)

# Normalize selected columns
df['total_feedback'] = pd.to_numeric(df['total_feedback'], errors='coerce')
df['total_feedback'] = (df['total_feedback'] - df['total_feedback'].min()) / (df['total_feedback'].max() - df['total_feedback'].min())
df['sentiment_score'] = (df['sentiment_score'] - df['sentiment_score'].min()) / (df['sentiment_score'].max() - df['sentiment_score'].min())


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback_data.db'
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
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'analyst', or 'viewer'

@app.route('/admin/load_data', methods=['GET', 'POST'])
@login_required
def load_data():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    # Load the combined data from the JSON file
    with open('combined_feedback_data.json', 'r') as file:
        combined_data = json.load(file)

    # Insert the data into the database
    try:
        with app.app_context():
            for entry in combined_data:
                # Create a new FeedbackData entry for each item in the JSON
                feedback_data = FeedbackData(
                    feedback_id=entry.get('feedback_id'),
                    user_id=entry.get('user_id'),
                    source=entry.get('source'),
                    content=entry.get('content'),
                    sentiment_score=entry.get('sentiment_score'),
                    sentiment_category=entry.get('sentiment_category'),
                    keywords=entry.get('keywords'),
                    timestamp=entry.get('timestamp'),
                    analysis_date=entry.get('analysis_date'),
                    email=entry.get('email'),
                    time_period=entry.get('time_period'),
                    total_feedback=entry.get('total_feedback'),
                    positive_feedback_count=entry.get('positive_feedback_count'),
                    neutral_feedback_count=entry.get('neutral_feedback_count'),
                    negative_feedback_count=entry.get('negative_feedback_count'),
                    average_sentiment_score=entry.get('average_sentiment_score')
                )
                db.session.add(feedback_data)

            db.session.commit()
    except Exception as e:
        db.session.rollback()
    flash(f'Error occurred while adding data: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))



# Define the FeedbackData model
class FeedbackData(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(100)) 
    content = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float)
    sentiment_category = db.Column(db.String(20)) 
    keywords = db.Column(db.String(200)) 
    timestamp = db.Column(db.String(50))
    analysis_date = db.Column(db.String(50)) 
    email = db.Column(db.String(150))
    time_period = db.Column(db.String(50))
    total_feedback = db.Column(db.Integer)
    positive_feedback_count = db.Column(db.Integer)
    neutral_feedback_count = db.Column(db.Integer)
    negative_feedback_count = db.Column(db.Integer)
    average_sentiment_score = db.Column(db.Float)


@app.route('/switch_database/<db_type>')
def switch_database(db_type):
    if db_type == 'mysql':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Ishita@123localhost/health_wellness_db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patient_data.db'
    db.session.remove()
    db.engine.dispose()
    db.create_all()  
    flash(f"Switched to {db_type} database successfully.")
    return redirect(url_for('index'))


# @app.route('/')
# def home():
#     return render_template('home.html')

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=150)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = StringField('Role (admin/viewer)', validators=[DataRequired()])

# Login Form
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
    # Redirect based on role
    if current_user.role == 'admin':
        feedback_data = FeedbackData.query.all() 
        return render_template('admin_dashboard.html', feedback_data=feedback_data)  # Admin dashboard
    else:
        feedback_data = FeedbackData.query.filter_by(user_id=current_user.id).all()
        return render_template('user_dashboard.html', feedback_data=feedback_data)  # Viewer dashboard


@app.route('/admin_dashboard')
def admin_dashboard():
    # Load data from combined_sentiment_data.json
    with open('combined_sentiment_data.json', 'r') as file:
        feedback_data = json.load(file)
    
    return render_template('admin_dashboard.html', feedback_data=feedback_data)

@app.route('/admin/append', methods=['GET', 'POST'])
@login_required
def append_data():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        new_feedback = FeedbackData(
            feedback_id =request.form['feedback_data'],
            user_id=current_user.id, 
            source=request.form['source'],
            content=request.form['content'],
            sentiment_score=request.form['sentiment_score'],
            sentiment_category=request.form['sentiment_category'],
            keywords=request.form['keywords'],
            timestamp=request.form['timestamp'],
            analysis_date=request.form['analysis_date'],
            email=request.form['email'],
            time_period=request.form['time_period'],
            total_feedback=request.form['total_feedback'],
            positive_feedback_count=request.form['positive_feedback_count'],
            neutral_feedback_count=request.form['neutral_feedback_count'],
            negative_feedback_count=request.form['negative_feedback_count'],
            average_sentiment_score=request.form['average_sentiment_score']
        )

        try:
            db.session.add(new_feedback)
            db.session.commit()
            flash('New feedback data added successfully!', 'success')
            return redirect(url_for('dashboard'))  
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding feedback data: {str(e)}', 'danger')
            return redirect(url_for('append_data'))  

    return render_template('append_data.html') 

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_data(id):
    feedback_data = FeedbackData.query.filter_by(feedback_id=id, user_id=current_user.id).first()
    if not feedback_data:
        flash('You do not have permission to edit this data.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        feedback_data.feedback_id =request.form['feedback_data'],
        feedback_data.user_id=current_user.id, 
        feedback_data.source = request.form['source']
        feedback_data.content = request.form['content']
        feedback_data.sentiment_score = request.form['sentiment_score']
        feedback_data.sentiment_category = request.form['sentiment_category']
        feedback_data.keywords = request.form['keywords']
        feedback_data.timestamp = request.form['timestamp']
        feedback_data.analysis_date = request.form['analysis_date']
        feedback_data.email = request.form['email']
        feedback_data.time_period = request.form['time_period']
        feedback_data.total_feedback = request.form['total_feedback']
        feedback_data.positive_feedback_count = request.form['positive_feedback_count']
        feedback_data.neutral_feedback_count = request.form['neutral_feedback_count']
        feedback_data.negative_feedback_count = request.form['negative_feedback_count']
        feedback_data.average_sentiment_score = request.form['average_sentiment_score']

        db.session.commit()
        flash('Data updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_feedback_data.html', data=feedback_data)

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_data(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    feedback_data = FeedbackData.query.get(id)
    if not feedback_data:
        flash('Feedback data not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if isinstance(feedback_data.timestamp, str):
        feedback_data.timestamp = datetime.strptime(feedback_data.timestamp, '%Y-%m-%d')

    if request.method == 'POST':
        feedback_data.feedback_id =request.form['feedback_data'],
        feedback_data.user_id=current_user.id, 
        feedback_data.source = request.form['source']
        feedback_data.content = request.form['content']
        feedback_data.sentiment_score = request.form['sentiment_score']
        feedback_data.sentiment_category = request.form['sentiment_category']
        feedback_data.keywords = request.form['keywords']
        feedback_data.timestamp = request.form['timestamp']
        feedback_data.analysis_date = request.form['analysis_date']
        feedback_data.email = request.form['email']
        feedback_data.time_period = request.form['time_period']
        feedback_data.total_feedback = request.form['total_feedback']
        feedback_data.positive_feedback_count = request.form['positive_feedback_count']
        feedback_data.neutral_feedback_count = request.form['neutral_feedback_count']
        feedback_data.negative_feedback_count = request.form['negative_feedback_count']
        feedback_data.average_sentiment_score = request.form['average_sentiment_score']

        db.session.commit()
        flash('Feedback data updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_feedback.html', data=feedback_data)

@app.route('/admin/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_data(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    feedback = FeedbackData.query.get(id)
    if feedback:
        db.session.delete(feedback)
        db.session.commit()
        flash('Data deleted successfully!', 'success')
    else:
        flash('Data not found.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/user/dashboard', methods=['GET', 'POST'])
@login_required
def user_access_data():
    feedback_data = None
    if request.method == 'POST':
        print(request.form)  # Log all form data
        # Get data from the form
        user_id = request.form['user_id']
        email = request.form['email']
        feedback_id = request.form['feedback_id']

        feedback_data = FeedbackData.query.filter_by(
            user_id=user_id,
            email=email,
            feedback_id=feedback_id
        ).first()

        if feedback_data:
            flash("Data found! You can now edit your information.", "success")
        else:
            flash("Data not found for the provided information.", "danger")

    return render_template('user_dashboard.html', feedback_data=feedback_data)

@app.route('/user/update/<int:id>', methods=['POST'])
@login_required
def user_update_data(id):
    feedback_data = FeedbackData.query.get_or_404(id)

    feedback_data.source = request.form['source']
    feedback_data.content = request.form['content']
    feedback_data.sentiment_score = request.form['sentiment_score']
    feedback_data.sentiment_category = request.form['sentiment_category']
    feedback_data.keywords = request.form['keywords']
    feedback_data.timestamp = request.form['timestamp']
    feedback_data.analysis_date = request.form['analysis_date']
    feedback_data.email = request.form['email']
    feedback_data.time_period = request.form['time_period']
    feedback_data.total_feedback = request.form['total_feedback']
    feedback_data.positive_feedback_count = request.form['positive_feedback_count']
    feedback_data.neutral_feedback_count = request.form['neutral_feedback_count']
    feedback_data.negative_feedback_count = request.form['negative_feedback_count']
    feedback_data.average_sentiment_score = request.form['average_sentiment_score']

    db.session.commit()
    flash("Data updated successfully!", "success")
    return redirect(url_for('user_access_data'))

def plot_sentiment_score_distribution(data):
    plt.figure(figsize=(8, 6))
    sns.histplot(data['sentiment_score'], kde=True, bins=20)
    plt.title('Distribution of Sentiment Scores')
    plt.xlabel('Sentiment Score')
    plt.ylabel('Frequency')
    plt.savefig('static/plots/sentiment_score_distribution.png')

def plot_sentiment_category_distribution(data):
    sentiment_counts = data['sentiment_category'].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3", len(sentiment_counts)))
    plt.title('Sentiment Category Distribution')
    plt.savefig('static/plots/sentiment_category_distribution.png')

def plot_feedback_source_distribution(data):
    source_counts = data['source'].value_counts()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=source_counts.index, y=source_counts.values, palette="viridis")
    plt.title('Feedback Source Distribution')
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.savefig('static/plots/feedback_source_distribution.png')

def plot_sentiment_over_time(data):
    data['analysis_date'] = pd.to_datetime(data['analysis_date'])
    daily_sentiment_avg = data.groupby('analysis_date')['sentiment_score'].mean()
    
    plt.figure(figsize=(10, 6))
    plt.plot(daily_sentiment_avg.index, daily_sentiment_avg.values, marker='o', color='b')
    plt.title('Average Sentiment Score Over Time')
    plt.xlabel('Date')
    plt.ylabel('Average Sentiment Score')
    plt.grid()
    plt.savefig('static/plots/sentiment_over_time.png')

def plot_correlation_heatmap_sentiment(data):
    plt.figure(figsize=(8, 6))
    sns.heatmap(data[['sentiment_score', 'positive_feedback_count', 'neutral_feedback_count', 'negative_feedback_count']].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap of Sentiment Metrics')
    plt.savefig('static/plots/sentiment_correlation_heatmap.png')

def generate_sentiment_analysis_charts():
    data = pd.read_csv('sentiment_data.csv')
    plot_sentiment_score_distribution(data)
    plot_sentiment_category_distribution(data)
    plot_feedback_source_distribution(data)
    plot_sentiment_over_time(data)
    plot_correlation_heatmap_sentiment(data)

@app.route('/sentiment_analysis')
@login_required
def sentiment_analysis():
    generate_sentiment_analysis_charts()
    return render_template('sentiment_analysis.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)