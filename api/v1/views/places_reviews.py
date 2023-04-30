#!/usr/bin/python3
"""Handles all RESTFul API requests for Review"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage, storage_t
from models.review import Review
from models.place import Place


@app_views.route('/places/<place_id>/reviews',
                 methods=['GET'], strict_slashes=False)
def get_reviews(place_id):
    """Returns a list of all Review objects for a place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    return jsonify([review.to_dict() for review in place.reviews])


@app_views.route('/reviews/<review_id>', methods=['GET'],
                 strict_slashes=False)
def get_review(review_id):
    """Returns an review object with a matching id"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)

    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """Deletes review object with a matching id"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)

    storage.delete(review)
    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>/reviews',
                 methods=['POST'], strict_slashes=False)
def create_review(place_id):
    """Add a new review object for a matching place id and user_id"""
    from models.user import User
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Not a JSON'}), 400
    elif 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
    elif storage.get(User, data['user_id']) is None:
        abort(404)
    elif 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400

    review = Review(text=data['text'],
                    place_id=place.id, user_id=data['user_id'])
    review.save()
    return jsonify(review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """Updates matching review Object with JSON data"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Not a JSON'}), 400

    for key in ['id', 'user_id', 'place_id', 'created_at', 'updated_at']:
        try:
            data.pop(key)
        except KeyError:
            pass

    for key, value in data.items():
        setattr(review, key, value)

    storage.save()
    return jsonify(review.to_dict()), 200
