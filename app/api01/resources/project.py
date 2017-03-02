# -*- coding: utf-8 -*-

import os
import sys
import logging
import yaml
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import g, abort, current_app
from bson.json_util import ObjectId
from werkzeug import secure_filename, datastructures
from datetime import datetime
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


project_fields = {
    'p_id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'date_created': fields.DateTime(dt_format='rfc822')
}


class Project(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('u_id', type=str, location='json',
                                 help='No u_id field provided')
        self.parser.add_argument('action', type=str, location='json',
                                 help='No action field provided')
        self.parser.add_argument('name', type=str, location='json',
                                 help='No name field provided')
        self.parser.add_argument('description', type=str, location='json',
                                 help='No name field provided')
        self.parser.add_argument('data',
                                 type=datastructures.FileStorage,
                                 help='No transcription provided',
                                 location='files')
        super(Project, self).__init__()

# GET
    @marshal_with(project_fields)
    def get(self, p_id):
        logging.info('Getting project' + p_id)
        project = g.mongo.db.project.find_one_or_404({"p_id": p_id})
        logging.info(project)
        return project, 200

# POST
    @marshal_with(project_fields)
    def post(self):
        logging.info('Creating new project')
        args = self.parser.parse_args()
        if not args.uid:
            logging.info('No u_id specified')
            abort(400)
        p_id = ObjectId()
        now = datetime.utcnow()
        logging.info('Adding the project entry')
        project = {"_id": p_id,
                   "p_id": str(p_id),
                   "name": args.name,
                   "description": args.description,
                   "date_created": now}
        logging.info(project)
        g.mongo.db.project.insert_one(project)
        logging.info('Adding the user_in_project entry')
        user_in_project = {"u_id": args.u_id,
                           "p_id": str(p_id),
                           "leader": True,
                           "joined": now}
        logging.info(user_in_project)
        g.mongo.db.user_in_project.insert_one(user_in_project)
        return project, 201

# PUT
    @marshal_with(project_fields)
    def put(self, p_id):
        logging.info('Altering project data')
        args = self.parser.parse_args()
        logging.info('BEFORE:')
        project = g.mongo.db.project.find_one_or_404({"p_id": p_id})
        logging.info(project)
        if args.data:
            logging.info('Adding utterances data')
            self.insert_utterances(p_id, args.data)
        elif args.action == 'add_user':
            logging.info('Adding a user')
            now = datetime.utcnow()
            g.mongo.db.user_in_project.insert_one({"u_id": args.u_id,
                                                   "p_id": p_id,
                                                   "leader": False,
                                                   "joined": now})
        elif args.action == 'remove_user':
            logging.info('Removing a user')
            if args.u_id:
                g.mongo.db.user_in_project.delete_one({"u_id": args.u_id,
                                                       "p_id": p_id})
            else:
                logging.info('Insuficient data')
                abort(400)

        elif args.action == 'edit':
            logging.info('Altering name and/or description')
            if args.name or args.desctiption:
                if args.name:
                    g.mongo.db.project.update({'p_id': p_id},
                                              {"$set": {'name': args.name}})
                if args.description:
                    g.mongo.db.project.update({'p_id': p_id},
                                              {"$set":
                                               {'description':
                                                args.description}})
            else:
                logging.info('Insuficient data')

        else:
            logging.info('No action specified')
            abort(400)
        logging.info('AFTER:')
        project = g.mongo.db.project.find_one({"p_id": p_id})
        logging.info(project)
        return project, 200

    def insert_utterances(self, p_id, data):
        logging.info('Inserting utterances')
        filename = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                secure_filename(data.filename))
        logging.info('Data file: ' + filename)
        data.save(filename)
        stream = open(filename, "r")
        yaml_object = yaml.load(stream)
        utterances = yaml_object['content']
        for u in utterances:
            utt_id = ObjectId()
            utterance = {
                '_id': utt_id,
                'utt_id': str(utt_id),
                'p_id': p_id,
                'step': u['step'],
                'party': u['p'],
                'content': u['u']
            }
            g.mongo.db.utterance.insert_one(utterance)
            logging.info('Inserted utterance: ' + utterance)

# DELETE
    def delete(self, p_id):
        logging.info('Deleting project ' + p_id)
        g.mongo.db.project.find_one_or_404({"p_id": p_id})
        logging.info('Deleting projects utterances')
        g.mongo.db.utterance.delete_many({"p_id": p_id})
        logging.info('Deleting projects selections')
        g.mongo.db.selection.delete_many({"p_id": p_id})
        logging.info('Deleting projects users info')
        g.mongo.db.user_in_project.delete_many({"p_id": p_id})
        logging.info('Deleting project itself')
        g.mongo.db.project.delete_one({"p_id": p_id})
        return {'result': True}, 200


class Projects(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Projects, self).__init__()

# GET
    @marshal_with(project_fields)
    def get(self):
        u_id = g.user['u_id']
        logging.info('Getting user ' + u_id + ' projects')
        u_in_p = g.mongo.db.user_in_project.find({"u_id": u_id},
                                                 {"p_id": 1, "_id": 0})
        p_ids = list()
        for id in list(u_in_p):
            p_ids.append(id['p_id'])
        projects = g.mongo.db.project.find({"p_id": {"$in": p_ids}})
        logging.info(projects)
        return projects, 200
