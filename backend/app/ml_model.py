import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy.orm import Session
from app import models

# Get absolute path for ML model storage
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

def ensure_storage():
    """Ensure that the ML model storage directory exists."""
    os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_save_model(data: pd.DataFrame) -> RandomForestClassifier:
    """
    Trains a Random Forest Classifier using features:
    attendance, internal_marks, previous_cgpa, assignment_score
    and target: category.
    Saves the trained model to backend/storage/model.pkl.
    """
    ensure_storage()
    X = data[['attendance', 'internal_marks', 'previous_cgpa', 'assignment_score']]
    y = data['category']
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    
    return clf

def generate_and_train_synthetic():
    """Generates synthetic dataset and trains the initial classifier."""
    np.random.seed(42)
    n_samples = 200
    
    # Random variables mirroring typical university student performance
    attendance = np.random.uniform(50, 100, n_samples)
    internal_marks = np.random.uniform(40, 100, n_samples)
    previous_cgpa = np.random.uniform(4.0, 10.0, n_samples)
    assignment_score = np.random.uniform(40, 100, n_samples)
    
    categories = []
    for i in range(n_samples):
        # Calculate a weighted score with a random noise factor
        score = (attendance[i] * 0.20 + 
                 internal_marks[i] * 0.30 + 
                 previous_cgpa[i] * 10.0 * 0.30 + 
                 assignment_score[i] * 0.20 + 
                 np.random.normal(0, 3.0))
        
        if score >= 83.0:
            categories.append("Excellent")
        elif score >= 70.0:
            categories.append("Good")
        elif score >= 55.0:
            categories.append("Average")
        else:
            categories.append("Needs Improvement")
            
    df = pd.DataFrame({
        'attendance': attendance,
        'internal_marks': internal_marks,
        'previous_cgpa': previous_cgpa,
        'assignment_score': assignment_score,
        'category': categories
    })
    
    train_and_save_model(df)

def load_model() -> RandomForestClassifier:
    """Loads the trained classifier. Trains a synthetic one if it doesn't exist."""
    ensure_storage()
    if not os.path.exists(MODEL_PATH):
        generate_and_train_synthetic()
        
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def predict_performance(attendance: float, internal_marks: float, previous_cgpa: float, assignment_score: float) -> str:
    """Runs prediction on student performance features."""
    clf = load_model()
    features = np.array([[attendance, internal_marks, previous_cgpa, assignment_score]])
    prediction = clf.predict(features)
    return str(prediction[0])

def retrain_from_db(db: Session):
    """
    Retrains the RandomForestClassifier model on database records.
    Falls back to synthetic data if database contains fewer than 5 records.
    """
    records = db.query(models.PerformanceRecord).all()
    if not records or len(records) < 5:
        # Not enough database entries; train with synthetic data
        generate_and_train_synthetic()
        return
        
    data = []
    for r in records:
        cat = r.predicted_category
        # Fallback if prediction category not set
        if not cat:
            score = (r.attendance * 0.20 + 
                     r.internal_marks * 0.30 + 
                     r.previous_cgpa * 10.0 * 0.30 + 
                     r.assignment_score * 0.20)
            if score >= 83.0:
                cat = "Excellent"
            elif score >= 70.0:
                cat = "Good"
            elif score >= 55.0:
                cat = "Average"
            else:
                cat = "Needs Improvement"
                
        data.append({
            'attendance': r.attendance,
            'internal_marks': r.internal_marks,
            'previous_cgpa': r.previous_cgpa,
            'assignment_score': r.assignment_score,
            'category': cat
        })
        
    df = pd.DataFrame(data)
    train_and_save_model(df)
