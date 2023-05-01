#!/usr/bin/python3
"""
0x05. AirBnB clone - RESTful API -- Dump Database
"""

from flask import Flask, jsonify
from flask_cors import CORS
from models import storage
from api.v1.views import app_views
from os import environ

#  Get host and port from environ if defined
if environ.get('HBNB_API_HOST') is None:
    HBNB_API_HOST = "0.0.0.0"
else:
    HBNB_API_HOST = environ.get('HBNB_API_HOST')
if environ.get('HBNB_API_PORT') is None:
    HBNB_API_PORT = 5000
else:
    HBNB_API_PORT = environ.get('HBNB_API_PORT')


app = Flask(__name__)
CORS(app, resources={"/*": {"origins": "0.0.0.0"}})
app.register_blueprint(app_views)
app.url_map.strict_slashes = False


@app.teardown_appcontext
def close_storage(exception=None):
    """Close any active SQLAlchemy sessions"""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """ Error 404 """
    return jsonify({'error': 'Not found'}), 404


@app.route('/dump')
def dump_database():
    """Dumps entire database"""
    from models.amenity import Amenity
    from models.city import City
    from models.place import Place
    from models.review import Review
    from models.state import State
    from models.user import User

    objs = [Amenity, City, Place, Review, State, User]

    results = set()

    for obj in objs:
        results.update(storage.all(obj).values())
    return jsonify({obj.__class__.__name__ + '.' + obj.id : obj.to_dict()
                    for obj in results})


if __name__ == '__main__':
    app.run(host=HBNB_API_HOST, port=HBNB_API_PORT, threaded=True)
