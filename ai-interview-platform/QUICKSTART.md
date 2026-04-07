# 🚀 AI Interview Platform - Quick Start Guide

## 5-Minute Setup (Docker)

### Prerequisites
- Docker & Docker Compose installed
- Groq API key (get from https://console.groq.com)

### Setup
```bash
# 1. Clone/extract project
cd ai-interview-platform

# 2. Create .env file
cp backend/.env.example backend/.env

# 3. Edit .env with Groq API key
nano backend/.env  # or your editor
# Set: GROQ_API_KEY=your_key_here

# 4. Start with Docker Compose
docker-compose up

# 5. Access the app
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:3000

# 6. Create test account
# Register at http://localhost:3000/register
# Email: test@example.com
# Password: TestPassword123
# Role: Candidate or Interviewer
```

---

## 30-Minute Manual Setup

### Step 1: Backend Setup (10 min)
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env (add Groq API key, database URL)
nano .env

# Start server
python -m uvicorn app.main:app --reload
```

Backend running at: http://localhost:8000

### Step 2: Database Setup (10 min)
```bash
# PostgreSQL must be running

# Option A: Using SQL file
psql -U postgres -f ../DATABASE_SCHEMA.sql

# Option B: Manual setup
psql -U postgres
CREATE DATABASE ai_interview_db;
CREATE USER interview_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ai_interview_db TO interview_user;
\c ai_interview_db
(paste contents of DATABASE_SCHEMA.sql)
```

### Step 3: Frontend Setup (10 min)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend running at: http://localhost:3000

---

## First Time User Flow

### 1. Register
- Choose: **Candidate** or **Interviewer**
- Fill in: Email, Username, Password, Full Name

### 2. For Candidates
- **Dashboard**: View your interviews
- **Create Mock Interview**: 
  - Select Domain (e.g., "Data Science")
  - Select Role (e.g., "Data Scientist")
  - Choose Difficulty (Beginner/Intermediate/Advanced)
- **Start Interview**:
  - Answer each question
  - Get AI feedback immediately
  - See score for each answer
  - View weak areas identified

### 3. For Interviewers
- **Dashboard**: Schedule real interviews
- **Create Domain**: Add custom interview domains
- **Add Roles**: Create specific job roles
- **Schedule Interview**: Assign interview to candidate

---

## Key Features

### ✅ Candidate Features
- Create unlimited mock interviews
- Take interview with AI evaluator
- Get real-time AI feedback
- View score (0-10) for each answer
- Identify weak areas
- Track interview history

### ✅ Interviewer Features
- Create interview domains
- Add custom roles
- Schedule real interviews for candidates
- View candidate submissions
- See AI scores and feedback
- Add manual notes

### ✅ AI Features
- Generates realistic interview questions
- Analyzes answers for correctness
- Provides detailed feedback
- Scores answers 0-10 scale
- Identifies weak areas
- Detects unprofessional behavior

### ✅ Platform Features
- JWT authentication
- Role-based access control
- 12 predefined domains with roles
- Real and mock interview support
- Interview history tracking
- Database persistence

---

## Core Domains & Roles

```
Data Science
├── Data Scientist
├── Data Analyst
└── Machine Learning Engineer

Web Development
├── Frontend Developer
├── Backend Developer
└── Full Stack Developer

Machine Learning
├── ML Engineer
├── AI Researcher
└── Deep Learning Specialist

Software Engineering
├── Software Engineer
├── DevOps Engineer
└── Solutions Architect

Cybersecurity
├── Security Analyst
├── Penetration Tester
└── Security Engineer

Cloud Computing
├── Cloud Architect
├── AWS Developer
└── Cloud Engineer

... and more (12 total domains)
```

---

## API Endpoints Quick Reference

### Authentication
```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login and get token
GET    /api/auth/me                Get profile
```

### Interviews
```
POST   /api/interviews             Create mock interview
GET    /api/interviews             Get your interviews
GET    /api/interviews/{id}        Get interview details
POST   /api/interviews/{id}/start  Start interview
GET    /api/interviews/{id}/next-question  Get next question
POST   /api/interviews/{id}/answer  Submit answer (gets AI feedback)
POST   /api/interviews/{id}/complete  Finish interview
```

### Domains
```
GET    /api/domains                Get all domains with roles
GET    /api/domains/{id}           Get domain details
POST   /api/domains                Create domain (interviewer)
GET    /api/domains/{id}/roles     Get roles in domain
POST   /api/domains/{id}/roles     Add role (interviewer)
```

---

## Troubleshooting

### Port 8000 already in use
```bash
# Kill process on port 8000
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Port 3000 already in use
```bash
lsof -ti:3000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :3000   # Windows
```

### Database connection error
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list               # Mac
# Verify credentials in .env
```

### API returns 401 Unauthorized
- Check token in localStorage
- Try logging out and back in
- Refresh the page

### Groq API errors
- Verify API key is correct
- Check you haven't exceeded rate limits
- Try regenerating API key

---

## Testing the System

### Test Registration & Login
```bash
# Register at http://localhost:3000/register
Email: candidate@test.com
Username: testcandidate
Password: TestPassword123
Full Name: Test Candidate
Role: Candidate
```

### Test Interview Flow
1. Login as candidate
2. Click "Create Mock Interview"
3. Select: Data Science > Data Scientist > Intermediate
4. Click "Start Interview"
5. Answer the 3 questions
6. View your scores and feedback

### Test API with Curl
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123",
    "full_name": "Test User",
    "role": "candidate"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'

# Get domains
curl http://localhost:8000/api/domains \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Environment Variables

### Required
- `GROQ_API_KEY`: Groq API key from https://console.groq.com
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (32+ random characters)

### Optional
- `SMTP_SERVER`: Email server (for notifications)
- `SENDER_EMAIL`: Email for notifications
- `FRONTEND_URL`: Frontend URL for CORS

---

## Next Steps

1. **Add More Domains**: Create custom interview domains
2. **Customize Questions**: Modify AI prompt templates
3. **Email Notifications**: Set up SMTP for alerts
4. **Analytics**: Build performance dashboard
5. **Export Reports**: Add PDF/Excel exports
6. **Video Recording**: Implement WebRTC
7. **Multiplayer**: Add real-time interviews

---

## Support

- 📚 API Docs: http://localhost:8000/docs
- 📖 GitHub: [Repository]
- 💬 Issues: Report bugs on GitHub
- 📧 Contact: [Your email]

---

## License

MIT License - See LICENSE file

---

**Happy Interviewing! 🎉**

Need help? Check INSTALLATION_GUIDE.md or README.md for detailed information.
