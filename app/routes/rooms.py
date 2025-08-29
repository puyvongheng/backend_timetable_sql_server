from flask import Blueprint, jsonify, request
from config import get_db_connection

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


# Helper to convert rows to dict
def rows_to_dict(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# GET all rooms
@rooms_bp.route('', methods=['GET'])
def get_rooms():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Rooms")
    rooms = rows_to_dict(cursor)
    cursor.close()
    connection.close()
    return jsonify(rooms)


# POST a new room
@rooms_bp.route('', methods=['POST'])
def add_room():
    data = request.json
    room_number = data.get('room_number')
    capacity = data.get('capacity')
    floor = data.get('floor')
    room_type = data.get('room_type')

    if not room_number or not capacity or not floor or not room_type:
        return jsonify({'error': 'All fields are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Rooms (room_number, capacity, floor, room_type)
        VALUES (?, ?, ?, ?)
    """, (room_number, capacity, floor, room_type))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Room added successfully'}), 201


# GET a specific room
@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Rooms WHERE id = ?", (room_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if not row:
        return jsonify({'error': 'Room not found'}), 404

    # Convert tuple to dict
    room = dict(zip([column[0] for column in cursor.description], row))
    return jsonify(room)


# PUT update an existing room
@rooms_bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.json
    room_number = data.get('room_number')
    capacity = data.get('capacity')
    floor = data.get('floor')
    room_type = data.get('room_type')

    if not room_number or not capacity or not floor or not room_type:
        return jsonify({'error': 'All fields are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Rooms
        SET room_number = ?, capacity = ?, floor = ?, room_type = ?
        WHERE id = ?
    """, (room_number, capacity, floor, room_type, room_id))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Room not found or no changes made'}), 404

    return jsonify({'message': 'Room updated successfully'}), 200


# DELETE a room
@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Rooms WHERE id = ?", (room_id,))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Room not found'}), 404

    return jsonify({'message': 'Room deleted successfully'}), 200
