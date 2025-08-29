from flask import Blueprint, jsonify, request
from config import get_db_connection

faculties_bp = Blueprint('faculties', __name__, url_prefix='/api/faculties')

# GET all faculties
@faculties_bp.route('', methods=['GET'])
def get_faculties():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Faculties")
    columns = [column[0] for column in cursor.description]
    faculties = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(faculties)

# POST a new faculty
@faculties_bp.route('', methods=['POST'])
def add_faculty():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Faculties (name) VALUES (?)", (name,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Faculty added successfully'}), 201

# GET a specific faculty
@faculties_bp.route('/<int:faculty_id>', methods=['GET'])
def get_faculty(faculty_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Faculties WHERE id = ?", (faculty_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        return jsonify({'error': 'Faculty not found'}), 404

    columns = ['id', 'name']  # update with your table columns
    faculty = dict(zip(columns, row))
    return jsonify(faculty)

# PUT update a faculty
@faculties_bp.route('/<int:faculty_id>', methods=['PUT'])
def update_faculty(faculty_id):
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Faculties SET name = ? WHERE id = ?", (name, faculty_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Faculty not found or no changes made'}), 404

    return jsonify({'message': 'Faculty updated successfully'}), 200

# DELETE a faculty
@faculties_bp.route('/<int:faculty_id>', methods=['DELETE'])
def delete_faculty(faculty_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Faculties WHERE id = ?", (faculty_id,))
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        connection.close()

        if rows_affected == 0:
            return jsonify({'error': 'Faculty not found'}), 404

        return jsonify({'message': 'Faculty deleted successfully'}), 200

    except Exception as err:
        return jsonify({'error': 'An unexpected error occurred: ' + str(err)}), 500
