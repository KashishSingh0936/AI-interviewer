-- AI Interview Platform Database Schema
-- PostgreSQL SQL Script

-- Create Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============= USERS =============
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'candidate' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ============= DOMAINS =============
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_domains_name ON domains(name);

-- ============= ROLES =============
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(domain_id, name)
);

CREATE INDEX idx_roles_domain ON roles(domain_id);
CREATE INDEX idx_roles_name ON roles(name);

-- ============= INTERVIEWS =============
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interviewer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    interview_type VARCHAR(20) DEFAULT 'mock' NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled' NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    overall_score INTEGER DEFAULT 0,
    accuracy_percentage INTEGER DEFAULT 0,
    feedback_summary TEXT,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interviews_candidate ON interviews(candidate_id);
CREATE INDEX idx_interviews_interviewer ON interviews(interviewer_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_type ON interviews(interview_type);

-- ============= QUESTIONS =============
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    audio_file_path VARCHAR(500),
    video_file_path VARCHAR(500),
    ai_feedback TEXT,
    score INTEGER DEFAULT 0,
    is_correct BOOLEAN DEFAULT FALSE,
    weak_area VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(interview_id, question_number)
);

CREATE INDEX idx_questions_interview ON questions(interview_id);
CREATE INDEX idx_questions_score ON questions(score);

-- ============= NOTIFICATIONS =============
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interview_id INTEGER REFERENCES interviews(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- ============= PREDEFINED DATA =============

-- Insert Sample Domains
INSERT INTO domains (name, description) VALUES
('Data Science', 'Data analysis, machine learning, and statistical modeling'),
('Web Development', 'Frontend, backend, and full-stack web development'),
('Machine Learning', 'Advanced ML algorithms and AI/ML engineering'),
('Software Engineering', 'Core software development and architecture'),
('Cybersecurity', 'Security analysis and penetration testing'),
('Cloud Computing', 'Cloud platforms and infrastructure management'),
('Mobile Development', 'iOS, Android, and cross-platform development'),
('Game Development', 'Game engines and interactive media'),
('Blockchain', 'Cryptocurrency and distributed ledger technology'),
('AI/NLP', 'Natural language processing and AI systems'),
('Database', 'Database design, optimization, and administration'),
('DevOps', 'Infrastructure automation and CI/CD pipelines')
ON CONFLICT (name) DO NOTHING;

-- Insert Sample Roles for Data Science
INSERT INTO roles (name, description, domain_id) VALUES
('Data Scientist', 'Expert in statistical analysis and ML algorithms',
    (SELECT id FROM domains WHERE name = 'Data Science')),
('Data Analyst', 'Specialized in data analysis and visualization',
    (SELECT id FROM domains WHERE name = 'Data Science')),
('Machine Learning Engineer', 'Focused on ML model development and deployment',
    (SELECT id FROM domains WHERE name = 'Data Science'))
ON CONFLICT (domain_id, name) DO NOTHING;

-- Insert Sample Roles for Web Development
INSERT INTO roles (name, description, domain_id) VALUES
('Frontend Developer', 'Expert in React, Vue, Angular, and UI/UX',
    (SELECT id FROM domains WHERE name = 'Web Development')),
('Backend Developer', 'Specialized in APIs, databases, and server architecture',
    (SELECT id FROM domains WHERE name = 'Web Development')),
('Full Stack Developer', 'Proficient in both frontend and backend technologies',
    (SELECT id FROM domains WHERE name = 'Web Development'))
ON CONFLICT (domain_id, name) DO NOTHING;

-- Insert Sample Roles for Cloud Computing
INSERT INTO roles (name, description, domain_id) VALUES
('Cloud Architect', 'Design cloud infrastructure and solutions',
    (SELECT id FROM domains WHERE name = 'Cloud Computing')),
('AWS Developer', 'Specialized AWS implementation and management',
    (SELECT id FROM domains WHERE name = 'Cloud Computing')),
('Cloud Engineer', 'Infrastructure automation and cloud operations',
    (SELECT id FROM domains WHERE name = 'Cloud Computing'))
ON CONFLICT (domain_id, name) DO NOTHING;

-- Create a test candidate user (optional)
-- Password: TestPassword123 (hashed with bcrypt)
-- INSERT INTO users (email, username, hashed_password, full_name, role, is_active)
-- VALUES ('candidate@test.com', 'testcandidate', '$2b$12$hash_here', 'Test Candidate', 'candidate', TRUE);

-- Create a test interviewer user (optional)
-- INSERT INTO users (email, username, hashed_password, full_name, role, is_active)
-- VALUES ('interviewer@test.com', 'testinterviewer', '$2b$12$hash_here', 'Test Interviewer', 'interviewer', TRUE);
