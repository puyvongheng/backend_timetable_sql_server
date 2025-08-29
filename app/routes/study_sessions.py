from flask import Blueprint, jsonify, request
from config import get_db_connection
import unicodedata
from datetime import datetime, time

study_sessions_bp = Blueprint('study_sessions', __name__, url_prefix='/api/study_sessions')


# Helper to convert SQL rows to dict
def rows_to_dict(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Convert HH:MM[:SS] to minutes
# Convert HH:MM[:SS] to minutes
def time_to_minutes(t):
    """
    Convert time to minutes since midnight.
    Accepts:
      - string "HH:MM" or "HH:MM:SS"
      - datetime.time object
      - tuple/list [hour, minute]
    """
    if isinstance(t, str):
        t = t.strip()
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                dt = datetime.strptime(t, fmt)
                return dt.hour * 60 + dt.minute
            except ValueError:
                continue
        raise ValueError("Invalid time format: " + t)
    elif isinstance(t, time):
        return t.hour * 60 + t.minute
    elif isinstance(t, (list, tuple)) and len(t) >= 2:
        return int(t[0]) * 60 + int(t[1])
    else:
        raise ValueError(f"Invalid time format: {t}")



# ----------------- GET all study sessions -----------------
@study_sessions_bp.route('', methods=['GET'])
def get_study_sessions():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, shift_name, sessions_day,
                   CONVERT(VARCHAR(8), session_time_start, 108) AS session_time_start,
                   CONVERT(VARCHAR(8), session_time_end, 108) AS session_time_end
            FROM study_sessions
        """)
        study_sessions = rows_to_dict(cursor)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify(study_sessions)


# ----------------- POST a new study session -----------------
@study_sessions_bp.route('', methods=['POST'])
def add_study_session():
    data = request.json
    shift_name = data.get('shift_name')
    sessions_day = data.get('sessions_day')
    session_time_start = data.get('session_time_start')
    session_time_end = data.get('session_time_end')

    if not shift_name or not sessions_day or not session_time_start or not session_time_end:
        return jsonify({'error': 'All fields are required'}), 400

    # Khmer-safe normalization
    shift_name = unicodedata.normalize('NFC', shift_name.strip())
    sessions_day = unicodedata.normalize('NFC', sessions_day.strip())

    new_start = time_to_minutes(session_time_start)
    new_end = time_to_minutes(session_time_end)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check overlapping sessions
        cursor.execute("""
            SELECT session_time_start, session_time_end FROM study_sessions
            WHERE shift_name = ? AND sessions_day = ?
        """, (shift_name, sessions_day))

        for row in cursor.fetchall():
            existing_start = time_to_minutes(row[0])
            existing_end = time_to_minutes(row[1])
            if new_start < existing_end and new_end > existing_start:
                return jsonify({'error': 'មានទិន្នន័យរួចហើយ'}), 409

        # Check exact duplicate
        cursor.execute("""
            SELECT id FROM study_sessions
            WHERE shift_name = ? AND sessions_day = ? AND session_time_start = ? AND session_time_end = ?
        """, (shift_name, sessions_day, session_time_start, session_time_end))
        if cursor.fetchone():
            return jsonify({'error': 'Study session already exists'}), 409

        # Insert
        cursor.execute("""
            INSERT INTO study_sessions (shift_name, sessions_day, session_time_start, session_time_end)
            VALUES (?, ?, ?, ?)
        """, (shift_name, sessions_day, session_time_start, session_time_end))
        connection.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'Study session added successfully'}), 201


# ----------------- GET a study session by ID -----------------
@study_sessions_bp.route('/<int:study_session_id>', methods=['GET'])
def get_study_session(study_session_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM study_sessions WHERE id = ?", (study_session_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Study session not found'}), 404
        columns = [col[0] for col in cursor.description]
        session = dict(zip(columns, row))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    return jsonify(session)


# ----------------- PUT update a study session -----------------
@study_sessions_bp.route('/<int:study_session_id>', methods=['PUT'])
def update_study_session(study_session_id):
    data = request.json
    shift_name = data.get('shift_name')
    sessions_day = data.get('sessions_day')
    session_time_start = data.get('session_time_start')
    session_time_end = data.get('session_time_end')

    if not shift_name or not sessions_day or not session_time_start or not session_time_end:
        return jsonify({'error': 'All fields are required'}), 400

    shift_name = unicodedata.normalize('NFC', shift_name.strip())
    sessions_day = unicodedata.normalize('NFC', sessions_day.strip())

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE study_sessions
            SET shift_name = ?, sessions_day = ?, session_time_start = ?, session_time_end = ?
            WHERE id = ?
        """, (shift_name, sessions_day, session_time_start, session_time_end, study_session_id))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Study session not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'Study session updated successfully'}), 200


# ----------------- DELETE a study session -----------------
@study_sessions_bp.route('/<int:study_session_id>', methods=['DELETE'])
def delete_study_session(study_session_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE id = ?", (study_session_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Study session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'message': 'Study session deleted successfully'}), 200
