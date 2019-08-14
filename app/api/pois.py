'''
POI API End Points
'''

from flask import (jsonify, request, url_for, g, abort)
from app import db
from app.models import POI
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth

@bp.route('/pois/<int:id>', methods=['GET'])
@token_auth.login_required
def get_poi(id):
    return jsonify(POI.query.get_or_404(id).to_dict())

@bp.route('/pois', methods=['GET'])
@token_auth.login_required
def get_pois():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = POI.to_collection_dict(POI.query, page, per_page, 'api.get_pois')
    return jsonify(data)

@bp.route('/pois', methods=['POST'])
@token_auth.login_required
def create_poi():
    pass

    

@bp.route('/poi/<int:id>', methods=['PUT'])
def update_poi():
    pass