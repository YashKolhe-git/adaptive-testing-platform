import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

app = Flask(__name__)
# Simplest CORS configuration
CORS(app, supports_credentials=True)  # This will allow all origins

load_dotenv() 
#yd
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
db = SQLAlchemy(app)

# Add user session storage
user_sessions = {}

class Question(db.Model):
    __tablename__ = "questions"  # Changed to lowercase

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Changed to String to match CSV
    category = db.Column(db.String(100), nullable=False)
    option_1 = db.Column(db.String(1000), nullable=False)
    option_2 = db.Column(db.String(1000), nullable=False)
    option_3 = db.Column(db.String(1000), nullable=False)
    option_4 = db.Column(db.String(1000), nullable=False)

    def __init__(self, text, answer, difficulty, category, option_1, option_2, option_3, option_4):
        self.text = text
        self.answer = answer
        self.difficulty = difficulty
        self.category = category
        self.option_1 = option_1
        self.option_2 = option_2
        self.option_3 = option_3
        self.option_4 = option_4
    
    def map(self):
        return {
            'id': self.id,
            'text': self.text,
            'difficulty': self.difficulty,
            'category': self.category,
            'options': [
                self.option_1,
                self.option_2,
                self.option_3,
                self.option_4
            ]
        }

@app.route('/api/questions/random', methods=['GET'])
def get_random_question():
    # Get difficulty from query params, default to 5
    difficulty = request.args.get('difficulty', 5, type=int)
    
    # Get question near the requested difficulty level
    question = Question.query.filter(
        Question.difficulty.between(difficulty - 1, difficulty + 1)
    ).order_by(db.func.random()).first()
    
    if not question:
        return jsonify({'error': 'No questions found'}), 404
    
    return jsonify(question.map())

@app.route('/api/questions/check/<int:id>', methods=['POST'])
def check_answer(id):
    data = request.get_json()
    user_answer = data.get('answer', '').strip().lower()
    
    question = Question.query.get_or_404(id)
    correct = user_answer == question.answer.strip().lower()
    
    return jsonify({
        'correct': correct,
        'correctAnswer': question.answer if not correct else None
    })

# Add new routes for adaptive testing
@app.route('/api/session/start', methods=['POST'])
def start_session():
    session_id = str(abs(hash(str(np.random.random()))))
    user_sessions[session_id] = {
        'current_difficulty': 3,  # Start with Medium (3)
        'questions_asked': [],
        'consecutive_correct': 0,
        'consecutive_wrong': 0,
        'wrong_answers_count': {}
    }
    print(f"Created session: {session_id}")
    return jsonify({'session_id': session_id})

@app.route('/api/questions/adaptive/<session_id>', methods=['GET'])
def get_adaptive_question(session_id):
    try:
        print(f"Getting question for session: {session_id}")  # Debug log
        print(f"Available sessions: {list(user_sessions.keys())}")  # Debug log
        
        if session_id not in user_sessions:
            return jsonify({'error': 'Invalid session'}), 404
        
        session = user_sessions[session_id]
        current_difficulty = session['current_difficulty']
        
        # Convert numeric difficulty to text
        difficulty_map = {
            1: 'Easy',
            2: 'Easy',
            3: 'Medium',
            4: 'Medium',
            5: 'Hard'
        }
        
        difficulty_level = difficulty_map[current_difficulty]
        
        # Get questions not already asked
        question = Question.query.filter(
            Question.difficulty == difficulty_level,
            ~Question.id.in_(session['questions_asked'])
        ).order_by(db.func.random()).first()
        
        if not question:
            # If no questions at current difficulty, try adjacent difficulties
            question = Question.query.filter(
                ~Question.id.in_(session['questions_asked'])
            ).order_by(db.func.random()).first()
        
        if not question:
            return jsonify({'error': 'No more questions available'}), 404
        
        # Track this question
        session['questions_asked'].append(question.id)
        
        return jsonify(question.map())
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/questions/check/<session_id>/<int:id>', methods=['POST'])
def check_adaptive_answer(session_id, id):
    if session_id not in user_sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    session = user_sessions[session_id]
    data = request.get_json()
    user_answer = data.get('answer', '').strip().lower()
    
    question = Question.query.get_or_404(id)
    correct = user_answer == question.answer.strip().lower()
    
    # Simple difficulty adjustment - one level at a time
    if correct and session['current_difficulty'] < 5:
        session['current_difficulty'] += 1  # Increase by 1 if correct
    elif not correct and session['current_difficulty'] > 1:
        session['current_difficulty'] -= 1  # Decrease by 1 if wrong
        
        # Track wrong answer for recommendations
        category = question.category
        session['wrong_answers_count'][category] = session['wrong_answers_count'].get(category, 0) + 1

    response = {
        'correct': correct,
        'correctAnswer': question.answer if not correct else None,
        'nextDifficulty': session['current_difficulty']
    }
    
    # Add recommendations if this was the last question
    if len(session['questions_asked']) >= 20:
        response['recommendations'] = get_recommendations(session['wrong_answers_count'])
        
    return jsonify(response)

def get_recommendations(wrong_answers_count):
    if not wrong_answers_count:
        return ["Great job! You got everything right!"]
    
    recommendations = []
    
    # Apply K-means clustering if we have enough data
    if len(wrong_answers_count) > 1:
        df = pd.DataFrame(list(wrong_answers_count.items()), columns=['Topic', 'Wrong Count'])
        n_clusters = min(len(np.unique(df['Wrong Count'])), 3)
        
        if n_clusters >= 2:
            X = df['Wrong Count'].values.reshape(-1, 1)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            df['Cluster'] = kmeans.fit_predict(X)
            
            # Sort clusters by wrong count to identify most problematic areas
            cluster_means = df.groupby('Cluster')['Wrong Count'].mean().sort_values(ascending=False)
            
            for cluster in cluster_means.index:
                cluster_topics = df[df['Cluster'] == cluster]['Topic'].tolist()
                if cluster == cluster_means.index[0]:
                    recommendations.append(f"Focus areas: {', '.join(cluster_topics)}")
                else:
                    recommendations.append(f"Additional practice recommended in: {', '.join(cluster_topics)}")
    else:
        # Simple recommendation for single topic
        topic, count = next(iter(wrong_answers_count.items()))
        recommendations.append(f"Focus on improving in: {topic}")
    
    return recommendations

def init_db():
    with app.app_context():
        db.create_all()

init_db()

@app.route('/api/debug/questions', methods=['GET'])
def debug_questions():
    questions = Question.query.all()
    return jsonify({
        'count': len(questions),
        'sample': [q.map() for q in questions[:3]] if questions else []
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)

