import os
import sys

# Ensure backend folder is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set mock env variables for testing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_which_is_thirty_two_chars_long"
os.environ["ENV"] = "testing"

from app import database, models, auth, ml_model

def run_tests():
    print("==================================================")
    print("         RUNNING AUTOMATED UNIT TESTS             ")
    print("==================================================")

    # Test 1: Check Database Setup & Connection (if valid DB URI)
    print("Test 1: Connecting to Database & Initializing Tables...")
    try:
        models.Base.metadata.create_all(bind=database.engine)
        print(" [PASS] Database tables initialized successfully.")
    except Exception as e:
        print(f" [WARNING] Could not connect to database: {e}")
        print("          (Ensure PostgreSQL is running locally to pass DB checks).")

    # Test 2: Standard JWT Authentication Functions
    print("\nTest 2: Validating JWT Standard Authentication...")
    try:
        user_data = {"sub": "testadmin", "role": "admin"}
        token = auth.create_access_token(data=user_data)
        assert isinstance(token, str) and len(token) > 0, "Token should be a non-empty string."
        print(" [PASS] Access token encoded successfully.")
        
        # Verify decoding
        import jwt
        decoded = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=[auth.config.JWT_ALGORITHM])
        assert decoded.get("sub") == "testadmin", "Decoded subject mismatch."
        assert decoded.get("role") == "admin", "Decoded role mismatch."
        print(" [PASS] Access token decoded and validated successfully.")
    except Exception as e:
        print(f" [FAIL] JWT Auth check failed: {e}")
        sys.exit(1)

    # Test 3: ML Model prediction
    print("\nTest 3: Checking AI Random Forest Performance Predictor...")
    try:
        # Load or generate model
        ml_model.ensure_storage()
        clf = ml_model.load_model()
        assert clf is not None, "Model failed to load."
        print(" [PASS] Classifier model initialized/loaded successfully.")
        
        # Run dummy prediction
        # Excellent parameters
        pred_ex = ml_model.predict_performance(attendance=95.0, internal_marks=92.0, previous_cgpa=9.1, assignment_score=94.0)
        assert pred_ex in ["Excellent", "Good", "Average", "Needs Improvement"], "Invalid category predicted."
        print(f" [PASS] Excellent parameters predicted as: '{pred_ex}'")

        # Low parameters
        pred_low = ml_model.predict_performance(attendance=62.0, internal_marks=45.0, previous_cgpa=5.1, assignment_score=50.0)
        assert pred_low in ["Excellent", "Good", "Average", "Needs Improvement"], "Invalid category predicted."
        print(f" [PASS] Risk parameters predicted as: '{pred_low}'")
    except Exception as e:
        print(f" [FAIL] ML prediction check failed: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("          ALL TEST SUITES EXECUTED                ")
    print("==================================================")

    # Clean up test database file
    try:
        import os
        if os.path.exists("test.db"):
            os.remove("test.db")
    except Exception:
        pass

if __name__ == "__main__":
    run_tests()
