from . import *

class Tea(Base):
    __tablename__ = 'teas'

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

    def __init__(self, **kwargs):
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

    def __repr__(self):
        return str(self.__dict__)


class TeaSchema(ModelSchema):
    class Meta:
        model = Tea
