# -*- coding: utf-8 -*-

import sys
import logging
from flask_restful import Resource, fields, marshal_with
from flask import g
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


node_fields = {
    'n_id': fields.String,
    'p_id': fields.String,
    'u_id': fields.String,
    'name': fields.String
}


class Node(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Node, self).__init__()

# GET
    @marshal_with(node_fields)
    def get(self, n_id):
        logging.info('Getting node ' + n_id)
        node = g.mongo.db.node.find_one_or_404({"n_id": n_id})
        logging.info(node)
        return node, 200


class Nodes(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Nodes, self).__init__()

# GET
    @marshal_with(node_fields)
    def get(self, p_id):
        u_id = g.user['u_id']
        logging.info('Getting nodes by user ' + u_id + ' and project ' + p_id)
        nodes = list(g.mongo.db.node.find({"p_id": p_id,
                                           "u_id": u_id}))
        logging.info(nodes)
        return nodes, 200
