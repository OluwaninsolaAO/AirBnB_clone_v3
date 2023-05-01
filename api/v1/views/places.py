#!/usr/bin/python3
"""Handles all RESTFul API requests for Places"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.city import City
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """Returns a list of all Places objects for a city"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """Returns an Place object with a matching id"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a matching Place objects"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """Add a new Place object for a matching city id and user_id"""
    from models.user import User
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Not a JSON'}), 400
    elif 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
    elif storage.get(User, data['user_id']) is None:
        abort(404)
    elif 'name' not in data:
        return jsonify({'error': 'Missing name'}), 400

    place = Place(name=data['name'], city_id=city.id, user_id=data['user_id'])
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """Updates matching Place Object with JSON data"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Not a JSON'}), 400

    for key in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
        try:
            data.pop(key)
        except KeyError:
            pass

    for key, value in data.items():
        setattr(place, key, value)

    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def place_search():
    """Returns a list of all Places objects matching search data"""

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Not a JSON'}), 400

    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    places = set()

    #  If states and cities are empty; retrive all Place objects
    if not (len(states) + len(cities)):
        places.update(storage.all(Place).values())
        if not len(amenities):
            return jsonify([place.to_dict() for place in places])
    else:  # else
        for state_id in states:
            state = storage.get(State, state_id)
            if state is None:
                abort(404)
            for city in state.cities:
                places.update(city.places)

        for city_id in cities:
            city = storage.get(City, city_id)
            if city is None:
                abort(404)
            places.update(city.places)

    if not len(amenities):
        return jsonify([place.to_dict() for place in places])

    #  Filter results with amenities if exists
    a_filter = [storage.get(Amenity, amenity_id) for amenity_id in
                amenities if storage.get(Amenity, amenity_id) is not None]
    results = set()
    for place in places:
        if len(set(a_filter).intersection(set(place.amenities))):
            #  patch SQLAlchemy bug
            try:
                del place.amenities
            except AttributeError:
                pass
            results.add(place)

    return jsonify([place.to_dict() for place in results])
