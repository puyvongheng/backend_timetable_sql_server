from flask import Blueprint, jsonify, request
from config import get_db_connection

majors_bp = Blueprint('majors', __name__, url_prefix='/api/majors')

# GET a specific major by ID
@majors_bp.route('/fillter/<int:major_id>', methods=['GET'])
def get_major_fillter(major_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name AS major_name
        FROM Majors
        WHERE id = ?
    """, (major_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        return jsonify({'error': 'Major not found'}), 404

    major = {'major_name': row[0]}
    return jsonify(major)

# GET all majors with their corresponding department and faculty names
@majors_bp.route('', methods=['GET'])
def get_majors():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            Majors.id, 
            Majors.name AS major_name, 
            Departments.id AS department_id,
            Departments.name AS department_name, 
            Faculties.id AS faculty_id,
            Faculties.name AS faculty_name
        FROM Majors
        JOIN Departments ON Majors.Departments_id = Departments.id
        JOIN Faculties ON Departments.Faculties_id = Faculties.id
    """)
    columns = [column[0] for column in cursor.description]
    majors = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(majors)

# POST a new major
@majors_bp.route('', methods=['POST'])
def add_major():
    data = request.json
    name = data.get('name')
    department_id = data.get('department_id')

    if not name or not department_id:
        return jsonify({'error': 'Name and department ID are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO Majors (Departments_id, name) VALUES (?, ?)",
            (department_id, name)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Major added successfully'}), 201
    except Exception as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500

# PUT update an existing major
@majors_bp.route('/<int:major_id>', methods=['PUT'])
def update_major(major_id):
    data = request.json
    name = data.get('name')
    department_id = data.get('department_id')

    if not name or not department_id:
        return jsonify({'error': 'Name and department ID are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Majors
        SET name = ?, Departments_id = ?
        WHERE id = ?
    """, (name, department_id, major_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Major not found or no changes made'}), 404

    return jsonify({'message': 'Major updated successfully'}), 200

# DELETE a major
@majors_bp.route('/<int:major_id>', methods=['DELETE'])
def delete_major(major_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Delete related timetable and students first
        cursor.execute("DELETE FROM Timetable WHERE major_id = ?", (major_id,))
        cursor.execute("DELETE FROM Students WHERE major_id = ?", (major_id,))
        # Now delete the major itself
        cursor.execute("DELETE FROM Majors WHERE id = ?", (major_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Major not found'}), 404

        return jsonify({'message': 'Major deleted successfully'}), 200
    except Exception as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
