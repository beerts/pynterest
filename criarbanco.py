from pynterest import database, app
from pynterest.models import Usuario, Foto

with app.app_context():
    database.create_all()