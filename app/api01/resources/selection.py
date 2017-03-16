# -*- coding: utf-8 -*-

import sys
import logging
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import g, abort
from bson.json_util import ObjectId
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

selection_fields = {
    's_id': fields.String,
    'utt_id': fields.String,
    'p_id': fields.String,
    'u_id': fields.String,
    'from': fields.Integer,
    'to': fields.Integer,
    'type': fields.String,
    'comment': fields.String
}


class Selection(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        self.general_parser = reqparse.RequestParser()
        self.bounds_parser = reqparse.RequestParser()
        self.network_parser = reqparse.RequestParser()
        self.put_parser = reqparse.RequestParser()
        self.general_parser.add_argument('p_id', type=str, location='json',
                                         help='No p_id field provided')
        self.general_parser.add_argument('name', type=str, location='json',
                                         help='No name field provided')
        self.general_parser.add_argument('comment', type=str, location='json',
                                         help='No comment provided')
        self.general_parser.add_argument('type', type=str, location='json',
                                         required=True,
                                         help='No type field provided')
        self.put_parser.add_argument('action', type=str, location='json',
                                     required=True,
                                     help='No action field provided')
        self.bounds_parser.add_argument('start_utt_id', type=str,
                                        location='json',
                                        required=True,
                                        help='No start_utt_id provided')
        self.bounds_parser.add_argument('end_utt_id', type=str,
                                        location='json',
                                        required=True,
                                        help='No end_utt_id provided')
        self.bounds_parser.add_argument('start_pos', type=int,
                                        location='json',
                                        required=True,
                                        help='No start_pos provided')
        self.bounds_parser.add_argument('end_pos', type=int,
                                        location='json',
                                        required=True,
                                        help='No end_pos provided')
        self.link_parser.add_argument('node_from', type=str, location='json',
                                      help='No node_from position provided')
        self.link_parser.add_argument('node_to', type=str, location='json',
                                      help='No node_to position provided')
        super(Selection, self).__init__()

# GET
    @marshal_with(selection_fields)
    def get(self, s_id):
        logging.info('Getting selection ' + s_id)
        selection = g.mongo.db.selection.find_one_or_404({"_id": s_id})
        logging.info(selection)
        return selection, 200

# POST
    @marshal_with(selection_fields)
    def post(self):
        u_id = g.user['u_id']
        logging.info('Creating new selection')
        s_id = ObjectId()
        args = self.general_parser.parse_args()
        bounds_args = self.bounds_parser.parse_args()
        link_args = self.link_parser.parse_args()
        selection = {"_id": s_id,
                     "s_id": str(s_id),
                     "p_id": args.p_id,
                     "u_id": u_id,
                     "type": args.type,
                     "comment": args.comment,
                     "start_utt_id": bounds_args.start_utt_id,
                     "end_utt_id": bounds_args.end_utt_id,
                     "start_pos": bounds_args.start_pos,
                     "end_pos": bounds_args.end_pos}
        logging.info('Saving selection ' + s_id)
        logging.info(selection)
        g.mongo.db.selection.insert_one(selection)
        if args.type == "node":
            node = {"_id": s_id,
                    "n_id": str(s_id),
                    "p_id": args.p_id,
                    "u_id": u_id,
                    "name": args.name}
            logging.info('Saving node ' + s_id)
            logging.info(node)
            g.mongo.db.node.insert_one(node)

        elif args.type == "link":
            link = {"_id": s_id,
                    "l_id": str(s_id),
                    "p_id": args.p_id,
                    "u_id": u_id,
                    "name": args.name,
                    "value": 1,
                    "node_from": link_args.node_from,
                    "node_to": link_args.node_to}
            logging.info('Saving link ' + s_id)
            logging.info(link)
            g.mongo.db.link.insert_one(link)
        else:
            abort(400)
        return selection, 201

# PUT
    @marshal_with(selection_fields)
    def put(self, s_id):
        logging.info('Altering selection data')
        logging.info('BEFORE:')
        selection = g.mongo.db.selection.find_one_or_404({"s_id": s_id})
        logging.info(selection)
        args = self.general_parser.parse_args()
        put_args = self.put_parser.parse_args()
        bounds_args = self.bounds_parser.parse_args()
        if put_args.action == 'change_bounds':
            logging.info('Changing selection bounds')
            new_bounds = {"start_utt_id": bounds_args.start_utt_id,
                          "end_utt_id": bounds_args.end_utt_id,
                          "end_utt_id": bounds_args.start_pos,
                          "end_utt_id": bounds_args.end_pos}
            g.mongo.db.selection.update({"s_id": s_id},
                                        {"$set": new_bounds})
        elif put_args.action == 'change_comment':
            logging.info('Changing selection comment')
            g.mongo.db.selection.update({"s_id": s_id},
                                        {"$set": {"comment": args.comment}})
        else:
            logging.info('Invalid action')
            abort(400)
        selection = g.mongo.db.selection.find_one({"s_id": s_id})
        logging.info('AFTER:')
        logging.info(selection)
        return selection, 200

# DELETE
    @marshal_with(selection_fields)
    def delete(self, s_id):
        logging.info('Deleting selection ' + s_id)
        g.mongo.db.selection.remove({"s_id": s_id})
        logging.info('Deleting node ' + s_id)
        g.mongo.db.node.remove({"s_id": s_id})
        logging.info('Deleting link ' + s_id)
        g.mongo.db.link.remove({"s_id": s_id})

        logging.info('Removing orphaned links:')
        links_to_remove = g.mongo.db.link.find({"$or": [{"node_from": s_id},
                                                        {"node_to": s_id}]})
        for link in links_to_remove:
            logging.info(link)
            g.mongo.db.link.remove({"l_id": link['l_id']})
            g.mongo.db.selection.remove({"s_id": link['s_id']})
        return {'result': True}, 200


class Selections(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Selections, self).__init__()

# GET
    @marshal_with(selection_fields)
    def get(self, p_id):
        u_id = g.user['u_id']
        logging.info('Getting all users selections in the project')
        selections = g.mongo.db.selection.find({"p_id": p_id,
                                                "u_id": u_id})
        logging.info(selections)
        return selections, 200


class Selections_by_type(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Selections_by_type, self).__init__()

# GET
    @marshal_with(selection_fields)
    def get(self, p_id, type):
        u_id = g.user['u_id']
        logging.info('Getting users selections of a given type in the project')
        if type not in ["node", "link"]:
            logging.info('type must be either node or link, was: ' + type)
            abort(404)
        selections = g.mongo.db.selection.find({"p_id": p_id,
                                                "u_id": u_id,
                                                "type": type})
        logging.info(selections)
        return selections, 200
