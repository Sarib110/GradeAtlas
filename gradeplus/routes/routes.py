from flask import Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from database.db import db
from models.models import User, Subject, Semester, Timetable
from services.services import (
    calculate_grade, what_if_simulator, exam_countdown,
    performance_analytics, get_translations, check_achievement,
    danger_alert, subject_analysis, grade_predictor, generate_timetable
)
from utils.helpers import (
    success_response, error_response, get_json_payload,
    validate_required, validate_email, get_current_user, validate_numbers
)

ALLOWED_SYSTEMS = {'pakistan', 'usa', 'uk', 'india', 'germany', 'australia'}
api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def health():
    return success_response({'status': 'ok'}, 'Service healthy')


def _parse_request():
    payload, error = get_json_payload()
    if error:
        return None, error
    return payload, None


def _validate_system(system):
    if not isinstance(system, str) or system.lower() not in ALLOWED_SYSTEMS:
        return False
    return True


def _get_user_or_error():
    current_user = get_current_user()
    if current_user is None:
        return None, error_response('Invalid or expired token.', 401)
    return current_user, None


def _validate_subject_payload(data):
    ok, missing = validate_required(data, ['name', 'marks'])
    if not ok:
        return None, error_response(f'Missing: {missing}', 400)

    if not isinstance(data['name'], str) or not data['name'].strip():
        return None, error_response('Subject name must be a non-empty string.', 400)

    valid_numbers, invalid_key = validate_numbers(data, ['marks', 'total_marks', 'credit_hrs'])
    if not valid_numbers:
        return None, error_response(f'{invalid_key} must be a valid number.', 400)

    marks = float(data['marks'])
    total_marks = float(data.get('total_marks', 100))
    credit_hrs = int(float(data.get('credit_hrs', 3)))

    if total_marks <= 0:
        return None, error_response('total_marks must be greater than zero.', 400)
    if marks < 0 or marks > total_marks:
        return None, error_response('marks must be between 0 and total_marks.', 400)
    if credit_hrs <= 0:
        return None, error_response('credit_hrs must be greater than zero.', 400)

    system = data.get('system', 'pakistan').lower()
    if not _validate_system(system):
        return None, error_response(f'Unsupported grading system: {system}', 400)

    return {
        'name': data['name'].strip(),
        'marks': marks,
        'total_marks': total_marks,
        'credit_hrs': credit_hrs,
        'system': system
    }, None


@api.route('/register', methods=['POST'])
def register():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['username', 'email', 'password'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    if not isinstance(payload['username'], str) or not payload['username'].strip():
        return error_response('Username must be a non-empty string.', 400)

    if not validate_email(payload['email']):
        return error_response('Email must be valid.', 400)

    if len(str(payload['password'])) < 8:
        return error_response('Password must be at least 8 characters long.', 400)

    if User.query.filter_by(email=payload['email'].lower()).first():
        return error_response('Email already registered.', 409)
    if User.query.filter_by(username=payload['username'].strip()).first():
        return error_response('Username taken.', 409)

    user = User(username=payload['username'].strip(), email=payload['email'].lower())
    user.set_password(payload['password'])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)
    return success_response({'user': user.to_dict(), 'access_token': token, 'refresh_token': refresh}, 'Account created!', 201)


@api.route('/login', methods=['POST'])
def login():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['email', 'password'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    user = User.query.filter_by(email=payload['email'].lower()).first()
    if not user or not user.check_password(payload['password']):
        return error_response('Invalid credentials.', 401)

    token = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)
    return success_response({'user': user.to_dict(), 'access_token': token, 'refresh_token': refresh}, 'Login successful!')


@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user, error = _get_user_or_error()
    if error:
        return error
    return success_response(user.to_dict())


@api.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user, error = _get_user_or_error()
    if error:
        return error

    payload, error = _parse_request()
    if error:
        return error

    if 'language' in payload:
        user.language = str(payload['language']).strip() or user.language
    if 'dark_mode' in payload:
        user.dark_mode = bool(payload['dark_mode'])

    db.session.commit()
    return success_response(user.to_dict(), 'Profile updated!')


@api.route('/grade/calculate', methods=['POST'])
def grade_calculate():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['marks', 'system'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    valid_numbers, invalid_key = validate_numbers(payload, ['marks'])
    if not valid_numbers:
        return error_response(f'{invalid_key} must be a valid number.', 400)

    system = str(payload['system']).lower()
    if not _validate_system(system):
        return error_response(f'Unsupported grading system: {system}', 400)

    marks = float(payload['marks'])
    if marks < 0 or marks > 100:
        return error_response('Marks must be between 0 and 100.', 400)

    result = calculate_grade(marks, system)
    return success_response(result)


@api.route('/whatif', methods=['POST'])
def whatif():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['subjects', 'system'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    if not isinstance(payload['subjects'], list) or not payload['subjects']:
        return error_response('Subjects must be a non-empty list.', 400)

    system = str(payload['system']).lower()
    if not _validate_system(system):
        return error_response(f'Unsupported grading system: {system}', 400)

    return success_response(what_if_simulator(payload['subjects'], system))


@api.route('/countdown', methods=['POST'])
def countdown():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['exam_date'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    result = exam_countdown(payload['exam_date'])
    if 'error' in result:
        return error_response(result['error'], 400)
    result['exam_name'] = payload.get('exam_name', 'Exam')
    return success_response(result)


@api.route('/analytics', methods=['GET'])
@jwt_required()
def analytics():
    user, error = _get_user_or_error()
    if error:
        return error

    semesters = Semester.query.filter_by(user_id=user.id).order_by(Semester.created_at).all()
    if not semesters:
        return success_response({'message': 'No semester data yet.'})
    return success_response(performance_analytics(semesters))


@api.route('/semesters', methods=['POST'])
@jwt_required()
def add_semester():
    user, error = _get_user_or_error()
    if error:
        return error

    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['name', 'gpa', 'cgpa'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    valid_numbers, invalid_key = validate_numbers(payload, ['gpa', 'cgpa'])
    if not valid_numbers:
        return error_response(f'{invalid_key} must be a valid number.', 400)

    semester = Semester(
        user_id=user.id,
        name=str(payload['name']).strip(),
        gpa=float(payload['gpa']),
        cgpa=float(payload['cgpa'])
    )
    db.session.add(semester)
    db.session.commit()
    return success_response(semester.to_dict(), 'Semester added!', 201)


@api.route('/semesters', methods=['GET'])
@jwt_required()
def get_semesters():
    user, error = _get_user_or_error()
    if error:
        return error
    return success_response([s.to_dict() for s in Semester.query.filter_by(user_id=user.id).all()])


@api.route('/translations/<language>', methods=['GET'])
def translations(language):
    return success_response(get_translations(language))


@api.route('/achievement', methods=['POST'])
def achievement():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['current_gpa', 'target_gpa'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    valid_numbers, invalid_key = validate_numbers(payload, ['current_gpa', 'target_gpa'])
    if not valid_numbers:
        return error_response(f'{invalid_key} must be a valid number.', 400)

    return success_response(check_achievement(payload['current_gpa'], payload['target_gpa']))


@api.route('/danger-alert', methods=['POST'])
def danger():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['gpa_history'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    if not isinstance(payload['gpa_history'], list):
        return error_response('gpa_history must be a list.', 400)

    return success_response(danger_alert(payload['gpa_history']))


@api.route('/subjects', methods=['POST'])
@jwt_required()
def add_subject():
    user, error = _get_user_or_error()
    if error:
        return error

    payload, error = _parse_request()
    if error:
        return error

    data, error = _validate_subject_payload(payload)
    if error:
        return error

    subject = Subject(user_id=user.id, **data)
    db.session.add(subject)
    db.session.commit()
    return success_response(subject.to_dict(), 'Subject added!', 201)


@api.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    user, error = _get_user_or_error()
    if error:
        return error

    subjects = Subject.query.filter_by(user_id=user.id).all()
    return success_response({'subjects': [s.to_dict() for s in subjects], 'analysis': subject_analysis(subjects) if subjects else {}})


@api.route('/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    user, error = _get_user_or_error()
    if error:
        return error

    subject = Subject.query.filter_by(id=subject_id, user_id=user.id).first()
    if not subject:
        return error_response('Subject not found.', 404)

    db.session.delete(subject)
    db.session.commit()
    return success_response(None, 'Subject deleted!')


@api.route('/predict', methods=['POST'])
def predict():
    payload, error = _parse_request()
    if error:
        return error

    ok, missing = validate_required(payload, ['current_marks', 'current_weight', 'final_weight', 'target_marks'])
    if not ok:
        return error_response(f'Missing: {missing}', 400)

    valid_numbers, invalid_key = validate_numbers(payload, ['current_marks', 'current_weight', 'final_weight', 'target_marks'])
    if not valid_numbers:
        return error_response(f'{invalid_key} must be a valid number.', 400)

    system = str(payload.get('system', 'pakistan')).lower()
    if not _validate_system(system):
        return error_response(f'Unsupported grading system: {system}', 400)

    return success_response(grade_predictor(payload['current_marks'], payload['current_weight'], payload['final_weight'], payload['target_marks'], system))


@api.route('/timetable/generate', methods=['POST'])
@jwt_required()
def generate_tt():
    user, error = _get_user_or_error()
    if error:
        return error

    subjects = Subject.query.filter_by(user_id=user.id).all()
    if not subjects:
        return error_response('Add subjects first.', 400)

    timetable_data = generate_timetable(subjects)
    Timetable.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    for entry in timetable_data:
        db.session.add(Timetable(user_id=user.id, day=entry['day'], subject_name=entry['subject_name'], hours=entry['hours'], priority=entry['priority']))
    db.session.commit()
    return success_response(timetable_data, 'Timetable generated!')


@api.route('/timetable', methods=['GET'])
@jwt_required()
def get_timetable():
    user, error = _get_user_or_error()
    if error:
        return error
    return success_response([s.to_dict() for s in Timetable.query.filter_by(user_id=user.id).all()])


@api.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    user, error = _get_user_or_error()
    if error:
        return error

    subjects = Subject.query.filter_by(user_id=user.id).all()
    semesters = Semester.query.filter_by(user_id=user.id).order_by(Semester.created_at).all()
    latest_cgpa = semesters[-1].cgpa if semesters else 0
    latest_gpa = semesters[-1].gpa if semesters else 0
    analysis = subject_analysis(subjects) if subjects else {}
    alert = danger_alert([s.gpa for s in semesters]) if len(semesters) >= 2 else {'alert': False}
    return success_response({
        'total_subjects': len(subjects),
        'total_semesters': len(semesters),
        'latest_gpa': latest_gpa,
        'latest_cgpa': latest_cgpa,
        'strong_subjects': len(analysis.get('strong_subjects', [])),
        'weak_subjects': len(analysis.get('weak_subjects', [])),
        'danger_alert': alert,
        'username': user.username
    })
