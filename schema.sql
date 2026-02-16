-- Student Marks Table Schema (matches Excel file structure)
-- Table: student_marks

CREATE TABLE IF NOT EXISTS student_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year VARCHAR(20) DEFAULT '2023-2024',
    subject VARCHAR(100) DEFAULT 'PDSM',
    s_no INTEGER,
    regd_no VARCHAR(20),
    name VARCHAR(200),
    
    -- MID I marks - M1Q1a, M1Q1b, M1Q2a, M1Q2b, M1Q3a, M1Q3b, M1Qu1, M1A1
    m1q1a REAL,
    m1q1b REAL,
    m1q2a REAL,
    m1q2b REAL,
    m1q3a REAL,
    m1q3b REAL,
    m1qu1 REAL,
    m1a1 REAL,
    
    -- MID II marks - M2Q1a, M2Q1b, M2Q2a, M2Q2b, M2Q3a, M2Q3b, M2Qu2, M2A2
    m2q1a REAL,
    m2q1b REAL,
    m2q2a REAL,
    m2q2b REAL,
    m2q3a REAL,
    m2q3b REAL,
    m2qu2 REAL,
    m2a2 REAL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_student_marks_regd ON student_marks(regd_no);
CREATE INDEX IF NOT EXISTS idx_student_marks_name ON student_marks(name);
CREATE INDEX IF NOT EXISTS idx_student_marks_subject ON student_marks(subject);
