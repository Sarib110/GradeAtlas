from flask import Blueprint
from flask_jwt_extended import jwt_required
from models.models import User
from utils.helpers import admin_required, success_response

admin_api = Blueprint('admin_api', __name__)


@admin_api.route('/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return success_response([user.to_dict() for user in users])
