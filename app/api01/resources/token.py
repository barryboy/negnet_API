# -*- coding: utf-8 -*-

from flask_restful import Resource, fields
from flask import g, jsonify
from ..authentication.authentication import auth, generate_auth_token

token_fields = {
    'u_id': fields.String,
    'token': fields.String,
    'duration': fields.Integer
}


class Token(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Token, self).__init__()

    def get(self):
        u_id = g.user['u_id']
        token = generate_auth_token(u_id, 86400)
        return jsonify({'u_id': u_id,
                        'token': token.decode('ascii'),
                        'duration': 86400})
