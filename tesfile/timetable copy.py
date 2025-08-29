from flask import Blueprint, app, jsonify, request
import mysql.connector
from config import get_db_connection
from flask import jsonify, request
from flask import current_app

timetable_bp = Blueprint('timetable', __name__, url_prefix='/api/timetable')






# for suden
@timetable_bp.route('/filter', methods=['GET'])
def get_timetable_filter():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        major_id = request.args.get('major_id')
        batch = request.args.get('batch')
        years = request.args.get('years')
        semester = request.args.get('semester')
        generation = request.args.get('generation')
        shift_name = request.args.get('shift_name')  # New filter for shift name
        query = """
            SELECT 
                t.id, 
                t.note, 
                t.study_sessions_id, 
                t.group_student,
                t.batch, 
                t.generation, 
                t.major_id, 
                t.teacher_id, 
                t.subject_id, 
                t.room_id,
                t.years,
                t.semester,
                ss.shift_name AS study_shift_name,  
                ss.sessions_day AS study_session_day,
                m.name AS major_name,
                ts.teacher_id AS teacher_id, 
                ts.subject_id AS subject_id,
                r.room_number AS room_number,
                sub.name AS subject_name
            FROM Timetable t
            LEFT JOIN study_sessions ss ON t.study_sessions_id = ss.id
            LEFT JOIN Majors m ON t.major_id = m.id
            LEFT JOIN teacher_subjects ts ON t.teacher_id = ts.teacher_id AND t.subject_id = ts.subject_id
            LEFT JOIN Rooms r ON t.room_id = r.id
            LEFT JOIN Subjects sub ON t.subject_id = sub.id
            WHERE 1=1
        """
        filters = []
        if major_id:
            query += " AND t.major_id = %s"
            filters.append(major_id)
        if batch:
            query += " AND t.batch LIKE %s"
            filters.append(f"%{batch}%")
        if years:
            query += " AND t.years = %s"
            filters.append(years)
        if semester:
            query += " AND t.semester = %s"
            filters.append(semester)
        if generation:
            query += " AND t.generation LIKE %s"
            filters.append(f"%{generation}%")
        if shift_name:  # Apply the shift_name filter
            query += " AND ss.shift_name LIKE %s"
            filters.append(f"%{shift_name}%")
        cursor.execute(query, tuple(filters))
        timetable_entries = cursor.fetchall()
        return jsonify({'timetable_entries': timetable_entries})
    except Exception as e:
        app.logger.error(f"Error fetching timetable data: {e}")
        return jsonify({'error': 'An error occurred while fetching timetable data'}), 500
    finally:
        cursor.close()
        connection.close()
        
  #  send data

# get all data in databes
@timetable_bp.route('', methods=['GET'])
def get_timetable():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch timetable data with detailed error logging
        cursor.execute("""
            SELECT 
                t.id, 
                t.note, 
                t.study_sessions_id, 
                t.group_student, 
                t.batch, 
                t.generation, 
                t.major_id, 
                t.teacher_id, 
                t.subject_id, 
                t.room_id,
                        t.years,
                        t.semester,
                       
                TIME_FORMAT(session_time_start, '%H:%i:%s') AS session_time_start,
                TIME_FORMAT(session_time_end, '%H:%i:%s') AS session_time_end,
                ss.shift_name AS study_shift_name,  
                ss.sessions_day AS study_session_day,
                m.name AS major_name,
                ts.teacher_id AS teacher_id, 
                ts.subject_id AS subject_id,
                r.room_number AS room_number,
                sub.name AS subject_name
                 
            FROM Timetable t
            LEFT JOIN study_sessions ss ON t.study_sessions_id = ss.id
            LEFT JOIN Majors m ON t.major_id = m.id
            LEFT JOIN teacher_subjects ts ON t.teacher_id = ts.teacher_id AND t.subject_id = ts.subject_id
            LEFT JOIN Rooms r ON t.room_id = r.id
            LEFT JOIN Subjects sub ON t.subject_id = sub.id
         
        """)
        timetable_entries = cursor.fetchall()

        return jsonify({'timetable_entries': timetable_entries})

    except Exception as e:
        # Log the exception details
        app.logger.error(f"Error fetching timetable data: {e}")
        return jsonify({'error': 'An error occurred while fetching timetable data'}), 500
    finally:
        cursor.close()
        connection.close()
      

# 🔍 Check
@timetable_bp.route('/checkconflicts', methods=['POST'])
def check_timetable_conflicts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    data = request.json
    required_fields = ['study_sessions_id', 'years', 'semester']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400

    # Extract required parameters
    study_sessions_id = data.get('study_sessions_id')
    years = data.get('years')
    semester = data.get('semester')
    teacher_id = data.get('teacher_id')
    room_id = data.get('room_id')
    subject_id = data.get('subject_id')
    major_id = data.get('major_id')
    generation = data.get('generation')
    group_student = data.get('group_student')

    try:
        conflicts = []
        
        
     


        # Check for room conflicts
        cursor.execute("""
            SELECT id, room_id, study_sessions_id, years, semester 
            FROM Timetable 
            WHERE room_id = %s AND study_sessions_id = %s AND years = %s AND semester = %s
        """, (room_id, study_sessions_id, years, semester))
        room_conflict = cursor.fetchone()
        if room_conflict:
            conflicts.append({
                'room': '🚫 បន្ទប់នេះមិនទំនេរ!',
            })
        cursor.fetchall()  # Ensure we fetch all rows here to avoid unread result

        # Check for teacher conflicts
        cursor.execute("""
            SELECT id, teacher_id, study_sessions_id, years, semester 
            FROM Timetable 
            WHERE teacher_id = %s AND study_sessions_id = %s AND years = %s AND semester = %s
        """, (teacher_id, study_sessions_id, years, semester))
        teacher_conflict = cursor.fetchone()
        if teacher_conflict:
            conflicts.append({
                'teacher': '🚫 គ្រូរមិនទំនេរ!',
            })
        cursor.fetchall()  # Ensure we fetch all rows here to avoid unread result

        # Check for room and subject conflicts
        cursor.execute("""
            SELECT id FROM Timetable 
            WHERE room_id = %s AND teacher_id = %s AND years = %s AND semester = %s AND subject_id = %s 
        """, (room_id, teacher_id, years, semester, subject_id))
        room_subject_exists = cursor.fetchone()
        if room_subject_exists:
            conflicts.append({
                'room_subject': 'គ្រូបានដា់អោយវង្រៀនហើយ 🤝 អាចបន្ថែមសិស្សក្រុមផ្សេងបាន (+them)! ទោបីជា  បន្ទប់នេះមិនទំនេរ!',
            })
         #  else:
         #      conflicts.append({
         #          'room_subject': ' '
        #       })
            cursor.fetchall()  # Ensure we fetch all rows here to avoid unread result





 








        # Check for group student conflicts
        cursor.execute("""
            SELECT * FROM Timetable 
            WHERE group_student = %s AND study_sessions_id = %s AND years = %s AND semester = %s AND major_id = %s AND generation = %s
        """, (group_student, study_sessions_id, years, semester, major_id, generation))
        group_student_conflict = cursor.fetchone()
        if group_student_conflict:
            conflicts.append({
                'messagesessions': '🚫 មានម៉ោងសិក្សារហើយ!'
            })
        cursor.fetchall()  # Ensure we fetch all rows here to avoid unread result

        # Check if the teacher is available at the study session
        cursor.execute("""
            SELECT * FROM teacher_teaching_time
            WHERE teacher_id = %s AND study_sessions_id = %s
        """, (teacher_id, study_sessions_id))
        if not cursor.fetchone():
            conflicts.append({'teacher_time': '🚫 គ្រូមិនអាចបង្រៀននៅម៉ោងនេះបានទេ'})
        cursor.fetchall()  # Ensure we fetch all rows here to avoid unread result

        # Return conflicts if found
        if conflicts:
            return jsonify({'conflicts': conflicts}), 200
        else:
            return jsonify({'message': 'No conflicts found'}), 200

    except mysql.connector.Error as err:
        # MySQL specific error logging
        print(f"MySQL Error: {err}")
        return jsonify({'error': f'MySQL Error: {err}'}), 500
    except Exception as e:
        # General error logging
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        # Ensure all results are fetched before closing the cursor
        try:
            cursor.fetchall()  # Fetch any remaining results to avoid 'Unread result' error
        except Exception as e:
            print(f"Error while fetching remaining results: {str(e)}")
        cursor.close()  # Close the cursor
        connection.close()  # Close the connection


# create timetable 
@timetable_bp.route('', methods=['POST'])
def create_timetable():
    """✏️ បង្កើតកាលវិភាគថ្មី"""
    data = request.json
    current_app.logger.info(f"Received data: {data}")
    # 🛑 ពិនិត្យពាក្យចាំបាច់ 🛑
    required_fields = ['study_sessions_id', 'group_student', 'batch', 'generation',
                       'major_id', 'teacher_id', 'subject_id', 'room_id', 'years', 'semester']
    
    
    # Define a dictionary to map English field names to Khmer labels
    khmer_labels = {
        'study_sessions_id': 'វគ្គសិក្សា',
        'group_student': 'ក្រុមសិស្ស',
        'batch': 'ឆ្នាំ',
        'generation': 'ជំនាន់',
        'major_id': 'ជំនាញ',
        'teacher_id': 'គ្រូបង្រៀន',
        'subject_id': 'មុខវិជ្ជា',
        'room_id': 'បន្ទប់',
        'years': 'ឆ្នាំសិក្សា',
        'semester': 'ឆមាស'
    }

    # Find missing fields
    missing_fields = [khmer_labels[field] for field in required_fields if not data.get(field)]


   # missing_fields = [field for field in required_fields if not data.get(field)]
    errors = []
    if missing_fields:
        errors.append({'error': f"❌ ភ្លេច បញ្ចូល  <br>  <br>{' <br>  '.join(missing_fields)}"}), 400

    # 📌 ទាញយកព័ត៌មានពី Request
    note = data.get('note', '').strip()
    study_sessions_id = data.get('study_sessions_id')
    group_student = data.get('group_student')
    batch = data.get('batch')
    generation = data.get('generation')
    major_id = data.get('major_id')
    teacher_id = data.get('teacher_id')
    subject_id = data.get('subject_id')
    room_id = data.get('room_id')
    years = data.get('years')
    semester = data.get('semester')

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        
        

        
        
        
        
        
        cursor.execute("SELECT number_sessions FROM Teachers WHERE id = %s", (teacher_id,))
        teacher = cursor.fetchone()
        if not teacher:
            errors.append({'error': '🚫 Teacher not found.'}), 400
            return jsonify({'errors': errors}), 400

        # Access number_sessions using index (0 for the first column)
        number_sessions = teacher[0]  # teacher is a tuple, so we access the first element

        # 🔍 Query to count the current timetable entries for the teacher
        cursor.execute("""
            SELECT COUNT(DISTINCT CONCAT(room_id, '-', study_sessions_id)) AS total_timetable
            FROM Timetable
            WHERE teacher_id = %s AND years = %s AND semester = %s
        """, (teacher_id, years, semester))

        result = cursor.fetchone()

        # Access total_timetable using index (0 for the first column in the tuple)
        total_timetable = result[0] if result else 0  # result is a tuple, so access the first element

        # 🔍 Check if total timetable exceeds teacher's allowed sessions
        if total_timetable >= number_sessions:
            errors.append({
                'error': f"🚫 គ្រូបានឈានដល់ចំនួនអតិបរមានៃ sessions ({number_sessions})ហើយសម្រាប់ឆមាសនេះ"
            })
            return jsonify({'errors': errors}), 400

                
        
        
  
        
        
        
        # 🔍 ពិនិត្យមើលថាបន្ទប់ត្រូវបានប្រើរួចឬអត់  ROOM
        cursor.execute("""
            SELECT t.id, ss.id AS study_sessions_id, t.years, t.semester, 
                m.name AS major_name, sub.name AS subject_name, te.name AS teacher_name
            FROM Timetable t
            LEFT JOIN study_sessions ss ON t.study_sessions_id = ss.id
            LEFT JOIN Majors m ON t.major_id = m.id
            LEFT JOIN Subjects sub ON t.subject_id = sub.id
            LEFT JOIN Teachers te ON t.teacher_id = te.id
            WHERE t.room_id = %s AND t.study_sessions_id = %s AND t.years = %s AND t.semester = %s
            AND NOT (t.teacher_id = %s AND t.subject_id = %s)
        """, (room_id, study_sessions_id, years, semester, teacher_id, subject_id))
        existing_room = cursor.fetchone()
        if existing_room:
            errors.append({
                'error': f'🚫 <strong>បន្ទប់មិនទំនេរ</strong> <br/>'
                        f'<strong>Timetable ID:</strong> {existing_room[0]} '
                        f'<strong>វគ្គសិក្សា:</strong> {existing_room[1]} '
                        f'<strong>ឆ្នាំសិក្សា:</strong> {existing_room[2]} '
                        f'<strong>ឆមាស:</strong> {existing_room[3]} <br/>'
                        f'<strong>ជំនាញ:</strong> {existing_room[4]} <br/>'
                        f'<strong>មុខវិជ្ជា:</strong> {existing_room[5]} <br/>'
                        f'<strong>គ្រូបង្រៀន:</strong> {existing_room[6]} <br/>​ <hr>'
            })






        # 🔍 ពិនិត្យមើលថាគ្រូស្ថិតនៅក្នុងបន្ទប់តែមួយក្នុង study_sessions_id, years, semester
        cursor.execute("""
            SELECT t.id, t.room_id, t.study_sessions_id, t.years, t.semester
            FROM Timetable t
            WHERE t.teacher_id = %s 
                AND t.study_sessions_id = %s 
                AND t.years = %s 
                AND t.semester = %s 
                AND t.room_id <> %s
        """, (teacher_id, study_sessions_id, years, semester, room_id))

        existing_teacher_room = cursor.fetchone()

        if existing_teacher_room:
            errors.append({
                'error': f'🚫 <strong>គ្រូបជាប់ង្រៀនហើយ ប្រហែលជានៅបន្ទប់ផ្សេង</strong> <br/>'
                        f'👨‍🏫 <strong>សម្រាប់sessionsនេះ</strong> <br/>'
                  
            })
            
            
            
            #មិនទានហើយ
        # 🔍 ពិនិត្យមើលថាមាន batch ដដែលអត់សម្រាប់ study_sessions_id, years, semester
  # 🔍 ពិនិត្យមើលថាតើមានកំណត់ត្រា Timetable សម្រាប់ study_sessions_id, years, semester និង generation ទេ
 
            
            
 






        # 🔍 ពិនិត្យថាក្រុមសិស្សមានម៉ោងសិក្សារួចនៅឬអត់  stusen  AND generation = %s
        cursor.execute("""
                SELECT * FROM Timetable 
                WHERE group_student = %s AND study_sessions_id = %s AND years = %s AND Semester = %s 
                    AND major_id = %s 
            """, (group_student, study_sessions_id, years, semester, major_id))

        if cursor.fetchone():
            errors.append({
                    'error': '🚫 <strong>ក្រុមសិស្សរួចហើយ</strong> <br/>'
                            '👨‍🎓 <strong>ក្រុមត្រូវបានចាត់តាំងរួចហើយសម្រាប់វគ្គនេះ</strong> <br/> <hr>'
            })
            
            
        
        
        
        
             #  new 🔍 ពិនិត្យថាក្រុមសិស្សមានម៉ោងសិក្សារួចនៅឬអត់  stusen  AND generation = %s
        cursor.execute("""
                SELECT * FROM Timetable 
                WHERE  generation  = %s AND study_sessions_id = %s AND years = %s AND Semester = %s 
                    AND major_id = %s 
            """, (generation, study_sessions_id, years, semester, major_id))

        if not cursor.fetchone():
            errors.append({
                    'error': '🚫 <strong>   </strong> <br/>'
            })
                
                
    


      
        







        # 🔍 ពិនិត្យមើលថាគ្រូនេះអាចបង្រៀនមុខវិជ្ជានេះឬអត់ teacher
        cursor.execute("""
            SELECT * FROM teacher_subjects 
            WHERE teacher_id = %s AND subject_id = %s
        """, (teacher_id, subject_id))

        if not cursor.fetchone():
            errors.append({'error': '🚫 គ្រូមិនអាចបង្រៀនមុខវិជ្ជានេះបានទេ ❌'}), 400

        # 🔍 ពិនិត្យមើលថាគ្រូមានសមត្ថភាពបង្រៀននៅម៉ោងនេះឬអត់ teacher
        cursor.execute("""
            SELECT * FROM teacher_teaching_time
            WHERE teacher_id = %s AND study_sessions_id = %s
        """, (teacher_id, study_sessions_id))

        if not cursor.fetchone():
            errors.append({'error': '🚫 គ្រូមិនអាចបង្រៀននៅម៉ោងនេះបានទេ ❌'}), 400
            
            
       
    
       
   
        
        

        # 👉 ប្រសិនបើមានកំហុសណាមួយ
        if errors:
            return jsonify({'errors': errors}), 400

        # ✅ បញ្ចូលទិន្នន័យកាលវិភាគថ្មី
        cursor.execute("""
            INSERT INTO Timetable (
                study_sessions_id, group_student, note, batch, generation, major_id,
                teacher_id, subject_id, room_id, years, Semester
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (study_sessions_id, group_student, note, batch, generation, major_id,
              teacher_id, subject_id, room_id, years, semester))

        connection.commit()
        return jsonify({'message': '🎉 បានបង្កើតដោយជោគជ័យ! ✅'}), 201

    except mysql.connector.Error as err:
        connection.rollback()
        current_app.logger.error(f"🚨 Error creating timetable: {err}")
        errors.append({'error': f'❌ មានបញ្ហា៖ {err}'}), 500
        return jsonify({'errors': errors}), 500
    finally:
        cursor.close()
        connection.close()


# delet timetable
@timetable_bp.route('/<int:timetable_id>', methods=['DELETE'])
def delete_timetable(timetable_id):
    """Delete a timetable entry by ID."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the timetable entry exists
        cursor.execute("SELECT * FROM Timetable WHERE id = %s", (timetable_id,))
        timetable = cursor.fetchone()

        if not timetable:
            return jsonify({'error': 'Timetable entry not found'}), 404

        # Perform the delete operation
        cursor.execute("DELETE FROM Timetable WHERE id = %s", (timetable_id,))
        connection.commit()

        return jsonify({'message': 'Timetable entry deleted successfully'}), 200

    except mysql.connector.Error as err:
        connection.rollback()
        app.logger.error(f"Error deleting timetable: {err}")
        return jsonify({'error': f'An error occurred: {err}'}), 500

    finally:
        cursor.close()
        connection.close()
        













# Update a timetable 
@timetable_bp.route('/<int:timetable_id>', methods=['PUT'])
def update_timetable(timetable_id):
    """Update a timetable entry by ID."""
    data = request.json
    required_fields = [
        'study_sessions_id', 'group_student', 'batch', 'generation',
        'major_id', 'teacher_id', 'subject_id', 'room_id', 'years', 'semester'
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if timetable entry exists
        cursor.execute("SELECT * FROM Timetable WHERE id = %s", (timetable_id,))
        existing_entry = cursor.fetchone()
        if not existing_entry:
            return jsonify({'error': 'Timetable entry not found'}), 404

        # Extract fields for update
        study_sessions_id = data.get('study_sessions_id')
        group_student = data.get('group_student')
        batch = data.get('batch')
        generation = data.get('generation')
        major_id = data.get('major_id')
        teacher_id = data.get('teacher_id')
        subject_id = data.get('subject_id')
        room_id = data.get('room_id')
        years = data.get('years')
        semester = data.get('semester')
        note = data.get('note', '').strip()

        # Update the timetable entry
        cursor.execute("""
            UPDATE Timetable
            SET 
                study_sessions_id = %s,
                group_student = %s,
                batch = %s,
                generation = %s,
                major_id = %s,
                teacher_id = %s,
                subject_id = %s,
                room_id = %s,
                years = %s,
                semester = %s,
                note = %s
            WHERE id = %s
        """, (study_sessions_id, group_student, batch, generation, major_id, teacher_id,
              subject_id, room_id, years, semester, note, timetable_id))

        connection.commit()
        return jsonify({'message': 'Timetable entry updated successfully'}), 200

    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({'error': f'An error occurred: {err}'}), 500

    finally:
        cursor.close()
        connection.close()
