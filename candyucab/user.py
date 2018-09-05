from candyucab import login_manager
from candyucab.db import Database
import psycopg2,psycopg2.extras


@login_manager.user_loader
def load_user(user_id):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT * from usuario WHERE u_id = %s;",(int(user_id),))
    user = cur.fetchone()
    return User(user)

class User (object):
    def __init__(self,user):
        self._user = user;
    def __getattr__(self,k):
        try:
            return self._user[k]
        except KeyError:
            raise AttributeError()
    def get_id(self):
        return self._user['u_id']
    def is_active(self):
        return self._user['active']
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return True
    def is_admin(self):
        return False
