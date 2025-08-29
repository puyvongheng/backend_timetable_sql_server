from flask import Blueprint, jsonify, request
from config import get_db_connection

teacher_teaching_time_bp = Blueprint('teacher_teaching_time', __name__, url_prefix='/api/teacher_teaching_time')


# Helper to convert rows to dict
def rows_to_dict(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# GET all teacher-teaching time associations
@teacher_teaching_time_bp.route('', methods=['GET'])
def get_teacher_teaching_time():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT Teachers.name AS teacher_name, teacher_teaching_time.teacher_id,
                   study_sessions.id AS session_id, study_sessions.shift_name,
                   study_sessions.sessions_day,
                   CONVERT(VARCHAR(8), study_sessions.session_time_start, 108) AS session_time_start,
                   CONVERT(VARCHAR(8), study_sessions.session_time_end, 108) AS session_time_end
            FROM teacher_teaching_time
            JOIN Teachers ON teacher_teaching_time.teacher_id = Teachers.id
            JOIN study_sessions ON teacher_teaching_time.study_sessions_id = study_sessions.id
        """

        cursor.execute(query)
        teacher_teaching_time = rows_to_dict(cursor)
        cursor.close()
        connection.close()
        return jsonify(teacher_teaching_time)

    except Exception as e:
        return jsonify({'error': f"Unexpected error: {e}"}), 500


# POST multiple teacher-teaching time associations
@teacher_teaching_time_bp.route('', methods=['POST'])
def add_teacher_teaching_times():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of teacher-teaching time associations'}), 400

    associations_to_insert = []
    for item in data:
        teacher_id = item.get('teacher_id')
        study_sessions_id = item.get('study_sessions_id')
        if not teacher_id or not study_sessions_id:
            return jsonify({'error': 'Both teacher_id and study_sessions_id are required for each entry'}), 400
        associations_to_insert.append((teacher_id, study_sessions_id))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for teacher_id, study_sessions_id in associations_to_insert:
            cursor.execute("""
                SELECT COUNT(*) FROM teacher_teaching_time
                WHERE teacher_id = ? AND study_sessions_id = ?
            """, (teacher_id, study_sessions_id))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO teacher_teaching_time (teacher_id, study_sessions_id)
                    VALUES (?, ?)
                """, (teacher_id, study_sessions_id))

        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Teacher-Teaching Time associations added successfully'}), 201

    except Exception as e:
        return jsonify({'error': f"Unexpected error: {e}"}), 500




# DELETE multiple teacher-teaching time associations
@teacher_teaching_time_bp.route('', methods=['DELETE'])
def delete_teacher_teaching_times():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of teacher-teaching time associations'}), 400

    associations_to_delete = []
    for item in data:
        teacher_id = item.get('teacher_id')
        study_sessions_id = item.get('study_sessions_id')
        if not teacher_id or not study_sessions_id:
            return jsonify({'error': 'Both teacher_id and study_sessions_id are required for each entry'}), 400
        associations_to_delete.append((teacher_id, study_sessions_id))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        for teacher_id, study_sessions_id in associations_to_delete:
            cursor.execute("""
                DELETE FROM teacher_teaching_time
                WHERE teacher_id = ? AND study_sessions_id = ?
            """, (teacher_id, study_sessions_id))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': f'{len(associations_to_delete)} Teacher-Teaching Time associations deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': f"Unexpected error: {e}"}), 500
