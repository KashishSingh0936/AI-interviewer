# AI Interview Platform - Full Setup Guide

## Project Overview

A full-stack web application for an AI-powered interview platform with:
- **Backend**: FastAPI + Python AI interviewer integration
- **Frontend**: React + Vite with Tailwind CSS
- **Database**: PostgreSQL
- **Authentication**: JWT-based
- **AI**: Groq API for question generation and answer analysis

## System Architecture

```
ai-interview-platform/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── ai_module/       # AI interviewer integration
│   │   ├── core/            # Config, security, database
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
└── frontend/
    ├── src/
    │   ├── pages/           # Page components
    │   ├── components/      # Reusable components
    │   ├── services/        # API calls
    │   ├── context/         # State management (Zustand)
    │   └── App.jsx
    ├── package.json
    └── vite.config.js
```

---

## Prerequisites

### System Requirements
- Python 3.10+
- Node.js 18+
- PostgreSQL 12+
- Git

### API Keys Required
1. **Groq API Key**: Get from [console.groq.com](https://console.groq.com)
   - Create account and generate API key
   - Used for AI interviewer

---

## Backend Setup (FastAPI)

### Step 1: Install Python Dependencies

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Edit .env file with your settings
nano .env
```

Key variables to set:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_interview_db
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
FRONTEND_URL=http://localhost:3000
```

### Step 3: Create PostgreSQL Database

```sql
-- Connect to your PostgreSQL instance
psql -U postgres

-- Create database
CREATE DATABASE ai_interview_db;

-- Create user with password
CREATE USER interview_user WITH PASSWORD 'your_password';

-- Grant privileges
ALTER ROLE interview_user SET client_encoding TO 'utf8';
ALTER ROLE interview_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE interview_user SET default_transaction_deferrable TO on;
ALTER ROLE interview_user SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE ai_interview_db TO interview_user;

-- Connect to database
\c ai_interview_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO interview_user;
```

Update `.env` with database URL:
```env
DATABASE_URL=postgresql://interview_user:your_password@localhost:5432/ai_interview_db
```

### Step 4: Run Backend

```bash
# From backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at**: `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

---

## Frontend Setup (React)

### Step 1: Install Node Dependencies

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

### Step 2: Start Development Server

```bash
# Start React development server
npm run dev
```

**Frontend will be available at**: `http://localhost:3000`

### Step 3: Build for Production

```bash
npm run build
npm run preview
```

---

## Database Schema Overview

### Core Tables

```sql
-- Users (candidates and interviewers)
users:
  - id (primary key)
  - email (unique)
  - username (unique)
  - hashed_password
  - full_name
  - role: 'candidate' | 'interviewer'
  - is_active
  - created_at, updated_at

-- Domains (interview topics)
domains:
  - id (primary key)
  - name (unique): "Data Science", "Web Development", etc.
  - description
  - created_at

-- Roles (positions within domains)
roles:
  - id (primary key)
  - name: "Data Scientist", "Frontend Developer", etc.
  - description
  - domain_id (foreign key) UNIQUE(domain_id, name)
  - created_at

-- Interviews
interviews:
  - id (primary key)
  - candidate_id (foreign key)
  - interviewer_id (nullable - NULL for mock)
  - domain_id (foreign key)
  - role_id (foreign key)
  - interview_type: 'mock' | 'real'
  - status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
  - difficulty: 'beginner' | 'intermediate' | 'advanced'
  - overall_score: 0-10
  - accuracy_percentage: 0-100
  - scheduled_at (nullable - for real interviews)
  - started_at, completed_at
  - created_at, updated_at

-- Questions & Answers
questions:
  - id (primary key)
  - interview_id (foreign key)
  - question_number (1, 2, 3)
  - question_text
  - answer_text (candidate's answer)
  - audio_file_path (optional)
  - video_file_path (optional)
  - ai_feedback (AI evaluation)
  - score: 0-10
  - is_correct: boolean
  - weak_area: string (if identified)
  - created_at, updated_at

-- Notifications
notifications:
  - id (primary key)
  - user_id (foreign key)
  - interview_id (nullable)
  - title, message
  - is_read
  - created_at
```

---

## API Endpoints Overview

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user profile

### Interviews
- `POST /api/interviews` - Create mock interview (candidate)
- `GET /api/interviews` - Get user's interviews
- `GET /api/interviews/{id}` - Get interview details
- `POST /api/interviews/{id}/start` - Start interview
- `GET /api/interviews/{id}/next-question` - Get next question
- `POST /api/interviews/{id}/answer` - Submit answer with AI feedback
- `POST /api/interviews/{id}/complete` - Complete interview

### Domains & Roles
- `GET /api/domains` - Get all domains with roles
- `GET /api/domains/{id}` - Get domain details
- `POST /api/domains` - Create domain (interviewer)
- `GET /api/domains/{id}/roles` - Get roles in domain
- `POST /api/domains/{id}/roles` - Create role (interviewer)
- `POST /api/domains/init` - Initialize predefined domains

---

## Authentication Flow

### JWT Tokens
- Access tokens expire in 24 hours (configurable)
- Tokens are stored in browser localStorage (frontend)
- Sent in `Authorization: Bearer <token>` header

### Login Flow
```javascript
1. User submits email + password
2. Backend validates and returns JWT token
3. Frontend stores token and user data in Zustand store
4. Token automatically included in API requests
5. On 401 response: token cleared, redirect to login
```

---

## User Roles & Permissions

### Candidate
✅ Can create mock interviews
✅ Can take interviews
✅ Can view own scores and feedback
✅ Cannot create/modify domains or roles
✅ Cannot schedule interviews
✅ Cannot view other candidates' results

### Interviewer/Organization
✅ Can create new domains and roles
✅ Can schedule real interviews for candidates
✅ Can view scheduled candidates
✅ Can view analytics
✅ Can manually adjust scores (future)
❌ Cannot take interviews

---

## Predefined Domains & Roles

The system comes with these domains:
- Data Science
- Web Development
- Machine Learning
- Software Engineering
- Cybersecurity
- Cloud Computing
- Mobile Development
- Game Development
- Blockchain
- AI/NLP
- Database
- DevOps

Each domain has 3 role options, e.g.:
- Data Science: Data Scientist, Data Analyst, ML Engineer
- Web Dev: Frontend Developer, Backend Developer, Full Stack Developer

These are auto-initialized on first backend startup.

---

## Interview Flow

### Mock Interview (Candidate Self-Initiated)
1. Candidate selects domain and role
2. System generates 3 questions
3. Candidate answers each question (text, audio, or video)
4. AI analyzes answer in real-time
5. AI provides score (0-10), feedback, weak area
6. Interview completes after 3 questions
7. Candidate sees final report

### Real Interview (Scheduled by Interviewer)
1. Interviewer schedules interview for candidate
2. Candidate receives notification
3. Same flow as mock interview
4. Additional: Interviewer can view results and add notes

---

## AI Scoring System

**Scoring Formula (0-10):**
- **9-10**: Correct answer with substantial depth (50+ words)
- **9**: Correct with good length (20-50 words)
- **8**: Correct but brief (<20 words)
- **4**: Incomplete (missing pieces)
- **3**: Vague/generic (right direction)
- **2**: Incorrect (wrong approach)
- **1**: Completely wrong
- **0**: No answer

**Weak Area Detection:**
- Extracts from AI feedback
- Identifies gaps: missing concepts, incomplete understanding, etc.
- Persists for improvement tracking

---

## Deployment

### Backend Deployment (Gunicorn + Nginx)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Frontend Deployment (Static Hosting)

```bash
# Build for production
npm run build

# Deploy dist/ folder to:
# - Vercel
# - Netlify
# - GitHub Pages
# - AWS S3 + CloudFront
# - Any static hosting
```

### Environment Variables for Production

Backend:
```env
ENVIRONMENT=production
DATABASE_URL=<prod_postgres_url>
SECRET_KEY=<long_random_string_min_32_chars>
FRONTEND_URL=<prod_frontend_url>
GROQ_API_KEY=<your_groq_key>
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

Frontend:
```env
VITE_API_URL=<prod_backend_api_url>
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U interview_user -d ai_interview_db -h localhost

# Check Django migrations
python -m alembic upgrade head

# Reset database
dropdb ai_interview_db
createdb ai_interview_db
```

### Token Errors
- Clear localStorage: `localStorage.clear()`
- Re-login
- Check SECRET_KEY in .env

### AI Module Issues
- Verify GROQ_API_KEY is set
- Check Groq API status
- Monitor API rate limits

### CORS Errors
- Ensure FRONTEND_URL in .env matches frontend URL
- Check browser console for specific error

---

## Future Enhancements

1. **Video Recording**: Full video capture during interview
2. **Email Notifications**: Send interview reminders/results
3. **Analytics Dashboard**: Detailed performance tracking
4. **Interviewer Feedback**: Manual scoring adjustments
5. **Interview Templates**: Custom question sets
6. **Export Reports**: PDF/Excel report generation
7. **Multi-language Support**: Interview in different languages
8. **Real-time Notifications**: WebSocket support
9. **Rate Limiting**: API protection
10. **Admin Panel**: User and domain management

---

## Security Best Practices

✅ **Implemented**:
- JWT authentication
- Password hashing (bcrypt)
- SQL injection prevention (SQLAlchemy ORM)
- CORS headers
- Input validation (Pydantic)

⚠️ **To Implement**:
- HTTPS/SSL certificates
- Rate limiting
- API key rotation
- Audit logging
- Two-factor authentication
- Data encryption at rest

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Groq Docs**: https://docs.groq.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

## License

MIT License - See LICENSE file for details

