from sqlalchemy.orm import Session
from app import models, auth, config
import random

def seed_data(db: Session):
    """
    Seeds initial departments, users, students, and performance records
    only if ENV == 'development'.
    """
    if config.ENV != "development":
        print("Skipping database seeding since ENV is not set to 'development'.")
        return

    # Check if we already have users (to prevent duplicate seeding)
    if db.query(models.User).filter(models.User.username == "admin").first():
        print("Database already seeded. Skipping.")
        return

    print("Seeding database for development environment...")

    # 1. Create Departments
    dept_names = [
        "Computer Science & Engineering",
        "Information Technology",
        "Electronics & Communication Engineering",
        "Electrical & Electronics Engineering",
        "Mechanical Engineering"
    ]
    
    depts = []
    for name in dept_names:
        dept = models.Department(name=name)
        db.add(dept)
        depts.append(dept)
    
    db.commit()
    # Refresh to get IDs
    for dept in depts:
        db.refresh(dept)

    # 2. Create Default Admin User
    admin_user = models.User(
        username="admin",
        email="admin@college.edu",
        password_hash=auth.get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin_user)

    # 3. Create Default Student User
    student_user = models.User(
        username="student",
        email="student@college.edu",
        password_hash=auth.get_password_hash("student123"),
        role="student"
    )
    db.add(student_user)
    db.commit()
    db.refresh(student_user)

    # 4. Link Student User to a Student profile
    cs_dept = depts[0]  # CS
    default_student = models.Student(
        user_id=student_user.id,
        name="Alex Mercer",
        roll_number="CS2026001",
        department_id=cs_dept.id,
        semester=6,
        cgpa=8.75,
        attendance=91.2,
        skills="Python, SQL, HTML, CSS, JavaScript, Git",
        interests="Web Development, Software Engineering, Cloud Computing"
    )
    db.add(default_student)
    db.commit()
    db.refresh(default_student)

    # Add performance history for the default student
    perf_records = [
        models.PerformanceRecord(
            student_id=default_student.id,
            semester=4,
            attendance=92.0,
            internal_marks=88.0,
            assignment_score=90.0,
            previous_cgpa=8.5,
            predicted_category="Excellent"
        ),
        models.PerformanceRecord(
            student_id=default_student.id,
            semester=5,
            attendance=90.5,
            internal_marks=85.0,
            assignment_score=92.0,
            previous_cgpa=8.6,
            predicted_category="Excellent"
        )
    ]
    for pr in perf_records:
        db.add(pr)

    # Add career recommendation history for default student
    rec = models.CareerRecommendation(
        student_id=default_student.id,
        career_path="Software Engineer",
        match_score=92.5,
        recommended_skills="System Design, Docker, FastAPI",
        roadmap="1. Master Backend Frameworks (FastAPI)\n2. Study Database Optimization (SQL/NoSQL)\n3. Learn DevOps Basics (Docker, CI/CD)\n4. Build a comprehensive portfolio project."
    )
    db.add(rec)

    # 5. Create ~20 synthetic students spread across departments
    names = [
        "Emily Watson", "Daniel Craig", "Sophia Loren", "Liam Neeson", "Olivia Wilde",
        "Noah Centineo", "Ava DuVernay", "Jackson Pollock", "Isabella Rossellini", "Lucas Hedges",
        "Mia Farrow", "Benjamin Franklin", "Charlotte Bronte", "William Shakespeare", "Amelia Earhart",
        "Arthur Conan Doyle", "Grace Hopper", "Ada Lovelace", "Charles Babbage", "Alan Turing"
    ]

    skills_pool = [
        "Python, R, SQL, Tableau", "HTML, CSS, JavaScript, React", "Java, C++, DSA, OOP",
        "Linux, AWS, Docker, Bash", "Cryptography, Networking, Python", "FastAPI, Git, CI/CD",
        "SQL, Excel, PowerBI", "Deep Learning, PyTorch, Python"
    ]

    interests_pool = [
        "Data Science, Data Analytics", "Web Development, Frontend Design", "Software Engineering, Algorithms",
        "DevOps, Cloud Computing", "Cybersecurity, Penetration Testing", "AI/ML, Research",
        "Business Intelligence, Operations", "Artificial Intelligence, Neural Networks"
    ]

    for i, name in enumerate(names):
        dept = random.choice(depts)
        sem = random.choice([4, 6, 8])
        cgpa = round(random.uniform(5.5, 9.8), 2)
        attendance = round(random.uniform(60.0, 98.0), 1)
        skills = random.choice(skills_pool)
        interests = random.choice(interests_pool)
        roll = f"{dept.name[:2].upper()}{2026000 + i + 2}"

        student = models.Student(
            name=name,
            roll_number=roll,
            department_id=dept.id,
            semester=sem,
            cgpa=cgpa,
            attendance=attendance,
            skills=skills,
            interests=interests
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # Generate standard performance record for ML retraining
        # Map values reasonably to train the model
        internal_marks = round(random.uniform(cgpa * 8, min(100, cgpa * 10 + 5)), 1)
        assignment_score = round(random.uniform(cgpa * 8, min(100, cgpa * 10 + 5)), 1)
        prev_cgpa = max(4.0, min(10.0, round(cgpa + random.uniform(-0.5, 0.5), 2)))
        
        # Calculate expected category
        score = (attendance * 0.2 + internal_marks * 0.3 + prev_cgpa * 10 * 0.3 + assignment_score * 0.2)
        if score >= 83:
            cat = "Excellent"
        elif score >= 70:
            cat = "Good"
        elif score >= 55:
            cat = "Average"
        else:
            cat = "Needs Improvement"

        pr = models.PerformanceRecord(
            student_id=student.id,
            semester=sem,
            attendance=attendance,
            internal_marks=internal_marks,
            assignment_score=assignment_score,
            previous_cgpa=prev_cgpa,
            predicted_category=cat
        )
        db.add(pr)
        db.commit()

    print("Database seeding completed successfully!")
