from flask import Blueprint, jsonify, request
from config import get_db_connection

subjects_bp = Blueprint('subjects', __name__, url_prefix='/api/subjects')


# Utility to convert rows to dict
def rows_to_dict(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]




@subjects_bp.route('', methods=['GET'])
def get_subjects():
    """Fetch all subjects with faculty details."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT s.id, s.name, s.faculties_id, s.batch, f.name AS faculty_name
        FROM Subjects s
        LEFT JOIN Faculties f ON s.faculties_id = f.id
      
    """)
    
    subjects = rows_to_dict(cursor)   # <-- convert to dict
    
    cursor.close()
    connection.close()
    
    sorted_subjects = sorted(
        subjects,
        key=lambda x: (
            x["faculties_id"] if x["faculties_id"] is not None else float('inf'),
            x["batch"] if x["batch"] is not None else float('inf'),
            x["name"] or ""   # default empty string if name is None
        )
    )    
    return jsonify(sorted_subjects)






# GET subjects with optional faculties filter
@subjects_bp.route('/filter', methods=['GET'])
def get_subjects_filter():
    faculties_id = request.args.get('faculties_id', type=int)
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT s.id, s.name, s.faculties_id, f.name AS faculty_name, s.batch
        FROM Subjects s
        LEFT JOIN Faculties f ON s.faculties_id = f.id
    """
    params = []
    if faculties_id:
        query += " WHERE s.faculties_id = ?"
        params.append(faculties_id)

    cursor.execute(query, tuple(params))
    subjects = rows_to_dict(cursor)
    cursor.close()
    connection.close()

    sorted_subjects = sorted(subjects, key=lambda x: (x["faculties_id"], x["name"]))
    return jsonify(sorted_subjects)


# GET subjects with multiple filters
# GET subjects with multiple filters
@subjects_bp.route('/filter1', methods=['GET'])
def get_subjects_filter1():
    faculties_id = request.args.get('faculties_id', type=int)
    batch = request.args.get('batch', type=int)
    teacher_id = request.args.get('teacher_id', type=int)

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT DISTINCT 
            s.id, 
            s.name, 
            s.faculties_id, 
            f.name AS faculty_name, 
            s.batch
        FROM Subjects s
        LEFT JOIN Faculties f ON s.faculties_id = f.id
        LEFT JOIN teacher_subjects ts ON s.id = ts.subject_id
    """
    conditions = []
    params = []

    if faculties_id is not None:
        conditions.append("s.faculties_id = ?")
        params.append(faculties_id)

    if batch is not None:
        conditions.append("s.batch = ?")
        params.append(batch)

    if teacher_id is not None:
        conditions.append("ts.teacher_id = ?")
        params.append(teacher_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add ordering and limit (SQL Server style)
    query += " ORDER BY s.faculties_id, s.name OFFSET 0 ROWS FETCH NEXT 50 ROWS ONLY"

    cursor.execute(query, tuple(params))
    subjects = rows_to_dict(cursor)

    cursor.close()
    connection.close()

    return jsonify(subjects)


# GET subjects with teachers
@subjects_bp.route('/filter2', methods=['GET'])
def get_subjects_filter2():
    faculties_id = request.args.get('faculties_id', type=int)
    batch = request.args.get('batch', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT 
            s.id AS subject_id,
            s.name AS subject_name,
            s.faculties_id,
            f.name AS faculty_name,
            s.batch,
            t.id AS teacher_id,
            t.name AS teacher_name
        FROM Subjects s
        LEFT JOIN Faculties f ON s.faculties_id = f.id
        LEFT JOIN teacher_subjects ts ON s.id = ts.subject_id
        LEFT JOIN Teachers t ON ts.teacher_id = t.id
    """
    conditions = ["t.id IS NOT NULL"]
    params = []

    if faculties_id is not None:
        conditions.append("s.faculties_id = ?")
        params.append(faculties_id)
    if batch is not None:
        conditions.append("s.batch = ?")
        params.append(batch)
    if teacher_id is not None:
        conditions.append("ts.teacher_id = ?")
        params.append(teacher_id)
    if subject_id is not None:
        conditions.append("s.id = ?")
        params.append(subject_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY t.id, s.name"

    cursor.execute(query, tuple(params))
    rows = rows_to_dict(cursor)
    cursor.close()
    connection.close()

    teacher_map = {}
    subject_map = {}

    for row in rows:
        tid = row['teacher_id']
        sid = row['subject_id']

        if tid not in teacher_map:
            teacher_map[tid] = {"teacher_id": tid, "teacher_name": row['teacher_name']}
        if sid not in subject_map:
            subject_map[sid] = {
                "subject_id": sid,
                "subject_name": row['subject_name'],
                "faculties_id": row['faculties_id'],
                "faculty_name": row['faculty_name'],
                "batch": row['batch']
            }

    return jsonify({
        "teachers": list(teacher_map.values()),
        "subjects": sorted(subject_map.values(), key=lambda x: x['faculties_id'])
    })


# POST a new subject
@subjects_bp.route('', methods=['POST'])
def add_subject():
    data = request.json
    name = data.get('name')
    faculties_id = data.get('faculties_id')
    batch = data.get('batch')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    if faculties_id and batch:
        cursor.execute("""
            INSERT INTO Subjects (name, faculties_id, batch)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
        """, (name, faculties_id, batch))
    elif faculties_id:
        cursor.execute("""
            INSERT INTO Subjects (name, faculties_id)
            OUTPUT INSERTED.id
            VALUES (?, ?)
        """, (name, faculties_id))
    else:
        cursor.execute("""
            INSERT INTO Subjects (name)
            OUTPUT INSERTED.id
            VALUES (?)
        """, (name,))

    subject_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Subject added successfully', 'id': subject_id}), 201


# GET a specific subject
@subjects_bp.route('/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Subjects WHERE id = ?", (subject_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not row:
        return jsonify({'error': 'Subject not found'}), 404

    subject = dict(zip([column[0] for column in cursor.description], row))
    return jsonify(subject)


# PUT update a subject
@subjects_bp.route('/<int:subject_id>', methods=['PUT'])
def update_subject_new(subject_id):
    data = request.json
    name = data.get('name')
    faculties_id = data.get('faculties_id')
    batch = data.get('batch')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    update_fields = []
    update_values = []

    if name:
        update_fields.append("name = ?")
        update_values.append(name)
    if faculties_id:
        update_fields.append("faculties_id = ?")
        update_values.append(faculties_id)
    if batch is not None:
        update_fields.append("batch = ?")
        update_values.append(batch)

    update_values.append(subject_id)

    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400

    query = f"UPDATE Subjects SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, tuple(update_values))
    connection.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({'error': 'Subject not found or no changes made'}), 404

    return jsonify({'message': 'Subject updated successfully'}), 200


@subjects_bp.route('/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Check if subject is used in teacher_subjects
        cursor.execute("SELECT COUNT(*) FROM teacher_subjects WHERE subject_id = ?", (subject_id,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'មិនអាចលុបមុខវិជ្ជានេះបាន ពីព្រោះមានការប្រើប្រាស់ក្នុងក្រុមគ្រូ'}), 400

        # Safe to delete
        cursor.execute("DELETE FROM Subjects WHERE id = ?", (subject_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Subject not found'}), 404

        return jsonify({'message': 'Subject deleted successfully'}), 200

    except Exception as err:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'មានបញ្ហាមិនរំពឹងទុក: ' + str(err)}), 500
    finally:
        cursor.close()
        connection.close()