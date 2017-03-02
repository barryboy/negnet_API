# -*- coding: utf-8 -*-

import sys
import logging
from flask_restful import Resource, fields, marshal_with
from flask import g
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


link_fields = {
    'l_id': fields.String,
    'p_id': fields.String,
    'u_id': fields.String,
    'name': fields.String,
    'value': fields.Integer,
    'node_from': fields.String,
    'node_to': fields.String
}


class Link(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Link, self).__init__()

# GET
    @marshal_with(link_fields)
    def get(self, l_id):
        logging.info('Getting link ' + l_id)
        link = g.mongo.db.link.find_one_or_404({"l_id": l_id})
        logging.info(link)
        return link, 200


class Links(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Links, self).__init__()

# GET
    @marshal_with(link_fields)
    def get(self, p_id):
        u_id = g.user['u_id']
        logging.info('Getting links by user ' + u_id + ' and project ' + p_id)
        links = g.mongo.db.link.find({"l_id": {"p_id": p_id,
                                               "u_id": u_id}})
        logging.info(links)
        return links, 200
