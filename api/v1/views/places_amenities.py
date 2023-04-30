#!/usr/bin/python3
"""Handles all RESTFul API requests for Amenities"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage, storage_t
from models.amenity import Amenity
from models.place import Place


@app_views.route('/places/<place_id>/amenities',
                 methods=['GET'], strict_slashes=False)
def get_place_amenities(place_id):
    """Retrieves the list of all Amenity objects of a Place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    if storage_t == 'db':
        return jsonify([amenity.to_dict() for amenity in place.amenities])
    return jsonify([amenity.to_dict() for amenity in place.amenities()])


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'],
                 strict_slashes=False)
def delete_place_amenity(place_id, amenity_id):
    """Deletes a Amenity object to a Place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if storage_t == "db":
        amenity_ids = [amenity.id for amenity in place.amenities]
        if amenity.id not in amenity_ids:
            abort(404)
        place.amenities.remove(amenity)
    else:
        if amenity.id not in place.amenity_ids:
            abort(404)
        place.amenity_ids.remove(amenity.id)

    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['POST'], strict_slashes=False)
def link_place_amenity(place_id, amenity_id):
    """Link a Amenity object to a Place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if storage_t == "db":
        amenity_ids = [amenity.id for amenity in place.amenities]
        if amenity.id in amenity_ids:
            return jsonify(amenity.to_dict()), 200
        else:
            place.amenities.append(amenity)
            place.save()
            return jsonify(amenity.to_dict()), 201
    else:
        if amenity.id in place.amenity_ids:
            return jsonify(amenity.to_dict()), 200
        else:
            place.amenity_ids.append(amenity.id)
            place.save()
            return jsonify(amenity.to_dict()), 201
