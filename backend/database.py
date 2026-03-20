"""
database.py — SQLAlchemy instance
Imported by both models.py and app.py to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()