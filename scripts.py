from flask.ext.script import Command, Option
from App.models import db, User

class AddUser(Command):
    "add a user"

    def get_options(self):
        return [
            Option('-n', '--name', dest='name'),
            Option('-p', '--password', dest='password'),
        ]

    def run(self, name, password):
        if not name:
            print "missing name"
            return
        if not password:
            print "missing password"
            return
        user = User(name, password)
        print "username: ", name
        if password: print "password: ", password

        db.session.add(user)
        db.session.commit()
