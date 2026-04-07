# AI Interview Platform - Dependencies & Installation Guide

## All Required Libraries & APIs

### Backend Dependencies

**Python Packages** (in `requirements.txt`):
```
fastapi==0.104.1              # Web framework
uvicorn==0.24.0               # ASGI server
sqlalchemy==2.0.23            # ORM
psycopg2-binary==2.9.9        # PostgreSQL driver
pydantic==2.5.0               # Data validation
pydantic-settings==2.1.0      # Settings management
python-jose==3.3.0            # JWT tokens
passlib==1.7.4                # Password hashing (bcrypt)
python-multipart==0.0.6       # Form data parsing
groq==0.1.2                   # Groq API client
python-dotenv==1.0.0          # Environment variables
aiofiles==23.2.1              # Async file operations
opencv-python==4.8.1.78       # Video processing
numpy==1.24.3                 # Numerical computing
pillow==10.1.0                # Image processing
```

**Installation:**
```bash
pip install -r requirements.txt
```

**External APIs:**
- **Groq API**: https://console.groq.com
  - Sign up for free account
  - Generate API key
  - Used for: Question generation, answer analysis, feedback
  - Free tier: Sufficient for development

---

### Frontend Dependencies

**Node Packages** (in `package.json`):
```json
{
  "dependencies": {
    "react": "^18.2.0",              // UI library
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.17.0",   // Routing
    "axios": "^1.6.0",               // HTTP client
    "zustand": "^4.4.0",             // State management
    "lucide-react": "^0.293.0",      // Icons
    "date-fns": "^2.30.0"            // Date utilities
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0", // Vite React plugin
    "vite": "^5.0.0",                // Build tool
    "tailwindcss": "^3.3.5",         // Styling
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16"
  }
}
```

**Installation:**
```bash
npm install
```

---

### Database

**PostgreSQL** (12 or higher):
- Download: https://www.postgresql.org/download/
- Windows: Use installer from official site
- Mac: `brew install postgresql`
- Linux: `sudo apt-get install postgresql`

**Database Setup:**
```bash
# Create database and user
psql -U postgres

CREATE DATABASE ai_interview_db;
CREATE USER interview_user WITH PASSWORD 'your_password';
ALTER ROLE interview_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE ai_interview_db TO interview_user;

# Load schema
\c ai_interview_db
\i DATABASE_SCHEMA.sql
```

---

### Development Tools (Optional)

**Postman** (API Testing):
- Download: https://www.postman.com/downloads/
- Import API collection from backend docs

**pgAdmin** (Database GUI):
- Download: https://www.pgadmin.org/
- Alternative to command-line psql

**VS Code Extensions**:
- REST Client (testing APIs)
- SQLTools (database management)
- Tailwind CSS IntelliSense
- ES7+ React/Redux snippets

---

### Deployment Dependencies

**For Production Backend:**
```bash
# Additional production packages
pip install gunicorn==21.2.0     # Production WSGI server
pip install python-multipart==0.0.6
pip install email-validator==2.1.0
```

**Production Server Setup:**
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Using with Nginx reverse proxy
# (See deployment guide for full setup)
```

**For Production Frontend:**
```bash
# Build for production
npm run build  # Creates optimized dist/ folder

# Serve static files
# (Deploy dist/ to CDN or web server)
```

---

## Complete Installation Steps

### Windows Setup

1. **Install Prerequisites:**
   - Python 3.10+: https://python.org
   - Node.js 18+: https://nodejs.org
   - PostgreSQL 12+: https://postgresql.org
   - Git: https://git-scm.com

2. **Clone Project:**
```bash
git clone <repo-url>
cd ai-interview-platform
```

3. **Run Setup Script:**
```bash
setup.bat
```

4. **Configure Environment:**
```bash
cd backend
copy .env.example .env
# Edit .env with your settings
```

5. **Create Database:**
```bash
psql -U postgres -f DATABASE_SCHEMA.sql
```

6. **Start Services:**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

### Mac/Linux Setup

1. **Install Prerequisites:**
```bash
# Using Homebrew (Mac)
brew install python@3.10 node postgresql

# Using apt (Linux)
sudo apt-get install python3.10 nodejs postgresql
```

2. **Clone and Setup:**
```bash
git clone <repo-url>
cd ai-interview-platform
chmod +x setup.sh
./setup.sh
```

3. **Configure Environment:**
```bash
cd backend
cp .env.example .env
# Edit .env with your values
nano .env  # or your favorite editor
```

4. **Create Database:**
```bash
psql -U postgres -f DATABASE_SCHEMA.sql
```

5. **Start Services:**
```bash
# Terminal 1
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm run dev
```

---

## API Keys Required

### 1. Groq API (Required)
**Purpose:** AI question generation, answer analysis, scoring

**Steps:**
1. Go to https://console.groq.com
2. Sign up with email
3. Navigate to "API Keys"
4. Create new key
5. Copy key to `.env`:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxx
```

**Rate Limits (Free Tier):**
- 30 requests per minute
- 3 requests per 1 minute

---

### 2. Secret Key Generation
**Purpose:** JWT token encryption

**Generate:**
```python
python3
>>> import secrets
>>> secrets.token_urlsafe(32)
'YOUR_SECRET_KEY_HERE'
```

Add to `.env`:
```env
SECRET_KEY=your_generated_key_here
```

---

### 3. Database Credentials
**Purpose:** PostgreSQL connection

**Create User:**
```sql
CREATE USER interview_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_interview_db TO interview_user;
```

Update `.env`:
```env
DATABASE_URL=postgresql://interview_user:your_password@localhost:5432/ai_interview_db
```

---

## Verification

### Test Backend
```bash
# Check API docs
curl http://localhost:8000/docs

# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}
```

### Test Frontend
```bash
# Check if frontend loads
curl http://localhost:3000

# Should return HTML page
```

### Test Database Connection
```bash
# From backend/
python3
>>> from app.core.database import SessionLocal
>>> db = SessionLocal()
>>> print("✓ Connected to database")
```

---

## Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  (Mac/Linux)
netstat -ano | findstr :8000  (Windows)

# Kill process
kill -9 <PID>  (Mac/Linux)
taskkill /PID <PID> /F  (Windows)
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres

# Reset database
dropdb ai_interview_db
createdb ai_interview_db
psql -U postgres -f DATABASE_SCHEMA.sql
```

### Missing Environment Variables
```bash
# Copy example file
cp backend/.env.example backend/.env

# Edit with your values
nano backend/.env
```

### Groq API Errors
- Verify API key is correct
- Check rate limits haven't been exceeded
- Ensure API key has permission for chat.completions

---

## Production Deployment Checklist

- [ ] Change `ENVIRONMENT=production` in .env
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure real database with backups
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure email for notifications
- [ ] Set up logging and monitoring
- [ ] Run database migrations
- [ ] Test all endpoints
- [ ] Configure CORS for production URL
- [ ] Set up rate limiting
- [ ] Enable API authentication
- [ ] Configure automated backups
- [ ] Set up CI/CD pipeline

---

