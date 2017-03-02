# -*- coding: utf-8 -*-
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from flask import g, abort, current_app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    user = verify_auth_token(username_or_token)
    if not user:
        user = g.mongo.db.user.find_one({'username': username_or_token})
        if not user or not check_password_hash(user['password_hash'], password):
            return False
    g.user = user
    return True


def generate_auth_token(u_id, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'id': u_id})


def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    user = g.mongo.db.user.find_one({'u_id': data['id']})
    return user
