-- ============================================================
--  CAMPUS TALENT MANAGEMENT SYSTEM — Full MySQL Setup Script
--  Run this entire file in MySQL Workbench or phpMyAdmin
--  or via terminal: mysql -u root -p < setup.sql
-- ============================================================

-- 1. CREATE & SELECT DATABASE
CREATE DATABASE IF NOT EXISTS campusprojectdb;
USE campusprojectdb;

-- ============================================================
-- 2. DROP TABLES (in safe order — child tables first)
-- ============================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Task_Allocation;
DROP TABLE IF EXISTS Skill_Endorsements;
DROP TABLE IF EXISTS Project_Reviews;
DROP TABLE IF EXISTS Project_Members;
DROP TABLE IF EXISTS Project_Requirements;
DROP TABLE IF EXISTS Milestones;
DROP TABLE IF EXISTS StudentSkills;
DROP TABLE IF EXISTS Projects;
DROP TABLE IF EXISTS Skills;
DROP TABLE IF EXISTS Students;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 3. CREATE TABLES
-- ============================================================

-- STUDENTS
CREATE TABLE Students (
    StudentID   INT AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(200) NOT NULL,
    Department  VARCHAR(100) NOT NULL,
    Year        INT NOT NULL CHECK (Year BETWEEN 1 AND 4),
    Email       VARCHAR(200) DEFAULT ''
);

-- SKILLS
CREATE TABLE Skills (
    SkillID     INT AUTO_INCREMENT PRIMARY KEY,
    SkillName   VARCHAR(150) NOT NULL UNIQUE,
    Category    VARCHAR(80)  DEFAULT 'Other',
    Difficulty  VARCHAR(50)  DEFAULT 'Medium',
    Description VARCHAR(255) DEFAULT ''
);

-- PROJECTS
CREATE TABLE Projects (
    ProjectID   INT AUTO_INCREMENT PRIMARY KEY,
    Title       VARCHAR(200) NOT NULL,
    Description TEXT,
    Status      VARCHAR(50)  DEFAULT 'Planning',
    StartDate   DATE,
    EndDate     DATE
);

-- STUDENT_SKILLS  (bridge: Students <-> Skills)
CREATE TABLE StudentSkills (
    StudentID   INT NOT NULL,
    SkillID     INT NOT NULL,
    Proficiency VARCHAR(50) DEFAULT 'Beginner',
    PRIMARY KEY (StudentID, SkillID),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (SkillID)   REFERENCES Skills(SkillID)
);

-- PROJECT_REQUIREMENTS  (bridge: Projects <-> Skills)
CREATE TABLE Project_Requirements (
    ProjectID  INT NOT NULL,
    SkillID    INT NOT NULL,
    Importance VARCHAR(50) DEFAULT 'Required',
    PRIMARY KEY (ProjectID, SkillID),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
    FOREIGN KEY (SkillID)   REFERENCES Skills(SkillID)
);

-- PROJECT_MEMBERS  (bridge: Projects <-> Students)
CREATE TABLE Project_Members (
    ProjectID  INT NOT NULL,
    StudentID  INT NOT NULL,
    Role       VARCHAR(100) DEFAULT 'Member',
    JoinedDate DATE,
    PRIMARY KEY (ProjectID, StudentID),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
);

-- MILESTONES
CREATE TABLE Milestones (
    MilestoneID INT AUTO_INCREMENT PRIMARY KEY,
    ProjectID   INT NOT NULL,
    Title       VARCHAR(200) NOT NULL,
    Deadline    DATE,
    Status      VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
);

-- TASK_ALLOCATION
CREATE TABLE Task_Allocation (
    TaskID      INT AUTO_INCREMENT PRIMARY KEY,
    MilestoneID INT NOT NULL,
    StudentID   INT NOT NULL,
    TaskName    VARCHAR(200) NOT NULL,
    TaskStatus  VARCHAR(50)  DEFAULT 'To Do',
    FOREIGN KEY (MilestoneID) REFERENCES Milestones(MilestoneID),
    FOREIGN KEY (StudentID)   REFERENCES Students(StudentID)
);

-- SKILL_ENDORSEMENTS
CREATE TABLE Skill_Endorsements (
    EndorsementID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID     INT NOT NULL,
    SkillID       INT NOT NULL,
    EndorserID    INT NOT NULL,
    EndorsedDate  DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (StudentID)  REFERENCES Students(StudentID),
    FOREIGN KEY (SkillID)    REFERENCES Skills(SkillID),
    FOREIGN KEY (EndorserID) REFERENCES Students(StudentID)
);

-- PROJECT_REVIEWS
CREATE TABLE Project_Reviews (
    ReviewID     INT AUTO_INCREMENT PRIMARY KEY,
    ProjectID    INT NOT NULL,
    ReviewerName VARCHAR(200),
    Rating       INT CHECK (Rating BETWEEN 1 AND 5),
    Comments     TEXT,
    ReviewDate   DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
);

-- ============================================================
-- 4. SEED DATA — Skills
-- ============================================================
INSERT INTO Skills (SkillName, Category, Difficulty, Description) VALUES
('Python',           'Programming', 'Easy',   'General-purpose scripting and data science'),
('Java',             'Programming', 'Medium',  'Object-oriented enterprise language'),
('JavaScript',       'Programming', 'Medium',  'Web scripting and Node.js'),
('C++',              'Programming', 'Hard',    'Systems and competitive programming'),
('Embedded C',       'Hardware',    'Hard',    'Low-level microcontroller programming'),
('Machine Learning', 'Programming', 'Hard',    'ML algorithms and modelling'),
('Deep Learning',    'Programming', 'Hard',    'Neural networks and AI'),
('React',            'Framework',   'Medium',  'UI library for web applications'),
('Node.js',          'Framework',   'Medium',  'Server-side JavaScript runtime'),
('TensorFlow',       'Framework',   'Hard',    'ML framework by Google'),
('Spring Boot',      'Framework',   'Hard',    'Java web application framework'),
('SQL',              'Database',    'Easy',    'Relational database queries'),
('MySQL',            'Database',    'Easy',    'Open-source relational database'),
('MongoDB',          'Database',    'Medium',  'NoSQL document database'),
('SolidWorks',       'Design',      'Medium',  '3D CAD modelling software'),
('AutoCAD',          'Design',      'Medium',  '2D and 3D CAD design'),
('Figma',            'Design',      'Easy',    'UI/UX prototyping tool'),
('Cybersecurity',    'Other',       'Hard',    'Network security and ethical hacking'),
('Docker',           'Other',       'Medium',  'Container platform'),
('VLSI',             'Hardware',    'Hard',    'Very large scale integration design'),
('Arduino',          'Hardware',    'Easy',    'Microcontroller prototyping'),
('MATLAB',           'Hardware',    'Medium',  'Numerical computing environment');

-- ============================================================
-- 5. SEED DATA — Students
-- ============================================================
INSERT INTO Students (Name, Department, Year, Email) VALUES
('Arjun Menon',      'AI/ML',       2, 'arjun@campus.edu'),
('Priya Nair',       'CS',          3, 'priya@campus.edu'),
('Rahul Sharma',     'IT',          1, 'rahul@campus.edu'),
('Anjali Krishnan',  'AI/ML',       4, 'anjali@campus.edu'),
('Kiran Pillai',     'EC',          2, 'kiran@campus.edu'),
('Deepak Mohan',     'CS',          3, 'deepak@campus.edu'),
('Sneha Varma',      'Mechanical',  2, 'sneha@campus.edu'),
('Vishnu Raj',       'IT',          4, 'vishnu@campus.edu'),
('Meera Suresh',     'CS',          1, 'meera@campus.edu'),
('Arun Kumar',       'AI/ML',       3, 'arun@campus.edu'),
('Neethu George',    'IT',          2, 'neethu@campus.edu'),
('Sanjay Pillai',    'EC',          3, 'sanjay@campus.edu'),
('Lakshmi Rao',      'CS',          4, 'lakshmi@campus.edu'),
('Rohit Das',        'AI/ML',       1, 'rohit@campus.edu'),
('Divya Menon',      'Mechanical',  3, 'divya@campus.edu');

-- ============================================================
-- 6. SEED DATA — StudentSkills
-- ============================================================
INSERT INTO StudentSkills (StudentID, SkillID, Proficiency) VALUES
(1,  1,  'Advanced'),     -- Arjun: Python
(1,  10, 'Intermediate'), -- Arjun: TensorFlow
(2,  8,  'Intermediate'), -- Priya: React
(2,  9,  'Beginner'),     -- Priya: Node.js
(3,  12, 'Beginner'),     -- Rahul: SQL
(3,  13, 'Beginner'),     -- Rahul: MySQL
(4,  6,  'Advanced'),     -- Anjali: Machine Learning
(4,  7,  'Advanced'),     -- Anjali: Deep Learning
(5,  5,  'Intermediate'), -- Kiran: Embedded C
(5,  21, 'Intermediate'), -- Kiran: Arduino
(6,  2,  'Advanced'),     -- Deepak: Java
(6,  11, 'Intermediate'), -- Deepak: Spring Boot
(7,  15, 'Intermediate'), -- Sneha: SolidWorks
(7,  16, 'Beginner'),     -- Sneha: AutoCAD
(8,  18, 'Advanced'),     -- Vishnu: Cybersecurity
(9,  1,  'Beginner'),     -- Meera: Python
(10, 7,  'Advanced'),     -- Arun: Deep Learning
(10, 6,  'Advanced'),     -- Arun: Machine Learning
(11, 3,  'Intermediate'), -- Neethu: JavaScript
(11, 8,  'Beginner'),     -- Neethu: React
(12, 20, 'Advanced'),     -- Sanjay: VLSI
(13, 3,  'Advanced'),     -- Lakshmi: JavaScript
(13, 9,  'Advanced'),     -- Lakshmi: Node.js
(14, 1,  'Beginner'),     -- Rohit: Python
(15, 15, 'Advanced'),     -- Divya: SolidWorks
(15, 16, 'Intermediate'); -- Divya: AutoCAD

-- ============================================================
-- 7. SEED DATA — Projects
-- ============================================================
INSERT INTO Projects (Title, Description, Status, StartDate, EndDate) VALUES
('Smart Campus AI',        'AI-powered campus navigation and resource management system', 'Active',    '2025-01-10', '2025-06-30'),
('EcoTrack IoT',           'IoT-based environmental monitoring for campus sustainability',  'Active',    '2025-02-01', '2025-07-31'),
('Campus Portal Redesign', 'Full redesign of the student web portal using modern stack',    'Planning',  '2025-04-01', '2025-09-01'),
('VLSI Research Tool',     'Simulation tool for VLSI circuit design and analysis',          'Completed', '2024-08-01', '2025-01-15'),
('CyberSec Lab',           'Hands-on ethical hacking and network security training lab',    'On Hold',   '2025-03-01', '2025-12-31');

-- ============================================================
-- 8. SEED DATA — Project_Requirements
-- ============================================================
INSERT INTO Project_Requirements (ProjectID, SkillID, Importance) VALUES
(1, 6,  'Required'),   -- Smart Campus AI: Machine Learning
(1, 7,  'Required'),   -- Smart Campus AI: Deep Learning
(1, 1,  'Required'),   -- Smart Campus AI: Python
(2, 5,  'Required'),   -- EcoTrack IoT: Embedded C
(2, 21, 'Required'),   -- EcoTrack IoT: Arduino
(2, 12, 'Nice to have'),
(3, 8,  'Required'),   -- Portal: React
(3, 9,  'Required'),   -- Portal: Node.js
(3, 17, 'Nice to have'),
(4, 20, 'Required'),   -- VLSI Tool: VLSI
(4, 4,  'Nice to have'),
(5, 18, 'Required'),   -- CyberSec: Cybersecurity
(5, 19, 'Nice to have');

-- ============================================================
-- 9. SEED DATA — Project_Members
-- ============================================================
INSERT INTO Project_Members (ProjectID, StudentID, Role, JoinedDate) VALUES
(1, 1,  'Lead Developer', '2025-01-10'),
(1, 4,  'ML Engineer',    '2025-01-10'),
(1, 10, 'ML Engineer',    '2025-01-15'),
(2, 5,  'IoT Developer',  '2025-02-01'),
(2, 3,  'Data Analyst',   '2025-02-05'),
(3, 2,  'Frontend Dev',   '2025-04-01'),
(3, 11, 'Frontend Dev',   '2025-04-01'),
(3, 13, 'Backend Dev',    '2025-04-02'),
(4, 12, 'Lead',           '2024-08-01'),
(5, 8,  'Lead',           '2025-03-01');

-- ============================================================
-- 10. SEED DATA — Milestones
-- ============================================================
INSERT INTO Milestones (ProjectID, Title, Deadline, Status) VALUES
(1, 'Data Collection & Preprocessing', '2025-02-28', 'Completed'),
(1, 'Model Training & Validation',     '2025-04-15', 'In Progress'),
(1, 'API Integration & Testing',       '2025-05-30', 'Pending'),
(1, 'Deployment & Demo',               '2025-06-30', 'Pending'),
(2, 'Sensor Hardware Setup',           '2025-03-01', 'Completed'),
(2, 'Firmware Development',            '2025-05-01', 'In Progress'),
(2, 'Dashboard Development',           '2025-06-15', 'Pending'),
(3, 'UI/UX Wireframes',                '2025-04-20', 'Pending'),
(3, 'Frontend Implementation',         '2025-06-30', 'Pending'),
(3, 'Backend API Development',         '2025-07-31', 'Pending');

-- ============================================================
-- 11. SEED DATA — Task_Allocation
-- ============================================================
INSERT INTO Task_Allocation (MilestoneID, StudentID, TaskName, TaskStatus) VALUES
(1, 1,  'Collect and clean training dataset',   'Done'),
(1, 4,  'Feature engineering pipeline',          'Done'),
(2, 1,  'Train ResNet model on campus data',    'In Progress'),
(2, 10, 'Hyperparameter tuning',                 'In Progress'),
(2, 4,  'Model evaluation metrics',              'To Do'),
(3, 1,  'Build REST API endpoints',             'To Do'),
(3, 10, 'Write API unit tests',                  'To Do'),
(5, 5,  'Assemble sensor nodes',                'Done'),
(5, 3,  'Configure MQTT broker',                'Done'),
(6, 5,  'Write firmware for temperature sensor','In Progress'),
(7, 3,  'Build real-time dashboard',            'To Do'),
(8, 2,  'Create Figma wireframes',              'To Do'),
(9, 2,  'Implement homepage and login page',    'To Do'),
(9, 11, 'Build dashboard components',           'To Do'),
(10, 13,'Set up Express.js server',             'To Do');

-- ============================================================
-- 12. SEED DATA — Skill_Endorsements
-- ============================================================
INSERT INTO Skill_Endorsements (StudentID, SkillID, EndorserID, EndorsedDate) VALUES
(1,  1,  4,  '2025-01-20'),  -- Anjali endorses Arjun for Python
(1,  6,  10, '2025-02-10'),  -- Arun endorses Arjun for ML
(4,  6,  1,  '2025-02-12'),  -- Arjun endorses Anjali for ML
(4,  7,  10, '2025-03-01'),  -- Arun endorses Anjali for Deep Learning
(8,  18, 6,  '2025-01-30'),  -- Deepak endorses Vishnu for Cybersecurity
(12, 20, 5,  '2025-02-05'),  -- Kiran endorses Sanjay for VLSI
(2,  8,  11, '2025-04-02'),  -- Neethu endorses Priya for React
(13, 3,  2,  '2025-04-05'),  -- Priya endorses Lakshmi for JavaScript
(6,  2,  13, '2025-03-15'),  -- Lakshmi endorses Deepak for Java
(10, 7,  4,  '2025-03-20');  -- Anjali endorses Arun for Deep Learning

-- ============================================================
-- 13. SEED DATA — Project_Reviews
-- ============================================================
INSERT INTO Project_Reviews (ProjectID, ReviewerName, Rating, Comments, ReviewDate) VALUES
(4, 'Dr. Ramesh Kumar',   5, 'Excellent simulation accuracy and clean code architecture. Outstanding final result.',       '2025-01-20'),
(4, 'Prof. Anita Sharma', 4, 'Very solid project. Documentation could be more detailed but the core work is impressive.', '2025-01-22'),
(1, 'Dr. Suresh Pillai',  4, 'Great progress so far. ML pipeline is well-structured. Awaiting final deployment.',         '2025-03-10'),
(2, 'Prof. Meena Rajan',  3, 'Good hardware setup. Software side needs more work on data visualisation.',                 '2025-03-15'),
(5, 'Dr. Anil Nair',      2, 'Project is on hold due to lab access issues. Needs restructuring before continuation.',     '2025-03-20');

-- ============================================================
-- DONE! Verify with:
-- SELECT * FROM Students;
-- SELECT * FROM Skills;
-- SELECT * FROM Projects;
-- SELECT * FROM Project_Members;
-- SELECT * FROM Task_Allocation;
-- ============================================================
