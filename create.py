from main import app,db
from main import Time, Card, Folder,User


with app.app_context():
    db.create_all()