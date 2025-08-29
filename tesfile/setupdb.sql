-- 1. Create Database
CREATE DATABASE timetable;
USE timetable;

-- 2. Create Tables

-- Table Faculties
CREATE TABLE Faculties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Table Departments
CREATE TABLE Departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Faculties_id INT,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (Faculties_id) REFERENCES Faculties(id)
);

-- Table Majors
CREATE TABLE Majors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Departments_id INT,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (Departments_id) REFERENCES Departments(id)
);





-- Table Teachers
CREATE TABLE Teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

ALTER TABLE Teachers
ADD COLUMN role ENUM('admin', 'simple') NOT NULL DEFAULT 'simple';



-- Table Subjects
CREATE TABLE Subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Table Teacher_Subjects (Many-to-Many relationship between Teachers and Subjects)
CREATE TABLE teacher_subjects (
    teacher_id INT,
    subject_id INT,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(id),
    PRIMARY KEY (teacher_id, subject_id)
);


--new table
CREATE TABLE teacher_teaching_time (
    teacher_id INT,
    study_sessions_id INT,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
    FOREIGN KEY (study_sessions_id) REFERENCES study_sessions(id),
    PRIMARY KEY (teacher_id, study_sessions_id)
);



ALTER TABLE Teachers 
ADD COLUMN number_sessions INT DEFAULT 0;

--ALTER TABLE Teachers ADD COLUMN profile_img VARCHAR(255);


-- Table Rooms
CREATE TABLE Rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL,
    capacity INT,
    floor VARCHAR(10),
    room_type ENUM('Laboratory', 'Lecture Hall', 'Classroom') DEFAULT 'Classroom'
);

-- Table Study_Sessions
CREATE TABLE study_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name ENUM(
        'Monday-Friday Morning',
        'Monday-Friday Afternoon',
        'Monday-Friday Evening',
        'Saturday-Sunday'
    ) NOT NULL,
    sessions_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    session_time_start TIME,
    session_time_end TIME
);

-- Table Students
CREATE TABLE Students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    date_joined DATE,
    major_id INT,
    generation INT,
    batch INT,
    group_student INT,
    FOREIGN KEY (major_id) REFERENCES Majors(id)
);
ALTER TABLE Students
ADD COLUMN shift_name ENUM(
    'Monday-Friday Morning',
    'Monday-Friday Afternoon',
    'Monday-Friday Evening',
    'Saturday-Sunday'
) NOT NULL;

-- Table Timetable
CREATE TABLE Timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    note VARCHAR(255),
    study_sessions_id INT,
    group_student INT,
    batch INT,
    generation INT,
    major_id INT,
    teacher_id INT,
    subject_id INT,
    room_id INT,
    FOREIGN KEY (study_sessions_id) REFERENCES study_sessions(id),
    FOREIGN KEY (major_id) REFERENCES Majors(id),
    FOREIGN KEY (teacher_id, subject_id) REFERENCES teacher_subjects(teacher_id, subject_id),
    FOREIGN KEY (room_id) REFERENCES Rooms(id)
);

ALTER TABLE Timetable
ADD years INT NOT NULL,
ADD Semester INT NOT NULL;
-- 3. Insert Data Example

-- Insert Faculties
INSERT INTO Faculties (name) VALUES
('មហាវិទ្យាល័យគ្រប់គ្រងពាណិជ្ជកម្ម និងទេសចរណ៍'),
('មហាវិទ្យាល័យវិស្វកម្ម'),
('មហាវិទ្យាល័យវិទ្យាសាស្ត្រ');

-- Insert Departments
INSERT INTO Departments (Faculties_id, name) VALUES
(1, 'ដេប៉ាតឺម៉ង់គ្រប់គ្រងជំនាញ'),
(1, 'ដេប៉ាតឺម៉ង់គ្រប់គ្រងទេសចរណ៍'),
(2, 'ដេប៉ាតឺម៉ង់វិស្វកម្មស៊ីវិល');

-- Insert Majors
INSERT INTO Majors (Departments_id, name) VALUES
(1, 'សហគ្រិនភាព និងធុរកិច្ច'),
(2, 'គ្រប់គ្រងទេសចរណ៍ និងបដិសណ្ឋារកិច្ច'),
(1, 'ទីផ្សារ');

-- Insert Teachers
INSERT INTO Teachers (username, name, password) VALUES
('teacher1', 'លោក យឿង សុថន', 'password123'),
('teacher2', 'លោកស្រី មុយ សុខឡែន', 'password123'),
('teacher3', 'លោក សំ ប៊ុនធឿន', 'password123');

-- Insert Subjects
INSERT INTO Subjects (name) VALUES
('ការណែនាំទៅកាន់ទេសចរណ៍'),
('មូលដ្ឋានគ្រប់គ្រង'),
('សេដ្ឋកិច្ចតូច'),
('ច្បាប់ទេសចរណ៍ និងបដិសណ្ឋារកិច្ច');

-- Insert Teacher_Subjects
INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES
(1, 1),  -- លោក យឿង សុថន បង្រៀនការណែនាំទៅកាន់ទេសចរណ៍
(2, 2),  -- លោកស្រី មុយ សុខឡែន បង្រៀនមូលដ្ឋានគ្រប់គ្រង
(3, 3);  -- លោក សំ ប៊ុនធឿន បង្រៀនសេដ្ឋកិច្ចតូច

-- Insert Rooms
INSERT INTO Rooms (room_number, capacity, floor, room_type) VALUES
('A7', 40, 'ជាន់ទី១', 'Classroom'),
('D5+6', 80, 'ជាន់ទី២', 'Lecture Hall'),
('C6', 30, 'ជាន់ទី៣', 'Classroom');

-- Insert Study_Sessions
INSERT INTO study_sessions (shift_name, sessions_day, session_time_start, session_time_end) VALUES
('Monday-Friday Morning', 'Monday', '07:30:00', '09:00:00'),
('Monday-Friday Morning', 'Tuesday', '07:30:00', '09:00:00'),
('Saturday-Sunday', 'Saturday', '07:30:00', '09:00:00');

-- Insert Students
INSERT INTO Students (username, name, password, date_joined, major_id, generation, batch, group_student) VALUES
('student1', 'John Doe', 'password123', '2023-01-01', 1, 2023, 1, 101),
('student2', 'Jane Smith', 'password123', '2023-01-01', 2, 2023, 1, 102);

-- Insert Timetable
INSERT INTO Timetable (note, study_sessions_id, group_student, batch, generation, major_id, teacher_id, subject_id, room_id) VALUES
('ការណែនាំទៅកាន់ទេសចរណ៍', 1, 101, 1, 2023, 1, 1, 1, 1),
('មូលដ្ឋានគ្រប់គ្រង', 2, 101, 1, 2023, 1, 2, 2, 2),
('សេដ្ឋកិច្ចតូច', 3, 102, 1, 2023, 2, 3, 3, 3);










 Required Libraries:
 requirements.txt

 pip freeze > requirements.txt

 source env/bin/activate




1. ការត្រួតពិនិត្យវេនសិក្សា (Study Shifts)
វេនសិក្សា គឺជាផ្នែកដែលមានការសំរេចពីម៉ោងនៃការសិក្សា។ ដើម្បីបញ្ចៀសការស្ទួន វេនសិក្សាត្រូវត្រូវត្រូវត្រូវត្រួតពិនិត្យថាការបែងចែកវេនសិក្សា (Study Shift) ទៅកាន់កាលវិភាគគ្នាត្រូវត្រឹមត្រូវ និងតម្រូវឲ្យម៉ោងនៃវេនត្រូវតែពាក់ព័ន្ធដោយស្មើ។

គោលការណ៍: ត្រូវការត្រួតពិនិត្យថា សិស្សមួយគ្រប់គ្រងសិក្សានៅលើម៉ោងដែលខុសគ្នា ហើយអាចបង្ហាញជាលីសវេនផ្សេងៗបាន។

អនុវត្ត: ការអនុវត្ត shift_name មិនអាចប្រើជាមួយពេលវេលាដូចគ្នានៅក្នុង study_sessions ។ ឧ. វេនសិក្សា Monday-Friday Morning មិនអាចស្គាល់ពេលវេលាជាមួយសកម្មភាពផងដែរ។

2. ការត្រួតពិនិត្យបន្ទប់ (Rooms)
បន្ទប់មិនអាចប្រើសម្រាប់មុខវិជ្ជា (subject) ឬក្រុមសិស្ស (group) ផ្សេងៗក្នុងម៉ោងដូចគ្នា។

គោលការណ៍: ត្រូវតែធានាថាបន្ទប់មួយមិនមានការប្រើប្រាស់ពីការរៀនមុខវិជ្ជា ឬក្រុមសិស្សផ្សេងៗក្នុងម៉ោងដូចគ្នា។

អនុវត្ត: ចូរត្រួតពិនិត្យថាក្រុមសិស្សឬមុខវិជ្ជា ត្រូវបានកំណត់សម្រាប់តម្លៃម៉ោងដែលទទួលបានត្រួតពិនិត្យនៅលើបន្ទប់ជាមួយមុខវិជ្ជាផ្សេងៗ។

កូដខាងលើអាចត្រួតពិនិត្យការប្រើប្រាស់បន្ទប់ក្នុងម៉ោងជាក់លាក់។

3. ការត្រួតពិនិត្យគ្រូបង្រៀន (Teachers)
គ្រូម្នាក់មិនអាចបង្រៀនមុខវិជ្ជាជាច្រើនក្នុងម៉ោងដូចគ្នា។

គោលការណ៍: គ្រូម្នាក់មិនអាចបង្រៀនក្នុងពេលវេលាដូចគ្នា ឬបញ្ចូលនៅក្នុងការបណ្តុះបណ្តាលមុខវិជ្ជាផ្សេងៗ។

អនុវត្ត: សូមត្រួតពិនិត្យការប្រើប្រាស់គ្រូក្នុងវេលាជាក់លាក់ដោយអនុវត្តកូដដូចខាងក្រោម៖


ប្រសិនបើមានការផ្គូរផ្គងវេនបង្រៀន នៅក្នុងម៉ោងដូចគ្នា នោះគួរត្រូវដកស្រង់ការកំណត់បញ្ចូលចេញ។

4. ការត្រួតពិនិត្យក្រុមសិស្ស (Groups)
ក្រុមសិស្សមិនអាចមានមុខវិជ្ជាផ្សេងៗក្នុងម៉ោងដូចគ្នា។

គោលការណ៍: ក្រុមសិស្សមួយទទួលបានតែម៉ោងសិក្សាក្នុងមុខវិជ្ជាមួយបន្ទប់នោះម្តងទេ។

អនុវត្ត: ត្រូវត្រួតពិនិត្យថាក្រុមសិស្សមួយត្រូវបានអនុញ្ញាតឲ្យមានមុខវិជ្ជាក្នុងម៉ោងដែលទទួលបានត្រឹមត្រូវ។

សង្ខេប
Study Shifts: ត្រួតពិនិត្យការបែងចែកម៉ោងសិក្សាឲ្យត្រឹមត្រូវ។
Rooms: បន្ទប់មិនអាចប្រើសម្រាប់មុខវិជ្ជា និងក្រុមសិស្សក្នុងម៉ោងដូចគ្នា។
Teachers: គ្រូម្នាក់មិនអាចបង្រៀននៅក្នុងម៉ោងដូចគ្នាប្រសិនបើបង្រៀនមុខវិជ្ជាជាច្រើន។
Groups: ក្រុមសិស្សមិនអាចមានមុខវិជ្ជាផ្សេងៗក្នុងម៉ោងដូចគ្នា។
ចំពោះការអនុវត្តន៍ក្នុងការបង្កើតកាលវិភាគ សូមបញ្ចាក់នូវការប្រើប្រាស់ Foreign Keys និងការត្រួតពិនិត្យនៅក្នុងសំនួរពាក់ព័ន្ធដូចខាងលើដើម្បីកុំមានការស្ទួនដែលអាចបញ្ចេញបញ្ហានៅពេលដំណើរការបញ្ចូល!
