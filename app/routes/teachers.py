from flask import Blueprint, jsonify, request, session
from config import get_db_connection  # ត្រូវកែ config.py ឲ្យ connect SQL Server
import pyodbc

teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')

# ----------------- Get total timetable by teacher -----------------
@teachers_bp.route('/teacher/<int:teacher_id>/total', methods=['GET'])
def get_total_timetable_by_teacher(teacher_id):
    year = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    
    if not year or not semester:
        return jsonify({'error': 'Year and semester must be provided.'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(DISTINCT CAST(room_id AS NVARCHAR) + '-' + CAST(study_sessions_id AS NVARCHAR)) AS total_timetable
            FROM Timetable
            WHERE teacher_id = ? AND years = ? AND semester = ?
        """, (teacher_id, year, semester))

        row = cursor.fetchone()
        total_timetable = row[0] if row else 0
        
        
        print (row)
        print (total_timetable)


        return jsonify({
            'teacher_id': teacher_id,
            'year': year,
            'semester': semester,
            'total_timetable': total_timetable
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500
    finally:
        cursor.close()
        connection.close()


# ----------------- Get all teachers -----------------
@teachers_bp.route('', methods=['GET'])
def get_teachers():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Fetch all teachers
    cursor.execute("SELECT id, username, name, role, number_sessions FROM Teachers")
    rows = cursor.fetchall()
    
    # Convert to list of dict (pyodbc returns tuples)
    teachers = [
        {
            "id": row[0],
            "username": row[1],
            "name": row[2],
            "role": row[3],
            "number_sessions": row[4]
        }
        for row in rows
    ]

    cursor.close()
    connection.close()

    return jsonify(teachers)
# get all data teacher
# @teachers_bp.route('', methods=['GET'])
# def get_teachers():
#     """Fetch all teachers or only the logged-in teacher's details."""
#     """Fetch all subjects."""
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT * FROM Teachers
#     """)

#     subjects = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return jsonify(subjects)


# ----------------- Get teachers with search & pagination -----------------
@teachers_bp.route('1', methods=['GET'])
def get_teachers1():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    rows_per_page = int(request.args.get('rows', 5))
    offset = (page - 1) * rows_per_page

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch filtered teachers
    cursor.execute("""
        SELECT id, username, name, role FROM Teachers
        WHERE username LIKE ? OR name LIKE ? OR role LIKE ?
        ORDER BY id
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (f'%{search}%', f'%{search}%', f'%{search}%', offset, rows_per_page))

    rows = cursor.fetchall()
    teachers = [{'id': r[0], 'username': r[1], 'name': r[2], 'role': r[3]} for r in rows]

    # Count total records
    cursor.execute("""
        SELECT COUNT(*) FROM Teachers
        WHERE username LIKE ? OR name LIKE ? OR role LIKE ?
    """, (f'%{search}%', f'%{search}%', f'%{search}%'))
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + rows_per_page - 1) // rows_per_page

    cursor.close()
    connection.close()

    return jsonify({
        'data': teachers,
        'totalRecords': total_records,
        'totalPages': total_pages,
        'page': page,
        'rows': rows_per_page,
        'pageInfo': f'Page {page} of {total_pages}'
    })

# ----------------- Check username -----------------
@teachers_bp.route('/username/<username>', methods=['GET'])
def check_username(username):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Teachers WHERE username = ?", (username,))
    is_taken = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return jsonify({'is_taken': is_taken})



# ----------------- Add teacher -----------------
@teachers_bp.route('', methods=['POST'])
def add_teacher():
    data = request.json
    username = data.get('username')
    
    

    name = data.get('name')
    password = data.get('password')
    role = data.get('role', 'simple')
    number_sessions = data.get('number_sessions')
    
    
    print (data)

    if not username or not name or not password:
        return jsonify({'error': 'Username, name, and password are required'}), 400
    if role not in ['admin', 'simple']:
        return jsonify({'error': 'Invalid role'}), 400
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
        return jsonify({'error': 'Password must be 8+ chars, 1 number, 1 uppercase'}), 400




    connection = get_db_connection()
    cursor = connection.cursor()
    
    
    cursor.execute("SELECT COUNT(*) FROM Teachers WHERE username = ?", (username,))
    
    
    
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': 'Username already taken'}), 400



    cursor.execute("""
        INSERT INTO Teachers (username, name, password, role, number_sessions)
        VALUES (?, ?, ?, ?, ?)
    """, (username, name, password, role, number_sessions))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Teacher added successfully'}), 201






# ----------------- Get teacher by id -----------------
@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, name, role FROM Teachers WHERE id = ?", (teacher_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if not row:
        return jsonify({'error': 'Teacher not found'}), 404
    teacher = {'id': row[0], 'username': row[1], 'name': row[2], 'role': row[3]}
    return jsonify(teacher)




# ----------------- Update teacher -----------------
@teachers_bp.route('/admin/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    data = request.json
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')
    role = data.get('role')
    number_sessions = data.get('number_sessions')
    print(data)

    if not username or not name:
        return jsonify({'error': 'Username and name required'}), 400
    if role and role not in ['admin', 'simple']:
        return jsonify({'error': 'Invalid role'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM Teachers WHERE id = ?", (teacher_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Teacher not found'}), 404

    # Build dynamic update query
    update_fields = ["username = ?", "name = ?", "role = ?", "number_sessions = ?"]
    values = [username, name, role, number_sessions]
    if password:
        update_fields.append("password = ?")
        values.append(password)
    values.append(teacher_id)

    query = f"UPDATE Teachers SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Teacher updated successfully'}), 200

# ----------------- Update teacher role only -----------------
@teachers_bp.route('', methods=['PUT'])
def update_teacher_role():
    data = request.json
    teacher_id = data.get('id')
    new_role = data.get('role')
    if not teacher_id or not new_role:
        return jsonify({'error': 'Teacher ID and role required'}), 400
    if new_role not in ['admin', 'simple']:
        return jsonify({'error': 'Invalid role'}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Teachers SET role = ? WHERE id = ?", (new_role, teacher_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Teacher not found or no changes'}), 404
    return jsonify({'message': 'Role updated successfully'}), 200


# ----------------- Delete teacher -----------------
@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Teachers WHERE id = ?", (teacher_id,))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Teacher not found'}), 404
    return jsonify({'message': 'Teacher deleted successfully'}), 200

# ----------------- Login -----------------
@teachers_bp.route('/login', methods=['POST'])
def login_teacher():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, name, password, role FROM Teachers WHERE username = ?", (username,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        return jsonify({'error': 'Username not registered'}), 404

    teacher = {'id': row[0], 'username': row[1], 'name': row[2], 'password': row[3], 'role': row[4]}
    if teacher['password'] != password:
        return jsonify({'error': 'Invalid username or password'}), 401

    session['teacher_id'] = teacher['id']
    session['teacher_username'] = teacher['username']
    session['teacher_name'] = teacher['name']
    session['teacher_role'] = teacher['role']

    return jsonify({'message': 'Login successful', 'user': teacher}), 200

# ----------------- Logout -----------------
@teachers_bp.route('/logout', methods=['POST'])
def logout_teacher():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

