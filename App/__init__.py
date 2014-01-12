
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate
from flask.ext.login import current_user
from flask import g

from App.models import db, login_manager
from App.views import ThingsAPIView, IndexView

##import views here

import config_dev

def create_app(config={}):
    app = Flask(__name__)
    app.config.from_object('App.config_dev')
    app.config.update(config)
    db.init_app(app)

    register_all_views(app)
    login_manager.init_app(app)
    app.before_request(before_request)

    return app

def reg_view(app, view, endpoint, url, methods=["GET", "POST"], defaults=None):
    view.APIKEY = app.config['APIKEY']
    view_func = view.as_view(endpoint)
    if defaults:
        app.add_url_rule(url, view_func=view_func, methods=methods)
    else:
        app.add_url_rule(url, view_func=view_func, methods=methods, defaults=defaults)

def register_all_views(app):
    reg_view(app, IndexView,     "/",        "/")
    reg_view(app, IndexView,     "index",    "/index")

    reg_view(app, ThingsAPIView, "things_api_collection", "/api/v1/things", defaults={'item_id': None})
    reg_view(app, ThingsAPIView, "things_api_item", "/api/v1/things/<int:item_id>", methods=["GET", "PUT", "DELETE"])

def before_request():
    g.user = current_user

app = create_app()
migrate = Migrate(app, db)








