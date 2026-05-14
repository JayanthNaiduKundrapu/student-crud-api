from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.student import Student
from app.utils.logger import setup_logger



student_bp = Blueprint(
    "students",
    __name__,
    url_prefix="/api/v1/students"
)

logger = setup_logger()

@student_bp.route("", methods=["POST"])
def create_student():

    logger.info("Create student endpoint called")
    data = request.get_json()

    # Validation for input data
    required_fields = ["name", "email", "age"]

    for field in required_fields:

        if field not in data:

            logger.error(f"Missing field: {field}")

            return jsonify({
                "error": f"{field} is required"
                }), 400
        
        if data["age"] <= 0:
            return jsonify({
                "error": "Age must be greater than 0"
                }), 400
        
        if "@" not in data["email"]:
            return jsonify({
                "error": "Invalid email"
                }), 400

    student = Student(
        name=data["name"],
        email=data["email"],
        age=data["age"]
    )

    db.session.add(student)
    db.session.commit()

    logger.info(f"Student created with ID {student.id}")

    return jsonify(student.to_dict()), 201

@student_bp.route("", methods=["GET"])
def get_students():

    logger.info("Fetching all students")
    students = Student.query.all()

    result = []

    for student in students:
        result.append(student.to_dict())

    logger.info("Fetched all students successfully")

    return jsonify(result), 200

@student_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id):

    student = Student.query.get(student_id)

    logger.info(f"Fetching student with ID {student.id}")

    if not student:
        logger.error(f"Student with ID {student_id} not found")
        return jsonify({
            "error": "Student not found"
        }), 404

    logger.info(f"Fetched student with ID {student_id} successfully")

    return jsonify(student.to_dict()), 200

@student_bp.route("/<int:student_id>", methods=["PUT"])
def update_student(student_id):

    student = Student.query.get(student_id)

    logger.info(f"Fetching student with ID {student.id}")

    if not student:
        logger.error(f"Student with ID {student_id} not found")
        return jsonify({
            "error": "Student not found"
        }), 404

    data = request.get_json()

    student.name = data["name"]
    student.email = data["email"]
    student.age = data["age"]

    db.session.commit()

    logger.info(f"Student with ID {student_id} updated successfully")

    return jsonify({
        "message": "Student updated successfully"
    }), 200

@student_bp.route("/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    student = Student.query.get(student_id)

    logger.info(f"Deleting student with ID {student_id}")

    if not student:
        logger.error(f"Student with ID {student_id} not found")
        return jsonify({
            "error": "Student not found"
        }), 404

    db.session.delete(student)

    db.session.commit()

    logger.info(f"Student with ID {student_id} deleted successfully")

    return jsonify({
        "message": "Student deleted successfully"
    }), 200 