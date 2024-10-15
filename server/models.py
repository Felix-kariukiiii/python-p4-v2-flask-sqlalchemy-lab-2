from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Relationship to Review
    reviews = db.relationship('Review', back_populates='customer')

    # Association proxy to access items directly through reviews
    items = association_proxy('reviews', 'item')

    serialize_rules = ('-reviews.customer',)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
             'reviews': [review.to_dict() for review in self.reviews] if self.reviews else [],
            'items': [item.to_dict() for item in self.items if item]  # Ensure item is not None
        }

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    # Relationship to Review
    reviews = db.relationship('Review', back_populates='item')

    serialize_rules = ('-reviews.item',)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'reviews': [review.to_dict() for review in self.reviews if review]
        }

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)

    # Foreign key to Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', back_populates='reviews')

    # Foreign key to Item
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    item = db.relationship('Item', back_populates='reviews')

    serialize_rules = ('-customer.reviews', '-item.reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'comment': self.comment,
            'customer': self.customer.name if self.customer else None,  # Safe access to customer name
            'item': self.item.name if self.item else None  # Safe access to item name
        }

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'
