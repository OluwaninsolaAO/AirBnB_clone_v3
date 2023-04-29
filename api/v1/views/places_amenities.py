#!/usr/bin/python3
"""Handles all RESTFul API requests for Amenities"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.amenity import Amenity
from models.place import Place


@app_views.route('/places/<place_id>/amenities',
                 methods=['GET'], strict_slashes=False)
def get_amenities(place_id):
    """Returns a list of all amenity objects for a place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    return jsonify([amenity.to_dict() for amenity in place.amenities])
