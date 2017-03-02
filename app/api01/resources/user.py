# -*- coding: utf-8 -*-

import sys
import logging
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import g, abort
from bson.json_util import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..authentication.authentication import auth

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

user_fields = {
    'u_id': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String,
    'date_joined': fields.DateTime(dt_format='rfc822')
}


class NewUser(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first_name', type=str, location='json',
                                 help='No first_name field provided')
        self.parser.add_argument('last_name', type=str, location='json',
                                 help='No last_name field provided')
        self.parser.add_argument('username', type=str, location='json',
                                 help='No username provided')
        self.parser.add_argument('password', type=str, location='json',
                                 help='No password provided')
        super(User, self).__init__()

# POST
    @marshal_with(user_fields)
    def post(self):
        logging.info('Creating a user')
        args = self.parser.parse_args()
        logging.info(args)
        if g.mongo.db.user.find({"username": args.username}).count() > 0:
            logging.info('Username ' + args.username + 'is already in use')
            abort(409)
        id = ObjectId()
        now = datetime.utcnow()
        user = {
            '_id': id,
            'u_id': str(id),
            'first_name': args.first_name,
            'last_name': args.last_name,
            'username': args.username,
            'password_hash': generate_password_hash(args.password),
            'date_joined': now
        }
        g.mongo.db.user.insert_one(user)
        logging.info(user)
        return user, 201


class User(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first_name', type=str, location='json',
                                 help='No first_name field provided')
        self.parser.add_argument('last_name', type=str, location='json',
                                 help='No last_name field provided')
        self.parser.add_argument('password', type=str, location='json',
                                 help='No password provided')
        self.parser.add_argument('new_password', type=str, location='json',
                                 help='No new_password provided')
        super(User, self).__init__()

# GET
    @marshal_with(user_fields)
    def get(self):
        u_id = g.user['u_id']
        logging.info('Getting user ' + u_id)
        user = g.mongo.db.user.find_one({"u_id": u_id})
        if not user:
            logging.info('Could not find user ' + u_id)
            abort(404)
        logging.info(user)
        return user, 200

# PUT
    @marshal_with(user_fields)
    def put(self):
        u_id = g.user['u_id']
        logging.info('Altering user data')
        logging.info('BEFORE:')
        user = g.mongo.db.user.find_one_or_404({'u_id': u_id})
        logging.info(user)
        args = self.parser.parse_args()
        if args.password and args.new_password:
            logging.info('Changing password')
            if not check_password_hash(user['password_hash'], args.password):
                logging.info('Invalid password')
                abort(401)
            new_password = generate_password_hash(args.new_password)

            g.mongo.db.user.update({'u_id': u_id},
                                   {"$set": {'password_hash': new_password}})
        elif args.first_name or args.last_name:
            if args.first_name:
                logging.info('Changing first name')
                g.mongo.db.user.update({'u_id': u_id},
                                       {"$set":
                                        {'first_name': args.first_name}})
            if args.last_name:
                logging.info('Changing last name')
                g.mongo.db.user.update({'u_id': u_id},
                                       {"$set": {'last_name': args.last_name}})
        else:
            logging.info('Inconsistent or absent arguments')
            abort(404)
        user = g.mongo.db.user.find_one_or_404({'u_id': u_id})
        logging.info('AFTER:')
        logging.info(user)
        return user, 200

# DELETE
    def delete(self):
        u_id = g.user['u_id']
        logging.info('Deleting user ' + u_id)
        g.mongo.db.user.find_one_or_404({"u_id": u_id})
        if g.mongo.db.user_in_project.find({"u_id": u_id}).count() > 0:
            g.mongo.db.user_in_project.remove({"u_id": u_id})
        g.mongo.db.user.remove({"u_id": u_id})
        return {'result': True}, 200


class Users(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        super(Users, self).__init__()

# GET
    @marshal_with(user_fields)
    def get(self, p_id=None):
        if p_id is None:
            logging.info('Getting all users')
            users = list(g.mongo.db.user.find())
        else:
            logging.info('Getting users in project ' + p_id)
            u_in_p = g.mongo.db.user_in_project.find({"p_id": p_id},
                                                     {"u_id": 1, "_id": 0})
            u_ids = list()
            for id in list(u_in_p):
                u_ids.append(id['u_id'])
                users = g.mongo.db.user.find({"u_id": {"$in": u_ids}})
        logging.info(users)
        return users, 200
