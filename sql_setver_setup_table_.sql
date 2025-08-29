
use-- Create Database
CREATE DATABASE SchoolDB;
GO

-- Switch to database
USE SchoolDB;
GO

--1  Faculties
CREATE TABLE Faculties (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL
);

--2 Departments
CREATE TABLE Departments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    Faculties_id INT NULL,
    name NVARCHAR(255) NOT NULL,
    CONSTRAINT FK_Departments_Faculties FOREIGN KEY (Faculties_id)
    REFERENCES Faculties(id)
);

--3 Majors
CREATE TABLE Majors (
    id INT IDENTITY(1,1) PRIMARY KEY,
    Departments_id INT NULL,
    name NVARCHAR(255) NOT NULL,
    CONSTRAINT FK_Majors_Departments FOREIGN KEY (Departments_id)
    REFERENCES Departments(id)
);

--4 Rooms
CREATE TABLE Rooms (
    id INT IDENTITY(1,1) PRIMARY KEY,
    room_number NVARCHAR(20) NOT NULL,
    capacity INT NULL,
    floor NVARCHAR(10) NULL,
    room_type NVARCHAR(50) NOT NULL 
    CONSTRAINT CK_RoomType CHECK (room_type IN ('Laboratory','Lecture Hall','Classroom','Computer'))
);

--5 Exams      -- new 
CREATE TABLE Exams (
    id INT IDENTITY(1,1) PRIMARY KEY,
    date DATE NULL,
    name NVARCHAR(100) NOT NULL,
    year INT NULL,
    semester NVARCHAR(50) NULL
);

--6  Score Types  --new
CREATE TABLE Score_Types (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL,
    max_score DECIMAL(5,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL
);




--7 Teachers 
CREATE TABLE Teachers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL,
    name NVARCHAR(255) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL 
    CONSTRAINT CK_TeacherRole CHECK (role IN ('admin','simple')),
    number_sessions INT DEFAULT 0
);

--8 Students 
CREATE TABLE Students (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL,
    name NVARCHAR(255) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    date_joined DATE NULL,
    major_id INT NULL,
    generation INT NULL,
    batch INT NULL,
    group_student INT NULL,
    shift_name NVARCHAR(50) NOT NULL
    CONSTRAINT CK_ShiftName CHECK (shift_name IN ('Monday-Friday Morning','Monday-Friday Afternoon','Monday-Friday Evening','Saturday-Sunday')),
    CONSTRAINT FK_Students_Majors FOREIGN KEY (major_id) REFERENCES Majors(id)
);

--9  Student Info 
CREATE TABLE Student_Info (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL,
    gender NVARCHAR(10) NULL 
    CONSTRAINT CK_StudentGender CHECK (gender IN ('Male','Female','Other')),
    date_of_birth DATE NULL,
    nationality NVARCHAR(100) NULL,
    profile_photo NVARCHAR(255) NULL,
    phone_number NVARCHAR(20) NULL,
    email NVARCHAR(255) NULL,
    address NVARCHAR(MAX) NULL,
    guardian_name NVARCHAR(255) NULL,
    guardian_phone NVARCHAR(20) NULL,
    guardian_relation NVARCHAR(100) NULL,
    enrollment_status NVARCHAR(20) DEFAULT 'Active'
        CONSTRAINT CK_EnrollStatus CHECK (enrollment_status IN ('Active','Inactive','Graduated','Dropped')),
    scholarship_status NVARCHAR(20) DEFAULT 'None'
        CONSTRAINT CK_Scholarship CHECK (scholarship_status IN ('None','Partial','Full')),
    enrollment_date DATE NULL,
    graduation_date DATE NULL,
    notes NVARCHAR(MAX) NULL,
    CONSTRAINT FK_StudentInfo_Students FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE
);

--10  Study Sessions
CREATE TABLE Study_Sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    shift_name NVARCHAR(50) NOT NULL
        CONSTRAINT CK_StudyShift CHECK (shift_name IN ('Monday-Friday Morning','Monday-Friday Afternoon','Monday-Friday Evening','Saturday-Sunday')),
    sessions_day NVARCHAR(20) NOT NULL
        CONSTRAINT CK_SessionDay CHECK (sessions_day IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')),
    session_time_start TIME NULL,
    session_time_end TIME NULL
);

--11  Subjects
CREATE TABLE Subjects (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    faculties_id INT NULL,
    batch INT NOT NULL DEFAULT 1,
    CONSTRAINT FK_Subjects_Faculties FOREIGN KEY (faculties_id) REFERENCES Faculties(id) ON DELETE CASCADE
);

--12  Teacher_Subjects
CREATE TABLE Teacher_Subjects (
    teacher_id INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (teacher_id, subject_id),
    CONSTRAINT FK_TeacherSubjects_Teachers FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
    CONSTRAINT FK_TeacherSubjects_Subjects FOREIGN KEY (subject_id) REFERENCES Subjects(id)
);

--13 Teacher_Teaching_Time
CREATE TABLE Teacher_Teaching_Time (
    teacher_id INT NOT NULL,
    study_sessions_id INT NOT NULL,
    PRIMARY KEY (teacher_id, study_sessions_id),
    CONSTRAINT FK_TeachingTime_Teachers FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
    CONSTRAINT FK_TeachingTime_StudySessions FOREIGN KEY (study_sessions_id) REFERENCES Study_Sessions(id)
);

--14 Scores new
CREATE TABLE Scores (
    id INT IDENTITY(1,1) PRIMARY KEY,
    exam_id INT NULL,
    type_id INT NULL,
    teacher_id INT NULL,
    subject_id INT NULL,
    student_id INT NULL,
    score DECIMAL(5,2) NULL,
    CONSTRAINT FK_Scores_Exams FOREIGN KEY (exam_id) REFERENCES Exams(id),
    CONSTRAINT FK_Scores_Types FOREIGN KEY (type_id) REFERENCES Score_Types(id),
    CONSTRAINT FK_Scores_Teachers FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
    CONSTRAINT FK_Scores_Subjects FOREIGN KEY (subject_id) REFERENCES Subjects(id),
    CONSTRAINT FK_Scores_Students FOREIGN KEY (student_id) REFERENCES Students(id)
);

-- 15 Timetable 
CREATE TABLE Timetable (
    id INT IDENTITY(1,1) PRIMARY KEY,
    note NVARCHAR(255) NULL,
    study_sessions_id INT NULL,
    group_student INT NULL,
    batch INT NULL,
    generation INT NULL,
    major_id INT NULL,
    teacher_id INT NULL,
    subject_id INT NULL,
    room_id INT NULL,
    years INT NOT NULL,
    semester INT NOT NULL,
    CONSTRAINT FK_Timetable_Sessions FOREIGN KEY (study_sessions_id) REFERENCES Study_Sessions(id),
    CONSTRAINT FK_Timetable_Majors FOREIGN KEY (major_id) REFERENCES Majors(id),
    CONSTRAINT FK_Timetable_Rooms FOREIGN KEY (room_id) REFERENCES Rooms(id),
    CONSTRAINT FK_Timetable_TeacherSubjects FOREIGN KEY (teacher_id, subject_id) 
    REFERENCES Teacher_Subjects(teacher_id, subject_id)
);