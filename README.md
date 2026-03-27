

# Adaptive Testing Platform

An AI-assisted adaptive quiz platform with:

- A React + Vite frontend (`client`)
- A FastAPI backend (`server`)
- MongoDB-backed question and user data
- Adaptive difficulty progression based on user performance
- Optional AI question generation via OpenAI

## Tech Stack

- Frontend: React, Vite, Material UI, Framer Motion, Firebase Auth/Firestore
- Backend: FastAPI, Uvicorn, Pydantic, PyMongo, JWT
- Database: MongoDB
- AI: OpenAI API (for question generation)

## Project Structure

```text
adaptive-testing-platform-main/
  client/   # React app
  server/   # FastAPI API
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+ (3.11 recommended)
- MongoDB (local or Atlas URI)

## Environment Variables

Create a `.env` file in the project root (`adaptive-testing-platform-main/.env`):

```env
# Backend
PORT=5000
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=adaptive_quiz
JWT_SECRET=change-me-in-production

# AI Question Generation
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=800
TEMPERATURE=0.7
DAILY_QUESTION_LIMIT=20
```

Notes:

- `OPENAI_API_KEY` is required if you want to use the AI generation endpoints.
- The frontend currently includes Firebase configuration in source code (`client/src/firebase/config.js`).

## Setup and Run

### 1) Backend (FastAPI)

From `server`:

```powershell
cd C:\Users\Yash\OneDrive\Desktop\final_year_adaptive\adaptive-testing-platform-main\server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Backend starts on: `http://localhost:5000`

Health check: `GET http://localhost:5000/api/health`

### 2) Frontend (React + Vite)

From `client`:

```powershell
cd C:\Users\Yash\OneDrive\Desktop\final_year_adaptive\adaptive-testing-platform-main\client
npm install
npm run dev
```

Frontend starts on: `http://localhost:3000`

Vite is configured to proxy `/api` requests to `http://localhost:5000`.

## Main Features

- Adaptive quiz flow (`/quiz`) with:
  - Dynamic difficulty adjustment
  - Topic-wise knowledge state tracking
  - Per-question feedback and final summary
- Authentication APIs:
  - Email/password register/login
  - JWT-protected profile routes
- Question APIs:
  - Fetch by topic/difficulty
  - Generate AI questions and store in MongoDB
- Admin UI routes for question management and analytics

## Key API Endpoints

- `GET /` - API root message
- `GET /api/health` - health + MongoDB connectivity
- `GET /api/questions` - list questions (`topic`, `difficulty` query supported)
- `POST /api/questions/generate` - generate questions via AI
- `POST /api/quiz/start` - start quiz session
- `POST /api/quiz/submit` - submit answer and get next question
- `POST /api/auth/register` - register user
- `POST /api/auth/login` - login user
- `GET /api/auth/me` - current user (JWT required)

## Typical Local Workflow

1. Start MongoDB.
2. Start backend on port `5000`.
3. Start frontend on port `3000`.
4. Open `http://localhost:3000`.
5. Go to `/quiz` and begin adaptive test.

## Troubleshooting

- **`No questions available`**: Ensure your MongoDB has records in the `questions` collection.
- **`OpenAI API key not found`**: Add `OPENAI_API_KEY` to root `.env`.
- **Proxy/API errors in frontend**: Confirm backend is running on `http://localhost:5000`.
- **Auth token issues**: Check `JWT_SECRET` is set and consistent.

## Development Notes

- There are legacy/test components and endpoints in the repo; primary production flow uses:
  - Frontend route: `/quiz`
  - Backend endpoints: `/api/quiz/start` and `/api/quiz/submit`
- CORS is currently permissive (`allow_origins=["*"]`) and should be tightened for production.

## License

No license file detected in this repository. Add a `LICENSE` file if you plan to distribute the project.
