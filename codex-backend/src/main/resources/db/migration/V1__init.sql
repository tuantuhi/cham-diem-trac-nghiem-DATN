CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    provider VARCHAR(50) DEFAULT 'local',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE students (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    student_code VARCHAR(100) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    class_name VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE exams (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(255),
    exam_type VARCHAR(50) NOT NULL DEFAULT 'OMR_50',
    answer_key TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE answer_keys (
    id UUID PRIMARY KEY,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    exam_code VARCHAR(100),
    answers_json TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE submissions (
    id UUID PRIMARY KEY,
    exam_id UUID NOT NULL REFERENCES exams(id),
    student_id UUID NOT NULL REFERENCES students(id),
    exam_code VARCHAR(100),
    image_url VARCHAR(500),
    score DECIMAL(5, 2),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    content TEXT,
    submitted_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE grades (
    id UUID PRIMARY KEY,
    submission_id UUID NOT NULL UNIQUE REFERENCES submissions(id),
    score DECIMAL(5, 2) NOT NULL,
    feedback TEXT,
    graded_by UUID REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE results (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id),
    exam_id UUID NOT NULL REFERENCES exams(id),
    grade_id UUID UNIQUE REFERENCES grades(id),
    final_score DECIMAL(5, 2) NOT NULL,
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE grading_results (
    id UUID PRIMARY KEY,
    submission_id UUID NOT NULL REFERENCES submissions(id),
    detected_answers TEXT,
    correct_answers INT,
    wrong_answers INT,
    score DECIMAL(5, 2),
    raw_ai_response TEXT
);

CREATE TABLE received_files (
    id UUID PRIMARY KEY,
    sender_device_id VARCHAR(255),
    file_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    received_at TIMESTAMP
);
