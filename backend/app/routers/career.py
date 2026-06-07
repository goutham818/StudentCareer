from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import io
import pandas as pd
from app import database, models, schemas, auth, ml_model

router = APIRouter(tags=["Career & AI Prediction"])

CAREER_PROFILES = {
    "Software Engineer": {
        "skills": ["python", "java", "c++", "dsa", "oop", "git", "system design", "algorithms", "javascript", "sql"],
        "interests": ["coding", "problem solving", "software development", "algorithms", "programming"],
        "min_cgpa": 7.0,
        "roadmap": (
            "1. Focus on Data Structures and Algorithms (DSA) basics.\n"
            "2. Master an Object-Oriented programming language (e.g. Java, C++, Python).\n"
            "3. Learn version control using Git & GitHub.\n"
            "4. Develop understanding of System Design and Software Engineering principles.\n"
            "5. Build multiple backend system projects."
        )
    },
    "Data Scientist": {
        "skills": ["python", "r", "sql", "machine learning", "statistics", "pandas", "data visualization", "numpy", "scikit-learn"],
        "interests": ["analytics", "math", "ai", "research", "data", "statistics", "machine learning"],
        "min_cgpa": 8.0,
        "roadmap": (
            "1. Deepen your knowledge in Statistics, Linear Algebra, and Calculus.\n"
            "2. Master Python, SQL, and data analysis libraries (Pandas, Numpy).\n"
            "3. Study ML theory: Supervised and Unsupervised algorithms.\n"
            "4. Get hands-on with ML packages (Scikit-Learn, XGBoost).\n"
            "5. Work on real-world datasets and publish findings on Kaggle/GitHub."
        )
    },
    "AI Engineer": {
        "skills": ["python", "deep learning", "pytorch", "tensorflow", "nlp", "computer vision", "math", "neural networks", "transformers"],
        "interests": ["artificial intelligence", "robotics", "automation", "neural networks", "ai", "deep learning"],
        "min_cgpa": 8.5,
        "roadmap": (
            "1. Establish strong programming foundations in Python.\n"
            "2. Learn neural network architectures and mathematical foundations of AI.\n"
            "3. Master Deep Learning frameworks (PyTorch or TensorFlow).\n"
            "4. Specialize in a subdomain like Natural Language Processing (NLP) or Computer Vision.\n"
            "5. Build custom AI models and participate in AI hackathons."
        )
    },
    "Data Analyst": {
        "skills": ["sql", "excel", "tableau", "powerbi", "python", "data cleaning", "analytics", "statistics", "pandas"],
        "interests": ["reporting", "business intelligence", "data", "visualization", "analytics", "dashboards"],
        "min_cgpa": 6.5,
        "roadmap": (
            "1. Master SQL for querying databases and data manipulation.\n"
            "2. Learn Advanced Excel (Pivot tables, lookup functions, macros).\n"
            "3. Master a visualization tool like Tableau or PowerBI.\n"
            "4. Learn python basics for data cleaning (pandas).\n"
            "5. Build clean, interactive business dashboards."
        )
    },
    "Cloud Engineer": {
        "skills": ["aws", "azure", "docker", "kubernetes", "linux", "networking", "cloud computing", "terraform", "bash"],
        "interests": ["infrastructure", "cloud", "virtualization", "networking", "systems", "cloud hosting"],
        "min_cgpa": 7.0,
        "roadmap": (
            "1. Learn Linux systems administration and command line basics.\n"
            "2. Understand Computer Networking concepts (TCP/IP, DNS, Subnets).\n"
            "3. Learn a major cloud platform, starting with AWS or Azure certification.\n"
            "4. Learn containerization using Docker & container orchestration (Kubernetes).\n"
            "5. Practice Infrastructure as Code (IaC) using Terraform."
        )
    },
    "Cybersecurity Analyst": {
        "skills": ["linux", "networking", "cryptography", "pen testing", "security", "firewalls", "wireshark", "metasploit"],
        "interests": ["security", "hacking", "cyber", "investigation", "privacy", "defense"],
        "min_cgpa": 7.0,
        "roadmap": (
            "1. Build solid understanding of Operating Systems (Linux, Windows) and Networking.\n"
            "2. Learn basic Cryptography concepts.\n"
            "3. Master security tools like Wireshark, Nmap, and Metasploit.\n"
            "4. Learn security policies, incident response, and pen testing.\n"
            "5. Earn standard entry-level certifications like Security+ or CEH."
        )
    },
    "Full Stack Developer": {
        "skills": ["html", "css", "javascript", "react", "node.js", "databases", "web dev", "api", "express", "mongodb", "postgresql"],
        "interests": ["web design", "building apps", "ui/ux", "frontend", "backend", "web development", "design"],
        "min_cgpa": 6.5,
        "roadmap": (
            "1. Learn frontend basics: HTML5, CSS3, and JavaScript (ES6+).\n"
            "2. Master a frontend framework (e.g. React.js) and responsive design.\n"
            "3. Learn backend development with Node.js/Express, Python/FastAPI, or Java.\n"
            "4. Understand relational and non-relational databases (PostgreSQL, MongoDB).\n"
            "5. Deploy complete full-stack projects using cloud hosting (Vercel, Render)."
        )
    },
    "DevOps Engineer": {
        "skills": ["ci/cd", "git", "linux", "docker", "ansible", "terraform", "jenkins", "cloud", "kubernetes", "python"],
        "interests": ["automation", "systems", "infrastructure", "operations", "scripting", "ci/cd"],
        "min_cgpa": 7.5,
        "roadmap": (
            "1. Gain strong experience in Linux administration and scripting (bash/python).\n"
            "2. Master Git branching strategies and workflow automation.\n"
            "3. Learn CI/CD pipeline automation (GitHub Actions, Jenkins).\n"
            "4. Learn Docker containerization and Kubernetes scaling.\n"
            "5. Learn configuration management and monitoring tools (Ansible, Prometheus, Grafana)."
        )
    }
}

# 1. Prediction Endpoints (registers both /predict and /api/predict)
@router.post("/predict", response_model=schemas.PredictionResponse)
@router.post("/api/predict", response_model=schemas.PredictionResponse)
def predict_student_performance(
    payload: schemas.PredictionRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    """Predict student academic performance category based on attendance, marks, cgpa, and assignment score."""
    try:
        category = ml_model.predict_performance(
            attendance=payload.attendance,
            internal_marks=payload.internal_marks,
            previous_cgpa=payload.previous_cgpa,
            assignment_score=payload.assignment_score
        )
        return {"predicted_category": category}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute prediction: {str(e)}"
        )

# 2. Career Guidance Endpoints (registers both /career-guidance and /api/career-guidance)
@router.post("/career-guidance")
@router.post("/api/career-guidance")
def get_career_guidance(
    student_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Returns scores and roadmaps for each career path based on student skills, interests, and CGPA.
    If student_id is omitted, attempts to find the current logged-in user's student profile.
    """
    student = None
    if student_id:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
    else:
        student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Complete your profile before requesting career guidance."
        )

    # Clean student skills and interests
    student_skills = [s.strip().lower() for s in student.skills.split(",") if s.strip()] if student.skills else []
    student_interests = [i.strip().lower() for i in student.interests.split(",") if i.strip()] if student.interests else []

    recommendations = []
    
    for title, profile in CAREER_PROFILES.items():
        # Match Skills (50%)
        matching_skills = [s for s in profile["skills"] if s in student_skills]
        skills_score = (len(matching_skills) / len(profile["skills"])) * 100 if profile["skills"] else 0
        
        # Match Interests (30%)
        matching_interests = [i for i in profile["interests"] if i in student_interests]
        interests_score = (len(matching_interests) / len(profile["interests"])) * 100 if profile["interests"] else 0
        
        # Match CGPA (20%)
        cgpa_score = 100.0 if student.cgpa >= profile["min_cgpa"] else (student.cgpa / profile["min_cgpa"]) * 100
        
        # Total match score out of 100
        match_score = round((skills_score * 0.50) + (interests_score * 0.30) + (cgpa_score * 0.20), 1)
        
        # Find missing skills
        missing_skills = [s for s in profile["skills"] if s not in student_skills]
        recommended_skills = ", ".join([s.title() for s in missing_skills[:4]]) # Recommend top 4 missing ones

        recommendations.append({
            "career_path": title,
            "match_score": match_score,
            "recommended_skills": recommended_skills if recommended_skills else "All core skills acquired!",
            "roadmap": profile["roadmap"]
        })

    # Sort by match score descending
    recommendations = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)
    
    # Save the top recommendation to career_recommendations table
    top_rec = recommendations[0]
    db_rec = models.CareerRecommendation(
        student_id=student.id,
        career_path=top_rec["career_path"],
        match_score=top_rec["match_score"],
        recommended_skills=top_rec["recommended_skills"],
        roadmap=top_rec["roadmap"]
    )
    db.add(db_rec)
    db.commit()

    return recommendations

# 3. CSV Dataset Upload Endpoints (registers both /upload-dataset and /api/upload-dataset)
@router.post("/upload-dataset")
@router.post("/api/upload-dataset")
async def upload_student_dataset(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(database.get_db)
):
    """
    Upload a student dataset in CSV format.
    Validates, inserts/updates records, and retrains the AI prediction model.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. Please upload a CSV file."
        )
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Strip column names of whitespace
        df.columns = df.columns.str.strip()
        
        # Required columns validation
        required_cols = ['name', 'roll_number', 'department', 'semester', 'cgpa', 'attendance',
                         'skills', 'interests', 'internal_marks', 'assignment_score', 'previous_cgpa', 'category']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV file is missing required columns: {', '.join(missing_cols)}"
            )
            
        records_added = 0
        records_updated = 0
        
        for _, row in df.iterrows():
            # Check or create Department
            dept_name = str(row['department']).strip()
            dept = db.query(models.Department).filter(models.Department.name.ilike(dept_name)).first()
            if not dept:
                dept = models.Department(name=dept_name)
                db.add(dept)
                db.commit()
                db.refresh(dept)
                
            roll = str(row['roll_number']).strip()
            
            # Find or create Student
            student = db.query(models.Student).filter(models.Student.roll_number == roll).first()
            is_new = False
            
            if not student:
                is_new = True
                student = models.Student(
                    roll_number=roll,
                    name=str(row['name']).strip(),
                    department_id=dept.id,
                    semester=int(row['semester']),
                    cgpa=float(row['cgpa']),
                    attendance=float(row['attendance']),
                    skills=str(row['skills']).strip() if pd.notna(row['skills']) else "",
                    interests=str(row['interests']).strip() if pd.notna(row['interests']) else ""
                )
                db.add(student)
                db.commit()
                db.refresh(student)
                
                # Create default user account
                username = roll.lower()
                existing_user = db.query(models.User).filter(models.User.username == username).first()
                if not existing_user:
                    hashed_pw = auth.get_password_hash(f"{roll.lower()}123")
                    student_user = models.User(
                        username=username,
                        email=f"{username}@college.edu",
                        password_hash=hashed_pw,
                        role="student"
                    )
                    db.add(student_user)
                    db.commit()
                    db.refresh(student_user)
                    student.user_id = student_user.id
                    db.commit()
                    db.refresh(student)
            else:
                # Update student profile
                student.name = str(row['name']).strip()
                student.department_id = dept.id
                student.semester = int(row['semester'])
                student.cgpa = float(row['cgpa'])
                student.attendance = float(row['attendance'])
                if pd.notna(row['skills']):
                    student.skills = str(row['skills']).strip()
                if pd.notna(row['interests']):
                    student.interests = str(row['interests']).strip()
                db.commit()
                db.refresh(student)

            # Insert performance record
            pr = models.PerformanceRecord(
                student_id=student.id,
                semester=int(row['semester']),
                attendance=float(row['attendance']),
                internal_marks=float(row['internal_marks']),
                assignment_score=float(row['assignment_score']),
                previous_cgpa=float(row['previous_cgpa']),
                predicted_category=str(row['category']).strip()
            )
            db.add(pr)
            db.commit()
            
            if is_new:
                records_added += 1
            else:
                records_updated += 1
                
        # Retrain the ML Classifier with new database performance records
        ml_model.retrain_from_db(db)
        
        return {
            "message": "Dataset uploaded successfully!",
            "added_students": records_added,
            "updated_students": records_updated,
            "model_status": "Retrained successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing CSV dataset: {str(e)}"
        )
