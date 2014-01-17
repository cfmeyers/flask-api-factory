#For IndexView
from flask import render_template, views

#For the API Views
from collections import defaultdict
from flask import request, jsonify, abort
from App import models
from App.models import db, login_manager

from flask.ext.login import current_user
import base64
from sqlalchemy import and_

class IndexView(views.View):
    """IndexView"""

    methods = ["GET"]

    def dispatch_request(self):

        return render_template("index.html")
        # return "hello world"

##Base View Class (for POSTs and GETs)
class APIView(views.MethodView):
    """APIView is the base class for all the API views"""
    APIKEY = "monkey patch this value"

    ##GET and POST both
    def get_model_name(self): raise NotImplementedError

    ##POST only
    def get_input_dict(self): raise NotImplementedError
    def create_item(self): raise NotImplementedError

    ##GET only
    def get_items(self): raise NotImplementedError
    def get_item(self): raise NotImplementedError
    def pack_item_for_JSON(self, item): raise NotImplementedError

    def pack_items_for_JSON(self, items):
        return {self.get_model_name():[self.pack_item_for_JSON(item) for item in items]}

    def check_api_key(self, key):
        if key == self.APIKEY:
            return True
        return False

    def validate_json_request(self, request):
        if not request.json:
            return False
        return True


    def post(self):
        if not self.validate_json_request(request):
            abort(400)
        if not current_user.is_authenticated():
            return "FAILED TO AUTHENTICATE"

        modelName = self.get_model_name()
        item = self.create_item(self.get_input_dict())
        db.session.add(item)
        db.session.commit()
        return jsonify( self.pack_item_for_JSON(item) )

    def get(self, item_id=None):

        if not current_user.is_authenticated():
            return "FAILED TO AUTHENTICATE"

        if item_id is None:
            items = self.get_items()
            modelName = self.get_model_name()
            return jsonify(self.pack_items_for_JSON(items))
        else:
            item = self.get_item(item_id)
            modelName = self.get_model_name()
            return jsonify( self.pack_item_for_JSON(item) )

    def delete(self, item_id):

        if not current_user.is_authenticated():
            return "FAILED TO AUTHENTICATE"
        item = self.get_item(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"SUCCESS" : str(item_id)})
        else:
            return jsonify({"FAIL" : str(item_id)})

    def put(self, item_id): raise NotImplementedError


def parse_request_to_create_object(request):
    """ given a json request object, return a default dict formatted to create objects
        Args: request:json object
        Returns: default dict with boolean default
    """

    inputDict              = defaultdict(bool)
    if "name" in request.json:
        inputDict["name"] = request.json["name"]
    if "tags" in request.json:
        inputDict["tags"] = request.json["tags"]
    if "project" in request.json:
        inputDict["project"] = request.json["project"]
    if "project" in request.json:
        inputDict["key"] = request.json["key"]

    return inputDict


class ThingsAPIView(APIView):
    """
    TEST CURL:
        curl --user admin:123 http://httpbin.org/headers

    POST
        curl --user admin:123 -i -H "Content-Type: application/json" -X POST -d '{"name":"pizza"}' http://localhost:5000/api/v1/things
        will fail:
            curl  -i -H "Content-Type: application/json" -X POST -d '{"name":"pizza"}' http://localhost:5000/api/v1/things
            curl --user admin:444 -i -H "Content-Type: application/json" -X POST -d '{"name":"pizza"}' http://localhost:5000/api/v1/things

    GET
        curl --user admin:123 http://localhost:5000/api/v1/things
        will fail:
            curl http://localhost:5000/api/v1/things
            curl --user admin:555 http://localhost:5000/api/v1/things

    PUT

        curl --user "admin:123" -i -H "Content-Type: application/json" -X PUT -d '{"name":"cadbury"}' http://localhost:5000/api/v1/things/2
        will fail:
            curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"cadbury"}' http://localhost:5000/api/v1/things/2
            curl --user "admin:777" -i -H "Content-Type: application/json" -X PUT -d '{"name":"cadbury"}' http://localhost:5000/api/v1/things/2

    DELETE
            curl --user admin:123 -i -H "Content-Type: application/json" -X DELETE -d '{}' http://localhost:5000/api/v1/things/1
        will fail:
            curl  -i -H "Content-Type: application/json" -X DELETE -d '{}' http://localhost:5000/api/v1/things/1
            curl --user admin:888 -i -H "Content-Type: application/json" -X DELETE -d '{}' http://localhost:5000/api/v1/things/1
    """

    def get_model_name(self): return "things"

    def get_input_dict(self): return parse_request_to_create_object(request)

    def create_item(self, inputDict): return models.Things(inputDict["name"])

    def get_items(self): return models.Things.query.all()

    def get_item(self, item_id): return models.Things.query.filter_by(id=item_id).first()

    def pack_item_for_JSON(self, item): return {"id": item.id, "time": item.timeStamp, "name": item.name}

    def put(self, item_id):
        """
        curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"cadbury"}' http://localhost:5000/api/v1/things/3
        curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"cadbury"}' http://localhost:5000/api/v1/things/3
        curl --user "admin:123" -i -H "Content-Type: application/json" -X PUT -d '{"name":"cadbury"}' http://localhost:5000/api/v1/things/3
        """

        if not current_user.is_authenticated():
            return "FAILED TO AUTHENTICATE"

        item = self.get_item(item_id)
        updates = parse_request_to_create_object(request)
        for key, val in updates.items():
            setattr(item, key, val)
        db.session.commit()
        return "Success"

@login_manager.header_loader
def load_user_from_header(header_val):
    if header_val.startswith('Basic '):
        header_val = header_val.replace('Basic ', '', 1)
    try:
        header_val = base64.b64decode(header_val)
    except TypeError:
        pass
    name = header_val.split(":")[0]
    key = header_val.split(":")[1]
    return models.User.query.filter(and_(models.User.api_key==key, models.User.name==name)).first()

@login_manager.user_loader
def load_user(username):
    return models.User.query.filter_by(name=username).first()













