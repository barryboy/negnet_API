#  -*- coding: utf-8 -*-

from flask_restful import Api
from . import api01
from .resources.token import Token
from .resources.user import NewUser, User, Users
from .resources.project import Project, Projects
from .resources.user_in_project import UserInProject
from .resources.utterance import Utterance, Utterances
from .resources.selection import Selection, Selections, Selections_by_type
from .resources.link import Link, Links
from .resources.node import Node, Nodes

api = Api(api01)

#  *** TOKEN ***
#   GET
api.add_resource(Token, '/api01/token/')

# *** USER ***
#   POST
api.add_resource(NewUser, '/newuser/', endpoint='new_user')
#   GET PUT DELETE
api.add_resource(NewUser, '/user/', endpoint='user')
#   GET
api.add_resource(Users, '/users/', endpoint='all_users')
api.add_resource(Users, '/users/<p_id>/', endpoint='users_in_project')

# *** PROJECT ***
#   POST
api.add_resource(Project, '/project/', endpoint='new_project')
#   GET PUT DELETE
api.add_resource(Project, '/project/<p_id>/', endpoint='project')
#   GET
api.add_resource(Projects, '/projects/', endpoint='projects')

#  *** USER IN PROJECT ***
#   GET
api.add_resource(UserInProject, '/userinproject/<p_id>/',
                 endpoint='user_in_project')

#  *** UTTERANCE ***
#   GET
api.add_resource(Utterance, '/utterance/<id>/', endpoint='utterance')
api.add_resource(Utterances, '/utterances/<p_id>/', endpoint='utterances')

#  *** SELECTION ***
#   POST
api.add_resource(Selection, '/selection/', endpoint='new_selection')
#   GET PUT DELETE
api.add_resource(Selection, '/selection/<s_id>/', endpoint='selection')
#   GET
api.add_resource(Selections, '/selections/<p_id>/', endpoint='selections')
api.add_resource(Selections_by_type, '/selections/<p_id>/<type>/',
                 endpoint='selections_by_type')

#  *** NODE ***
#   GET
api.add_resource(Node, '/api01/node/<n_id>/')
api.add_resource(Nodes, '/api01/nodes/<p_id>/')

#  *** LINK ***
#   GET
api.add_resource(Link, '/api01/link/<l_id>/')
api.add_resource(Links, '/api01/links/<p_id>/')
