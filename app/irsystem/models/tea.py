import json
from uuid import UUID

from sqlalchemy.ext.declarative import DeclarativeMeta

from . import *

# From: http://blog.mmast.net/sqlalchemy-serialize-json
class OutputMixin(object):
    RELATIONSHIPS_TO_DICT = False

    def __iter__(self):
        return self.to_dict().iteritems()

    def to_dict(self, rel=None, backref=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        res = {column.key: getattr(self, attr)
               for attr, column in self.__mapper__.c.items()}
        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if backref == relation.table:
                    continue
                value = getattr(self, attr)
                if value is None:
                    res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=self.__table__)
                else:
                    res[relation.key] = [i.to_dict(backref=self.__table__)
                                         for i in value]
        return res

    def to_json(self, rel=None):
        def extended_encoder(x):
            if isinstance(x, type(datetime)):
                return x.isoformat()
            if isinstance(x, UUID):
                return str(x)
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        return json.dumps(self.to_dict(rel), default=extended_encoder)

class Tea(OutputMixin, Base):
    __tablename__ = 'teas'

    steepsterID = db.Column(db.Integer)
    name = db.Column(db.String(128), nullable = False)
    brand = db.Column(db.String(128))
    reviewCount = db.Column(db.Float)
    ratingValue = db.Column(db.Float)
    teaType = db.Column(db.String(128), nullable = False)
    ingredients	= db.Column(db.String(400))
    flavors	= db.Column(db.String, nullable = False)
    soldIn = db.Column(db.String(128))
    caffeine = db.Column(db.String(128))
    certification = db.Column(db.String(128))
    wantIt = db.Column(db.Float)
    ownIt = db.Column(db.Float)
    imageUrl = db.Column(db.String(400))
    url = db.Column(db.String)
    review1 = db.Column(db.String)
    review2 = db.Column(db.String)
    review3 = db.Column(db.String)
    features = db.Column(db.String)
    features_flavors = db.Column(db.String)

    def __init__(self, **kwargs):
        self.steepsterID = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.brand = kwargs.get('brand', None)
        self.reviewCount = kwargs.get('reviewCount', None)
        self.ratingValue = kwargs.get('ratingValue', None)
        self.teaType = kwargs.get('teaType', None)
        self.ingredients = kwargs.get('ingredients', None)
        self.flavors = kwargs.get('flavors', None)
        self.soldIn = kwargs.get('soldIn', None)
        self.caffeine = kwargs.get('caffeine', None)
        self.certification = kwargs.get('certification', None)
        self.wantIt = kwargs.get('wantIt', None)
        self.ownIt = kwargs.get('ownIt', None)
        self.imageUrl = kwargs.get('imageUrl', None)
        self.url = kwargs.get('url', None)
        self.review1 = kwargs.get('review1', None)
        self.review2 = kwargs.get('review2', None)
        self.review3 = kwargs.get('review3', None)
        self.features = kwargs.get('features', None)
        self.features_flavors = kwargs.get('features_flavors', None)
        
    def __repr__(self):
        return str(self.__dict__)


class TeaSchema(ModelSchema):
    class Meta:
        model = Tea
