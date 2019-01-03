# -*- coding: utf-8 -*-
from splitter.database import SurrogatePK, db, Column, Model, relationship


class Restaurant(SurrogatePK, Model):
    __tablename__ = 'restaurants'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50), nullable=False)
    phone_num = Column(db.String, unique=True, nullable=False)

    receipt_id = Column(db.Integer, db.ForeignKey('receipt.id'))
