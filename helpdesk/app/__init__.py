import logging

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.utils.legacy import get_sqla_class

from .inicio import VistaInicio

SQLA = get_sqla_class()

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)

with app.app_context():
    appbuilder = AppBuilder(
        app,
        db.session,
        base_template="mybase.html",
        indexview=VistaInicio,
    )

    from . import models, views, reportes  # noqa: E402,F401