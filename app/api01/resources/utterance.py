# -*- coding: utf-8 -*-

import sys
import logging
from flask_restful import Resource, fields, marshal_with
from flask import g
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

utterance_fields = {
    'utt_id': fields.String,
    'p_id': fields.String,
    'step': fields.Integer,
    'party': fields.String,
    'content': fields.String
}


class Utterance(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Utterance, self).__init__()

# GET
    @marshal_with(utterance_fields)
    def get(self, utt_id):
        logging.info('Getting utterance ' + utt_id)
        utterance = g.mongo.db.utterance.find_one({"utt_id": utt_id})
        logging.info(utterance)
        return utterance, 200


class Utterances(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Utterances, self).__init__()

# GET
    @marshal_with(utterance_fields)
    def get(self, p_id):
        logging.info('Getting utterances from  project ' + p_id)
        utterances = list(g.mongo.db.utterance.find({"p_id": p_id}))
        logging.info(utterances)
        return utterances, 200
