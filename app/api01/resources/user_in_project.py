# -*- coding: utf-8 -*-

import sys
import logging
from flask_restful import Resource, fields, marshal_with
from flask import g
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

user_in_project_fields = {
    'p_id': fields.String,
    'u_id': fields.String,
    'leader': fields.Boolean,
    'joined': fields.DateTime(dt_format='rfc822')
}


class UserInProject(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(UserInProject, self).__init__()

# GET
    @marshal_with(user_in_project_fields)
    def get(self, p_id):
        u_id = g.user['u_id']
        logging.info('Getting a user in project')
        user_in_project = g.mongo.db.user_in_project.find_one_or_404(
            {"u_id": u_id,
             "p_id": p_id})
        logging.info(user_in_project)
        return user_in_project, 200
