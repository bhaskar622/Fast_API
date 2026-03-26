# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    All SQLAlchemy models MUST inherit from this class.
    This is like 'models.Model' in Odoo — the base for everything.
    """
    pass
