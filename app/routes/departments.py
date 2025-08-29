from flask import Blueprint, jsonify, request
from config import get_db_connection

departments_bp = Blueprint('departments', __name__, url_prefix='/api/departments')

# GET all departments
@departments_bp.route('', methods=['GET'])
def get_departments():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT Departments.id, Departments.name AS department_name, 
               Faculties.id AS faculty_id, Faculties.name AS faculty_name
        FROM Departments
        INNER JOIN Faculties ON Departments.Faculties_id = Faculties.id
    """)
    columns = [column[0] for column in cursor.description]
    departments = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(departments)

# POST a new department
@departments_bp.route('', methods=['POST'])
def add_department():
    data = request.json
    name = data.get('name')
    faculty_id = data.get('faculty_id')

    if not name or not faculty_id:
        return jsonify({'error': 'Both name and faculty_id are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO Departments (name, Faculties_id) VALUES (?, ?)",
            (name, faculty_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Department added successfully'}), 201

    except Exception as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500

# GET a specific department
@departments_bp.route('/<int:department_id>', methods=['GET'])
def get_department(department_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT Departments.id, Departments.name AS department_name, 
               Faculties.id AS faculty_id, Faculties.name AS faculty_name
        FROM Departments
        INNER JOIN Faculties ON Departments.Faculties_id = Faculties.id
        WHERE Departments.id = ?
    """, (department_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        return jsonify({'error': 'Department not found'}), 404

    columns = ['id', 'department_name', 'faculty_id', 'faculty_name']
    department = dict(zip(columns, row))
    return jsonify(department)

# PUT update a department
@departments_bp.route('/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    data = request.json
    name = data.get('name')
    faculty_id = data.get('faculty_id')

    if not name or not faculty_id:
        return jsonify({'error': 'Both name and faculty_id are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Departments SET name = ?, Faculties_id = ? WHERE id = ?",
        (name, faculty_id, department_id)
    )
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Department not found or no changes made'}), 404

    return jsonify({'message': 'Department updated successfully'}), 200

# DELETE a department
@departments_bp.route('/<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Departments WHERE id = ?", (department_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Department not found'}), 404

        return jsonify({'message': 'Department deleted successfully'}), 200

    except Exception as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
