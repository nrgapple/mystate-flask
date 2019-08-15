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
    data = request.get_json() or {}
    if 'name' not in data or 'lat' not in data or 'lng' not in data:
        return bad_request('must include name, lat, and lng fields')
    if POI.query.filter_by(name=data['name']).first():
        return bad_request('please use a different name')
    poi = POI()
    poi.from_dict(data)
    db.session.add(poi)
    db.session.commit()
    response = jsonify(poi.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_poi', id=poi.id)
    return response

    

@bp.route('/pois/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_poi(id):
    poi = POI.query.get_or_404(id)
    data = request.get_json() or {}
    poi.from_dict(data)
    db.session.commit()
    return jsonify(poi.to_dict())