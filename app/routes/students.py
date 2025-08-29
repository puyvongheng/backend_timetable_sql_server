from collections import defaultdict
from flask import Blueprint, jsonify, request
import mysql.connector
from config import get_db_connection
from collections import defaultdict
import pyodbc

students_bp = Blueprint('students', __name__, url_prefix='/api/students')


@students_bp.route('/exams', methods=['GET'])
def exams():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    

    try:
        sql = "SELECT * FROM exams"
        
    
        
        cursor.execute(sql)
        
        exams_data = cursor.fetchall()
        return jsonify({'exams': exams_data})
    
    except Exception as e:
        print(f"Error fetching exams: {e}")
        return jsonify({'error': 'Cannot fetch exams'}), 500

    finally:
        cursor.close()
        connection.close()
        
# GET /exams/<id> - fetch a specific exam by ID
@students_bp.route('/exams/<int:id>', methods=['GET']) 
def get_exam_by_id(id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM exams WHERE id = %s", (id,))
        exam = cursor.fetchone()

        if not exam:
            return jsonify({'error': 'Exam not found'}), 404

        return jsonify({'exam': exam})

    except Exception as e:
        print(f"Error fetching exam: {e}")
        return jsonify({'error': 'Cannot fetch exam'}), 500

    finally:
        cursor.close()
        connection.close()
        
        

@students_bp.route('/score_types', methods=['GET'])
def score_types():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM score_types"
        cursor.execute(sql)
        score_types = cursor.fetchall()
        return jsonify({'score_types': score_types})
    except Exception as e:
        print(f"Error fetching exams: {e}")
        return jsonify({'error': 'Cannot fetch exams'}), 500
    finally:
        cursor.close()
        connection.close()
        
        
        

@students_bp.route('/total_scores2', methods=['GET'])
def total_scores2():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get filters
    student_id = request.args.get('student_id', '')
    exam_id = request.args.get('exam_id', '')
    major_id = request.args.get('major_id', '')
    generation = request.args.get('generation', '')
    batch = request.args.get('batch', '')
    group_student = request.args.get('group_student', '')
    shift_name = request.args.get('shift_name', '')
    
    
    if not any([shift_name, group_student, batch, generation, major_id, exam_id]):
        return jsonify({"message": "Please select at least one filter (shift_name, group_student, batch, generation, major_id, or exam_id)."}), 400

    
    #------------------ Get total students ------------------
    student_count_sql = """
        SELECT COUNT(*) AS total_students
        FROM students
        WHERE 1 = 1
    """
    student_count_params = []

    if major_id:
        student_count_sql += " AND students.major_id = %s"
        student_count_params.append(major_id)
    if generation:
        student_count_sql += " AND students.generation = %s"
        student_count_params.append(generation)
    if batch:
        student_count_sql += " AND students.batch = %s"
        student_count_params.append(batch)
    if group_student:
        student_count_sql += " AND students.group_student = %s"
        student_count_params.append(group_student)
    if shift_name:
        student_count_sql += " AND students.shift_name = %s"
        student_count_params.append(shift_name)

    cursor.execute(student_count_sql, student_count_params)
    total_students = cursor.fetchone()["total_students"]
    print("Total Students: ", total_students)
    #------------------ End total students ------------------

    # Base SQL
    sql = """
        SELECT
            students.id AS student_id,
            students.name AS student_name,
            subjects.name AS subject_name,
            score_types.name AS score_type,
            SUM(COALESCE(scores.score, 0)) AS score_total
        FROM students
        LEFT JOIN scores ON students.id = scores.student_id
        LEFT JOIN subjects ON scores.subject_id = subjects.id
        LEFT JOIN exams ON scores.exam_id = exams.id
        LEFT JOIN score_types ON scores.type_id = score_types.id
        WHERE 1 = 1
    """
    params = []
    
  
    if exam_id:
        sql += " AND exams.id = %s"
        params.append(exam_id)
    if major_id:
        sql += " AND students.major_id = %s"
        params.append(major_id)
    if generation:
        sql += " AND students.generation = %s"
        params.append(generation)
    if batch:
        sql += " AND students.batch = %s"
        params.append(batch)
    if group_student:
        sql += " AND students.group_student = %s"
        params.append(group_student)
    if shift_name:
        sql += " AND students.shift_name = %s"
        params.append(shift_name)

    sql += """
        GROUP BY students.id, students.name, subjects.name, score_types.name
        ORDER BY students.name, subjects.name, score_types.name
    """

    cursor.execute(sql, params)
    rows = cursor.fetchall()
      #------------------ End score results ------------------
    

    
    
    


    student_results = defaultdict(lambda: {
        "subjects": [],
        "total_score": 0,
 })
    
    
    
    
    

    for row in rows:
        sid = row['student_id']
        student_name = row['student_name']
        subject_name = row['subject_name']
        score_type = row['score_type']
        score_total = row['score_total'] or 0


        student_results[sid]["student_name"] = student_name
     
        student_results[sid]["student_id"] = sid


        student_results[sid]["total_score"] += score_total

        # Find subject entry
        subject_entry = next(
            (s for s in student_results[sid]["subjects"] if s["subject_name"] == subject_name),
            None
        )

        if not subject_entry:
            subject_entry = {
                "subject_name": subject_name,
                "scores": []
            }
            student_results[sid]["subjects"].append(subject_entry)

        subject_entry["scores"].append({
            "score_type": score_type,
            "score_total": score_total,

        })

    # Sort and rank
    final = sorted(student_results.values(), key=lambda x: x["total_score"], reverse=True)
    for idx, student in enumerate(final, start=1):
        student['rank'] = idx

    cursor.close()
    connection.close()

    # ✅ Final JSON response with total_students and results
    return jsonify({
        "total_students": total_students,
        "results": final
    })



#ddddddddddddelet it
@students_bp.route('/scores2', methods=['GET'])
def scores2():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get filters from query parameters (default is None)
    student_id = request.args.get('student_id', '')
    exam_id = request.args.get('exam_id', '')
    subject_id = request.args.get('subject_id', '')
    major_id = request.args.get('major_id', '')
    generation = request.args.get('generation', '')
    batch = request.args.get('batch', '')
    group_student = request.args.get('group_student', '')
    shift_name = request.args.get('shift_name', '')

    # Fetch score types dynamically from the database, including weight
    cursor.execute("SELECT id, name, max_score, weight FROM score_types ORDER BY id")
    score_types_result = cursor.fetchall()
    ordered_score_types = {score['name']: {'weight': score['weight'], 'max_score': score['max_score']} for score in score_types_result}


 
    # SQL to get student list with LEFT JOIN on scores
    sql = """
    SELECT
        students.id AS student_id,
        students.name AS student_name,
        subjects.name AS subject_name,
        subjects.id AS subject_id,
        score_types.name AS score_type,
        score_types.id AS score_type_id,
        scores.id AS score_id,
        scores.score
        
    FROM students
    CROSS JOIN subjects
    

    
    LEFT JOIN scores ON scores.student_id = students.id 
                     AND scores.subject_id = subjects.id
                   
    LEFT JOIN score_types ON scores.type_id = score_types.id
    LEFT JOIN exams ON scores.exam_id = exams.id
    WHERE 1 = 1


        """

    params = []
    

    if student_id:
        sql += " AND students.id = %s"
        params.append(student_id)

    if exam_id:
        sql += " AND (scores.exam_id = %s OR scores.exam_id IS NULL)"
        params.append(exam_id)

    if subject_id:
        sql += " AND subjects.id = %s"
        params.append(subject_id)



    if major_id:
        sql += " AND students.major_id = %s"
        params.append(major_id)

    if generation:
        sql += " AND students.generation = %s"
        params.append(generation)

    if batch:
        sql += " AND students.batch = %s"
        params.append(batch)

    if group_student:
        sql += " AND students.group_student = %s"
        params.append(group_student)

    if shift_name:
        sql += " AND students.shift_name = %s"
        params.append(shift_name)
        
    sql += " LIMIT 100"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    # Group by student -> subject
    student_data = defaultdict(lambda: defaultdict(lambda: {
        'scores': {},  # Store scores as a dictionary for easy access during processing
        'total': 0,
        'count': 0
    }))

    for row in rows:
        student_name = row['student_name']
        subject_name = row['subject_name'] if row['subject_name'] else 'No Subject'
        score_type = row['score_type']
        score_type_id = row['score_type_id']
        
        score = row['score'] if row['score'] is not None else 0
        
        subject = student_data[student_name][subject_name]
        if score_type:
            subject['scores'][score_type] = score
            subject['total'] += score
            subject['count'] += 1

    # Prepare final result
    result = []

    for student_name, subjects in student_data.items():
        student_result = {
            'student_name': student_name,
            'scores': [],
            'total_score_with_status': 'No (Fail)'  # Flag to check if the total score should have (fail) text
        }

        for subject_name, data in subjects.items():
            subject_scores_list = []  # List to hold scores in order
            fail_detected = False  # Flag to track if any score is a failure

            for score_type, weight_data in ordered_score_types.items():
                score = data['scores'].get(score_type, 0)
                weight = weight_data['weight']
                max_score = weight_data['max_score']
                
                # Check if the score is below the threshold and append (Fail)
                threshold = max_score * weight
                score_with_status = f"{score} (ធ្លាក់)" if score < threshold else str(score)
                

                # Flag failure if this score is below threshold
                if score < threshold:
                    fail_detected = True
                
                subject_scores_list.append({
                    'score_type': score_type,

                    'score': score_with_status
                })

            # If any score is a failure, mark the total as fail
            if fail_detected:
                student_result['total_score_with_status'] = f"{data['total']} (ធ្លាក់)"
            else:
                student_result['total_score_with_status'] = str(data['total'])
                
       
            subject_result_item = {  # Create subject item to be appended
                'subject_name': subject_name,
                'scores': subject_scores_list,  # Keep scores list for Angular table structure
                'total_score': f"{data['total']} (ធ្លាក់)" if fail_detected or data['total'] <= 60 else data['total'],
                'average_score': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0
            }
            
                        # Update overall status flag for the student
  
                
            student_result['scores'].append(subject_result_item)
       

        result.append(student_result)

    cursor.close()
    connection.close()

    # Restructure the result to directly match the table header order
    final_result = []
    for student_data_item in result:
        student_name = student_data_item['student_name']
        student_id = None  # Initialize here
        
        
        
        
        
        
        

        for subject_data in student_data_item['scores']:
            subject_name = subject_data['subject_name']
            subject_id = None
            row_data = {
                'Student Name': student_name,
                'Subject Name': subject_name,
                'ពិន្ទុកសរុប': subject_data['total_score'],

                'Total មធ្យមភាគ': subject_data['average_score'],
                
                'ពិន្ទុកសរុប With Status': subject_data['total_score'] if isinstance(subject_data['total_score'], str) else f"{subject_data['total_score']} (ជាប់)",
            }

            # Find the matching row from original query for IDs
            for row in rows:
                if row['student_name'] == student_name and (row['subject_name'] or 'No Subject') == subject_name:
                    student_id = row['student_id']
                    subject_id = row.get('subject_id') if row['subject_name'] else None
                    break
            row_data['student_id'] = student_id
            row_data['subject_id'] = subject_id
            

            # Add scores with score_type_ids
            for score_type in ordered_score_types:
                matching_score = next((s for s in subject_data['scores'] if s['score_type'] == score_type), {'score': 0})
                row_data[score_type] = matching_score['score']
            final_result.append(row_data)
            
            
            
     
            



    return jsonify(final_result)







# dont delet
@students_bp.route('/scores2tess', methods=['GET'])
def scores2tess():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # Get filters from query parameters (default is None)
    student_id = request.args.get('student_id', '')
    exam_id = request.args.get('exam_id', '')
    subject_id = request.args.get('subject_id', '')
    major_id = request.args.get('major_id', '')
    generation = request.args.get('generation', '')
    batch = request.args.get('batch', '')
    group_student = request.args.get('group_student', '')
    shift_name = request.args.get('shift_name', '')
    
 
    if not (major_id and generation and batch and group_student and shift_name and subject_id):
        return jsonify({'error': 'At least one of the following filters is required: major_id, generation, batch, group_student, or shift_name.'}), 400

    # Fetch score types dynamically from the database, including weight
    cursor.execute( """
                   SELECT 
                   id, 
                   name, 
                   max_score, 
                   weight 
                   
                   FROM 
                   score_types 
                   
                   ORDER BY id 
                   
                   """)
   
    score_types_result = cursor.fetchall()
    ordered_score_types = {score['name']: {'weight': score['weight'], 'max_score': score['max_score']} for score in score_types_result}

    # SQL to get student list with LEFT JOIN on scores
    sql = """
    SELECT
        students.id AS student_id,
        students.name AS student_name,
        subjects.name AS subject_name,
        subjects.id AS subject_id,
        score_types.name AS score_type,
        score_types.id AS score_type_id,
        scores.id AS score_id,
        scores.score
    FROM students
    
    CROSS JOIN subjects
    LEFT JOIN scores ON scores.student_id = students.id 
                     AND scores.subject_id = subjects.id
                      AND scores.exam_id = %s
    LEFT JOIN score_types ON scores.type_id = score_types.id
    LEFT JOIN exams ON scores.exam_id = exams.id
    WHERE 1 = 1
    
    """

    params = [exam_id]
    
    if student_id:
        sql += " AND students.id = %s"
        params.append(student_id)
    if exam_id:
        sql += " AND (scores.exam_id = %s OR scores.exam_id IS NULL)"
        params.append(exam_id)
    if subject_id:
        sql += " AND subjects.id = %s"
        params.append(subject_id)
    if major_id:
        sql += " AND students.major_id = %s"
        params.append(major_id)
    if generation:
        sql += " AND students.generation = %s"
        params.append(generation)
    if batch:
        sql += " AND students.batch = %s"
        params.append(batch)
    if group_student:
        sql += " AND students.group_student = %s"
        params.append(group_student)
    if shift_name:
        sql += " AND students.shift_name = %s"
        params.append(shift_name)
    sql += " LIMIT 100"

    cursor.execute(sql, params)
    
    rows = cursor.fetchall()

    # If no data is found for the exam_id, create fake data with score = 0
    if not rows and exam_id:
        cursor.execute("""
        SELECT 
        students.id AS student_id, 
        students.name AS student_name, 
        subjects.id AS subject_id, 
        subjects.name AS subject_name
       
        FROM students
        
        CROSS JOIN subjects
    
        """)
        
        rows = cursor.fetchall()
        # Generate fake rows with score = 0
        for row in rows:
            row['score'] = 0
            row['score_type'] = 'Fake'  # Assign a placeholder score_type if missing

    # Group by student -> subject
    student_data = defaultdict(lambda: defaultdict(lambda: {
        'scores': {},  # Store scores as a dictionary for easy access during processing
        'total': 0,
        'count': 0
    }))


    for row in rows:
        student_name = row['student_name']
        subject_name = row['subject_name'] if row['subject_name'] else 'No Subject'
        # Safeguard: Check if 'score_type' exists before using it
        score_type = row.get('score_type', 'No Score Type')
        
        score = row['score'] if row['score'] is not None else 0
        
        subject = student_data[student_name][subject_name]
        if score_type != 'No Score Type':  # Only process if score_type exists
            subject['scores'][score_type] = score
            subject['total'] += score
            subject['count'] += 1

    # Prepare final result
    result = []

    for student_name, subjects in student_data.items():
        student_result = {
            'student_name': student_name,
            'scores': [],
            'total_score_with_status': 'No (Fail)'  # Flag to check if the total score should have (fail) text
        }

        for subject_name, data in subjects.items():
            subject_scores_list = []  # List to hold scores in order
            fail_detected = False  # Flag to track if any score is a failure

            for score_type, weight_data in ordered_score_types.items():
                score = data['scores'].get(score_type, 0)
                weight = weight_data['weight']
                max_score = weight_data['max_score']
                
                # Check if the score is below the threshold and append (Fail)
                threshold = max_score * weight
                score_with_status = f"{score} (ធ្លាក់)" if score < threshold else str(score)
                
                # Flag failure if this score is below threshold
                if score < threshold:
                    fail_detected = True
                
                subject_scores_list.append({
                    'score_type': score_type,
                    'score': score_with_status
                })

            # If any score is a failure, mark the total as fail
            if fail_detected:
                student_result['total_score_with_status'] = f"{data['total']} (ធ្លាក់)"
            else:
                student_result['total_score_with_status'] = str(data['total'])
                
            subject_result_item = {
                'subject_name': subject_name,
                'scores': subject_scores_list,
                'total_score': f"{data['total']} (ធ្លាក់)" if fail_detected or data['total'] <= 60 else data['total'],
                'average_score': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0
            }
            
            student_result['scores'].append(subject_result_item)

        result.append(student_result)

    cursor.close()
    connection.close()

    final_result = []
    for student_data_item in result:
        student_name = student_data_item['student_name']
        student_id = None  # Initialize here

        for subject_data in student_data_item['scores']:
            subject_name = subject_data['subject_name']
            subject_id = None
            row_data = {
                'Student Name': student_name,
                'Subject Name': subject_name,
                'ពិន្ទុកសរុប': subject_data['total_score'],
                'Total មធ្យមភាគ': subject_data['average_score'],
                'ពិន្ទុកសរុប With Status': subject_data['total_score'] if isinstance(subject_data['total_score'], str) else f"{subject_data['total_score']} (ជាប់)",
            }

            for row in rows:
                if row['student_name'] == student_name and (row['subject_name'] or 'No Subject') == subject_name:
                    student_id = row['student_id']
                    subject_id = row.get('subject_id') if row['subject_name'] else None
                    break
            row_data['student_id'] = student_id
            row_data['subject_id'] = subject_id

            for score_type in ordered_score_types:
                matching_score = next((s for s in subject_data['scores'] if s['score_type'] == score_type), {'score': 0})
                row_data[score_type] = matching_score['score']
            final_result.append(row_data)

    return jsonify(final_result)



@students_bp.route('/edit_score', methods=['POST'])
def edit_score():
    data = request.json
    print(data)

    try:
        student_id = data['student_id']
        subject_id = data['subject_id']
        score_type = data['score_type']
        
        new_score = data['score']
        exam_id = data['exam_id']       # Optional now
        teacher_id = data.get('teacher_id') # Optional now
    except KeyError as e:
        return jsonify({"message": f"Missing key: {str(e)}"}), 400  # Return error if any key is missing
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the score_type id from the score_types table
    cursor.execute("SELECT id FROM score_types WHERE name = %s", (score_type,))
    id_score_type = cursor.fetchone()

    if not id_score_type:
        return jsonify({"message": "Invalid score type"}), 401

    score_type_id = id_score_type['id']
    print('-------------------')
    print(score_type_id)

    # Check if the score already exists
    cursor.execute("""
        SELECT id FROM scores
        WHERE student_id = %s AND subject_id = %s AND type_id = %s
    """, (student_id, subject_id, score_type_id))

    existing_score = cursor.fetchone()

    if existing_score:
        # If the score exists, update it
        cursor.execute("""
            UPDATE scores
            SET score = %s, exam_id = %s, teacher_id = %s
            WHERE student_id = %s AND subject_id = %s AND type_id = %s
        """, (new_score, exam_id, teacher_id, student_id, subject_id, score_type_id))
    else:
        # If the score doesn't exist, insert a new record
        cursor.execute("""
            INSERT INTO scores (student_id, subject_id, type_id, score, exam_id, teacher_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, subject_id, score_type_id, new_score, exam_id, teacher_id))

    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({"message": "Score updated/created successfully"})





@students_bp.route('/logout', methods=['POST'])
def logout_student():
    """Log out the student by clearing the session or token."""
    # Assuming the client handles removing the token from local storage or cookies
    return jsonify({'message': 'Logged out successfully'}), 200





@students_bp.route('/login', methods=['POST'])
def login_student():
    """Authenticate a student and return their details."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
      # Check if the username exists in the database
    cursor.execute("SELECT * FROM Students WHERE username = %s", (username,))
    student = cursor.fetchone()
    if not student:
        # If username is not found in the database
        return jsonify({'error': 'Username not registered'}), 404  # 404 for "not found" error
    
          # If username is found, check if the password is correct
    if student['password'] != password:  # Assuming passwords are stored in plaintext (NOT RECOMMENDED)
        return jsonify({'error': 'Invalid password'}), 401  # Unauthorized if the password is incorrect

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Students WHERE username = %s AND password = %s", (username, password))
    student = cursor.fetchone()
    cursor.close()
    connection.close()

    if not student:
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful', 'user': student}), 200
    return jsonify({'message': 'Login successful', 'user': {'id': student['id'], 'name': student['name'], 'username': student['username']}}), 200





@students_bp.route('', methods=['GET'])
def get_students():
    """Fetch all students with their corresponding major names, with pagination."""
    
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)
    
    if page <= 0 or page_size <= 0:
        return jsonify({'error': 'Page and pageSize must be positive integers'}), 400
    
    offset = (page - 1) * page_size

    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Query total students
    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM Students
        JOIN Majors ON Students.major_id = Majors.id
    """)
    total_students = cursor.fetchone()[0]  # pyodbc returns tuple, take first column
    
    # Query students with pagination
    cursor.execute("""
        SELECT Students.id, Students.name AS student_name, batch, shift_name, generation, group_student, 
               Majors.name AS major_name, Students.username
        FROM Students
        JOIN Majors ON Students.major_id = Majors.id
        ORDER BY Students.id
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (offset, page_size))
    
    # Fetch all rows
    rows = cursor.fetchall()
    
    # Map results to list of dicts
    columns = [col[0] for col in cursor.description]
    students = [dict(zip(columns, row)) for row in rows]
    
    cursor.close()
    connection.close()

    return jsonify({
        'currentPage': page,
        'pageSize': page_size,
        'totalStudents': total_students,
        'students': students
    })




@students_bp.route('', methods=['POST'])
def add_student():
    """Add a new student to the database."""
    data = request.json

    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    major_id = data.get('major_id')
    date_joined = data.get('date_joined')
    generation = data.get('generation')
    batch = data.get('batch')
    group_student = data.get('group_student')
    shift_name = data.get('shift_name') 
    
    if not username or not password or not major_id or not shift_name:
        return jsonify({'error': 'Username, password, major_id, and shift_name are required fields.'}), 400

    allowed_shifts = [
        'Monday-Friday Morning',
        'Monday-Friday Afternoon',
        'Monday-Friday Evening',
        'Saturday-Sunday'
    ]

    if shift_name not in allowed_shifts:
        return jsonify({'error': 'Invalid shift_name. Allowed values are: "Monday-Friday Morning", "Monday-Friday Afternoon", "Monday-Friday Evening", "Saturday-Sunday".'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()

    try:
        # Check if username already exists in the database
        cursor.execute("SELECT 1 FROM Students WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'error': 'Username already taken'}), 400

        # Insert the new student into the database
        cursor.execute("""
            INSERT INTO Students (username, name, password, major_id, date_joined, generation, batch, group_student, shift_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, name, password, major_id, date_joined, generation, batch, group_student, shift_name))

        connection.commit()
        return jsonify({'message': 'Student added successfully'}), 201

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    finally:
        cursor.close()
        connection.close()


@students_bp.route('/ghost', methods=['POST'])
def add_studentghost():
    """Add a new student to the database."""
    data = request.json

    major_id = data.get('major_id')
    date_joined = data.get('date_joined')
    generation = data.get('generation')
    batch = data.get('batch')
    group_student = data.get('group_student')
    shift_name = data.get('shift_name') 
    


  
    allowed_shifts = [
        'Monday-Friday Morning',
        'Monday-Friday Afternoon',
        'Monday-Friday Evening',
        'Saturday-Sunday'
    ]

    if shift_name not in allowed_shifts:
        return jsonify({'error': 'Invalid shift_name. Allowed values are: "Monday-Friday Morning", "Monday-Friday Afternoon", "Monday-Friday Evening", "Saturday-Sunday".'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

   

    # Insert the new student into the database
    cursor.execute(""" 
        INSERT INTO Students (major_id, date_joined, generation, batch, group_student, shift_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (major_id, date_joined, generation, batch, group_student, shift_name))


    connection.commit()
    cursor.close()
    connection.close()


    return jsonify({'message': 'Student added successfully'}), 201



# GET a specific student
@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Fetch a specific student by their ID."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify(student)

@students_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update an existing student's details with optional fields."""
    
    data = request.json
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    major_id = data.get('major_id')
    generation = data.get('generation')
    batch = data.get('batch')
    group_student = data.get('group_student')

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Prepare the update query dynamically based on the provided fields
    update_values = []
    update_query = "UPDATE Students SET "

    if username is not None:
        update_query += "username = %s, "
        update_values.append(username)
    if name is not None:
        update_query += "name = %s, "
        update_values.append(name)
    if password is not None:
        update_query += "password = %s, "
        update_values.append(password)
    if major_id is not None:
        update_query += "major_id = %s, "
        update_values.append(major_id)
    if generation is not None:
        update_query += "generation = %s, "
        update_values.append(generation)
    if batch is not None:
        update_query += "batch = %s, "
        update_values.append(batch)
    if group_student is not None:
        update_query += "group_student = %s, "
        update_values.append(group_student)

    # Remove trailing comma and space
    update_query = update_query.rstrip(", ")

    # Ensure that at least one field is provided for update
    if not update_values:
        return jsonify({'error': 'No fields to update'}), 400

    update_query += " WHERE id = %s"
    update_values.append(student_id)

    # Execute the query and commit changes
    cursor.execute(update_query, tuple(update_values))
    connection.commit()

    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Student not found or no changes made'}), 404

    return jsonify({'message': 'Student updated successfully'}), 200


# DELETE a student
@students_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Students WHERE id = %s", (student_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Student not found'}), 404

        return jsonify({'message': 'Student deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500



@students_bp.route('/all', methods=['GET'])
def get_all_students():
    """Fetch all students from the database."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, username, name, date_joined, major_id, generation, batch, group_student, shift_name 
            FROM Students
        """)
        students = cursor.fetchall()

        return jsonify(students), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error: ' + str(err)}), 500

    finally:
        cursor.close()
        connection.close()


        
        
        
        
        

#  used
@students_bp.route('/majors_with_students', methods=['GET'])
def get_majors_with_students():
    """Fetch all majors along with aggregated student data."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch all majors with department names
        cursor.execute("""
            SELECT 
                Majors.id AS major_id, 
                Majors.name AS major_name,
                Departments.name AS department_name
            FROM Majors
            JOIN Departments ON Majors.Departments_id = Departments.id
        """)
        majors = cursor.fetchall()

        # Fetch student counts grouped by major_id, generation, batch, group_student, and shift_name
        cursor.execute("""
            SELECT 
                major_id, 
                generation, 
                batch, 
                group_student, 
                shift_name, 
                COUNT(*) AS total_students
            FROM Students
            GROUP BY major_id, generation, batch, group_student, shift_name
        """)
        student_groups = cursor.fetchall()

        # Merge student data with majors
        for major in majors:
            major["students"] = [
                student for student in student_groups if student["major_id"] == major["major_id"]
            ]

        return jsonify(majors), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error: ' + str(err)}), 500

    finally:
        cursor.close()
        connection.close()





@students_bp.route('/students_with_timetable3no', methods=['GET'])
def get_students_with_timetable3no():
    try:
        years = request.args.get('years')
        Semester = request.args.get('Semester')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get all students
        cursor.execute("""
            SELECT 
                s.batch,
                s.generation,
                s.group_student,
                s.major_id,
                s.shift_name
            FROM Students s
        """)
        students = cursor.fetchall()

        # Get timetable data (with filtering by years/Semester)
        timetable_query = """
            SELECT 
                t.batch,
                t.generation,
                t.group_student,
                t.major_id,
                ss.shift_name,
                t.years,
                t.Semester,
                COUNT(t.id) AS timetable_count
            FROM Timetable t
            LEFT JOIN study_sessions ss ON ss.id = t.study_sessions_id
        """

        filters = []
        params = []

        if years:
            filters.append("t.years = %s")
            params.append(years)

        if Semester:
            filters.append("t.Semester = %s")
            params.append(Semester)

        if filters:
            timetable_query += " WHERE " + " AND ".join(filters)

        timetable_query += " GROUP BY t.batch, t.generation, t.group_student, t.major_id, ss.shift_name, t.years, t.Semester"

        cursor.execute(timetable_query, tuple(params))
        timetable_data = cursor.fetchall()

        # Convert timetable data to a dictionary for quick lookup
        timetable_lookup = {}
        for t in timetable_data:
            key = (t["batch"], t["generation"], t["group_student"], t["major_id"], t["shift_name"])
            if key not in timetable_lookup:
                timetable_lookup[key] = {
                    "custom_year_semester": [],
                    "timetable_count": 0
                }
            timetable_lookup[key]["custom_year_semester"].append(f"{t['years']} Summer {t['Semester']}")
            timetable_lookup[key]["timetable_count"] += t["timetable_count"]

        # Prepare response data
        merged_result = {}
        for student in students:
            key = (student["batch"], student["generation"], student["group_student"], student["major_id"], student["shift_name"])
            timetable_entry = timetable_lookup.get(key)

            if key not in merged_result:
                merged_result[key] = {
                    "batch": student["batch"],
                    "generation": student["generation"],
                    "group_student": student["group_student"],
                    "major_id": student["major_id"],
                    "shift_name": student["shift_name"],
                    "custom_year_semester": [],
                    "timetable_count": 0,
                    "message": "ដែលមិនទាន់មាន"  # Default: No timetable assigned
                }

            if timetable_entry:
                merged_result[key]["custom_year_semester"] = timetable_entry["custom_year_semester"]
                merged_result[key]["timetable_count"] = timetable_entry["timetable_count"]
                merged_result[key]["message"] = "មានកាវិភាគ"
                
                
        

        return jsonify({'data': list(merged_result.values())}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error: ' + str(err)}), 500

    finally:
        cursor.close()
        connection.close()
        
@students_bp.route('/students_with_timetable3', methods=['GET'])
def get_students_with_timetable3():
    
    
    try:
        years = request.args.get('years')
        Semester = request.args.get('Semester')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get all students
        cursor.execute("""
            SELECT 
                s.batch,
                s.generation,
                s.group_student,
                s.major_id,
                s.shift_name
            FROM Students s
        """)
        students = cursor.fetchall()

        # Get timetable data (with filtering by years/Semester)
        timetable_query = """
            SELECT 
                t.batch,
                t.generation,
                t.group_student,
                t.major_id,
                ss.shift_name,
                t.years,
                t.Semester,
                COUNT(t.id) AS timetable_count
            FROM Timetable t
            LEFT JOIN study_sessions ss ON ss.id = t.study_sessions_id
        """

        filters = []
        params = []

        if years:
            filters.append("t.years = %s")
            params.append(years)

        if Semester:
            filters.append("t.Semester = %s")
            params.append(Semester)

        if filters:
            timetable_query += " WHERE " + " AND ".join(filters)

        timetable_query += " GROUP BY t.batch, t.generation, t.group_student, t.major_id, ss.shift_name, t.years, t.Semester"

        cursor.execute(timetable_query, tuple(params))
        timetable_data = cursor.fetchall()

        # Convert timetable data to a dictionary for quick lookup
        timetable_lookup = {}
        for t in timetable_data:
            key = (t["batch"], t["generation"], t["group_student"], t["major_id"], t["shift_name"])
            if key not in timetable_lookup:
                timetable_lookup[key] = {
                    "custom_year_semester": [],
                    "timetable_count": 0
                }
            timetable_lookup[key]["custom_year_semester"].append(f"{t['years']} Summer {t['Semester']}")
            timetable_lookup[key]["timetable_count"] += t["timetable_count"]

        # Prepare response data
        merged_result = []
        for student in students:
            key = (student["batch"], student["generation"], student["group_student"], student["major_id"], student["shift_name"])
            timetable_entry = timetable_lookup.get(key)

            entry = {
                "batch": student["batch"],
                "generation": student["generation"],
                "group_student": student["group_student"],
                "major_id": student["major_id"],
                "shift_name": student["shift_name"],
                "custom_year_semester": [],
                "timetable_count": 0,
                "message": "ដែលមិនទាន់មាន"  # Default: No timetable assigned
            }

            if timetable_entry:
                entry["custom_year_semester"] = timetable_entry["custom_year_semester"]
                entry["timetable_count"] = timetable_entry["timetable_count"]
                entry["message"] = "មានកាវិភាគ"

            merged_result.append(entry)

        # 🔥 Sort the data by major_id → generation → batch → group_student → shift_name
        sorted_result = sorted(merged_result, key=lambda x: (
            x["major_id"],
            x["generation"],
            x["batch"],
            x["group_student"],
            x["shift_name"]
        ))

        return jsonify({'data': sorted_result}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error: ' + str(err)}), 500

    finally:
        cursor.close()
        connection.close()

        
        
        
        
        


    try:
        years = request.args.get('years')
        semester = request.args.get('Semester')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get all students with major_id
        cursor.execute("""
            SELECT 
                s.batch,
                s.generation,
                s.group_student,
                s.major_id,  # Only major_id
                s.shift_name
            FROM Students s
        """)
        students = cursor.fetchall()

        # Get timetable data (with filtering by years/Semester)
        timetable_query = """
            SELECT 
                t.batch,
                t.generation,
                t.group_student,
                t.major_id,
                ss.shift_name,
                t.years,
                t.Semester,
                COUNT(t.id) AS timetable_count
            FROM Timetable t
            LEFT JOIN study_sessions ss ON ss.id = t.study_sessions_id
            GROUP BY t.batch, t.generation, t.group_student, t.major_id, ss.shift_name, t.years, t.Semester
        """

        filters = []
        params = []

        if years:
            filters.append("t.years = %s")
            params.append(years)

        if semester:
            filters.append("t.Semester = %s")
            params.append(semester)

        if filters:
            timetable_query += " WHERE " + " AND ".join(filters)

        cursor.execute(timetable_query, tuple(params))
        timetable_data = cursor.fetchall()

        # Convert timetable data to a dictionary for quick lookup
        timetable_lookup = {}
        for t in timetable_data:
            key = (t["batch"], t["generation"], t["group_student"], t["major_id"], t["shift_name"])
            if key not in timetable_lookup:
                timetable_lookup[key] = {
                    "custom_year_semester": [],
                    "timetable_count": 0
                }
            timetable_lookup[key]["custom_year_semester"].append(f"{t['years']} Summer {t['Semester']}")
            timetable_lookup[key]["timetable_count"] += t["timetable_count"]

        # Prepare response data
        merged_result = {}
        for student in students:
            key = (student["major_id"], student["batch"], student["generation"], student["group_student"], student["shift_name"])
            timetable_entry = timetable_lookup.get(key)

            if key not in merged_result:
                merged_result[key] = {
                    "major_id": student["major_id"],  # Include major_id in the result
                    "batch": student["batch"],
                    "generation": student["generation"],
                    "group_student": student["group_student"],
                    "shift_name": student["shift_name"],
                    "custom_year_semester": [],
                    "timetable_count": 0,
                    "message": "Not assigned"  # Default message
                }

            if timetable_entry:
                merged_result[key]["custom_year_semester"] = timetable_entry["custom_year_semester"]
                merged_result[key]["timetable_count"] = timetable_entry["timetable_count"]
                merged_result[key]["message"] = "Assigned"

        return jsonify({'data': list(merged_result.values())}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error: ' + str(err)}), 500

    finally:
        cursor.close()
        connection.close()