import pandas as pd
from app import db, Question, app

def convert_difficulty(diff_text):
    """Convert text difficulty to number"""
    difficulty_map = {
        'Easy': 2,
        'Medium': 5,
        'Hard': 8
    }
    return difficulty_map.get(diff_text, 5)  # default to 5 if unknown

def load_questions_from_csv():
    with app.app_context():
        # First, drop existing tables and create new ones
        db.drop_all()
        db.create_all()
        
        # Read your CSV file
        df = pd.read_csv('./python_mcq_dataset.csv')
        
        # Map your CSV columns to Question model fields
        for _, row in df.iterrows():
            try:
                question = Question(
                    text=str(row['Question']),
                    answer=str(row['Correct Answer']),
                    difficulty=str(row['Difficulty']),  # Keep as string
                    category=str(row['Topic']),
                    option_1=str(row['Option 1']),
                    option_2=str(row['Option 2']),
                    option_3=str(row['Option 3']),
                    option_4=str(row['Option 4'])
                )
                db.session.add(question)
            except Exception as e:
                print(f"Error adding question: {row['Question']}")
                print(f"Error: {str(e)}")
                continue
        
        try:
            db.session.commit()
            print("Successfully loaded all questions!")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to database: {str(e)}")

if __name__ == "__main__":
    load_questions_from_csv() 