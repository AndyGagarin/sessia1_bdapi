from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from config import Config
from Models import User, Document, Comments, Employee, Department, Position, TrainingEvent, VacationEvent, AbsenceEvent, db
import re
import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@app.route('/api/v1/SignUp', methods=['POST'])
def signup():
    data = request.get_json()

    # Проверка наличия обязательных полей
    if not data or 'name' not in data or 'password' not in data:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Неверный формат запроса',
            'errorCode': '1001'
        }), 400

    # Проверка, что имя не занято
    existing_user = User.query.filter_by(name=data['name']).first()
    if existing_user:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Пользователь с таким именем уже существует',
            'errorCode': '1003'
        }), 400

    # Хеширование пароля
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Создание нового пользователя
    new_user = User(
        name=data['name'],
        password=hashed_password
    )

    # Сохранение пользователя в базе данных
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Пользователь зарегистрирован успешно'
    }), 201


@app.route('/api/v1/SignIn', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'name' not in data or 'password' not in data:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Неверный формат запроса',
            'errorCode': '1001'
        }), 400

    user = User.query.filter_by(name=data['name']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Неверные учетные данные',
            'errorCode': '1002'
        }), 403

    access_token = create_access_token(identity=user.id)
    return jsonify({'token': access_token}), 200


@app.route('/api/v1/Documents', methods=['GET'])
@jwt_required()
def get_documents():
    documents = Document.query.all()
    return jsonify([doc.to_dict() for doc in documents]), 200

@app.route('/api/v1/Document/<int:document_id>/Comments', methods=['GET'])
@jwt_required()
def get_document_comments(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Документ не найден',
            'errorCode': '2002'
        }), 404

    comments = Comments.query.filter_by(document_id=document_id).all()
    return jsonify([comment.to_dict() for comment in comments]), 200

@app.route('/api/v1/employees', methods=['GET'])
@jwt_required()
def get_employees():
    employees = Employee.query.all()
    return jsonify([{
        'id': emp.id,
        'fullname': emp.fullname,
        'department': emp.department.name,
        'position': emp.position.name,
        'work_phone_number': emp.work_phone_number,
        'phone_number': emp.phone_number,
        'office_number': emp.office_number,
        'email': emp.email
    } for emp in employees]), 200

@app.route('/api/v1/employees/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Сотрудник не найден',
            'errorCode': '3002'
        }), 404

    return jsonify({
        'id': employee.id,
        'fullname': employee.fullname,
        'department': employee.department.name,
        'position': employee.position.name,
        'work_phone_number': employee.work_phone_number,
        'phone_number': employee.phone_number,
        'office_number': employee.office_number,
        'email': employee.email,
        'birth_day': employee.birth_day.strftime('%Y-%m-%d') if employee.birth_day else None,
        'manager': employee.manager.fullname if employee.manager else None,
        'assistant': employee.assistant.fullname if employee.assistant else None,
        'other': employee.Other
    }), 200

@app.route('/api/v1/departments', methods=['GET'])
@jwt_required()
def get_departments():
    departments = Department.query.all()
    return jsonify([{
        'id': dept.id,
        'name': dept.name,
        'description': dept.description,
        'head': dept.head.fullname if dept.head else None,
        'employees_count': len(dept.employees)
    } for dept in departments]), 200

@app.route('/api/v1/departments/<int:department_id>/employees', methods=['GET'])
@jwt_required()
def get_department_employees(department_id):
    department = Department.query.get(department_id)
    if not department:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Подразделение не найдено',
            'errorCode': '3005'
        }), 404

    return jsonify([{
        'id': emp.id,
        'fullname': emp.fullname,
        'position': emp.position.name,
        'work_phone_number': emp.work_phone_number,
        'email': emp.email,
        'office_number': emp.office_number
    } for emp in department.employees]), 200

@app.route('/api/v1/employees/<int:employee_id>/events', methods=['GET'])
@jwt_required()
def get_employee_events(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Сотрудник не найден',
            'errorCode': '3007'
        }), 404

    training_events = TrainingEvent.query.filter_by(employee_id=employee_id).all()
    absence_events = AbsenceEvent.query.filter_by(employee_id=employee_id).all()
    vacation_events = VacationEvent.query.filter_by(employee_id=employee_id).all()

    return jsonify({
        'training': [event.to_dict() for event in training_events],
        'absence': [event.to_dict() for event in absence_events],
        'vacation': [event.to_dict() for event in vacation_events]
    }), 200

@app.route('/api/v1/employees/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Сотрудник не найден',
            'errorCode': '3009'
        }), 404

    data = request.get_json()

    required_fields = ['fullname', 'work_phone_number', 'office_number', 'email',
                       'department_id', 'position_id']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'timestamp': int(datetime.datetime.now().timestamp()),
                'message': f'Отсутствует обязательное поле {field}',
                'errorCode': '3010'
            }), 400

    phone_pattern = r'^[0-9+() #-]{1,20}$'
    if not re.match(phone_pattern, data['work_phone_number']):
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Неверный формат рабочего телефона',
            'errorCode': '3011'
        }), 400

    if 'phone_number' in data and data['phone_number']:
        if not re.match(phone_pattern, data['phone_number']):
            return jsonify({
                'timestamp': int(datetime.datetime.now().timestamp()),
                'message': 'Неверный формат личного телефона',
                'errorCode': '3012'
            }), 400

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Неверный формат email',
            'errorCode': '3013'
        }), 400

    for key, value in data.items():
        if hasattr(employee, key):
            setattr(employee, key, value)

    db.session.commit()
    return jsonify({'message': 'Данные сотрудника обновлены успешно'}), 200

@app.route('/api/v1/Document/<int:document_id>/Comment', methods=['POST'])
@jwt_required()
def add_document_comment(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Документ не найден',
            'errorCode': '2004'
        }), 404

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({
            'timestamp': int(datetime.datetime.now().timestamp()),
            'message': 'Неверный формат запроса',
            'errorCode': '2005'
        }), 400

    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(id=user_id).first()

    new_comment = Comments(
        document_id=document_id,
        text=data['text'],
        author_id=employee.id,
        position_id=employee.position_id
    )

    db.session.add(new_comment)
    document.has_comments = True
    db.session.commit()

    return jsonify(new_comment.to_dict()), 201

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'timestamp': int(datetime.datetime.now().timestamp()),
        'message': 'Ресурс не найден',
        'errorCode': '1004'
    }), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)