from flask_login import LoginManager, UserMixin


class User(UserMixin):

    def __init__(self, user_id):
        self.id = user_id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
return '<User %r>' % (self.id)
