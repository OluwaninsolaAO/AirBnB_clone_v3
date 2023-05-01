#!/usr/bin/python
""" holds class City"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class City(BaseModel, Base):
    """Representation of city """
    if models.storage_t == "db":
        __tablename__ = 'cities'
        state_id = Column(String(60), ForeignKey('states.id'), nullable=False)
        name = Column(String(128), nullable=False)
        places = relationship("Place", backref="cities",
                              cascade='all, delete, delete-orphan')
    else:
        state_id = ""
        name = ""

        @property
        def places(self):
            """Returns a list of places within a city"""
            from models.place import Place
            from models import storage

            resp = []

            for place in storage.all(Place).values():
                if place.city_id == self.id:
                    resp.append(place)

            return resp

    def __init__(self, *args, **kwargs):
        """initializes city"""
        super().__init__(*args, **kwargs)
