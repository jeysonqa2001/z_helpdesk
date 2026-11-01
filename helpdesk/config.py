import os
from dotenv import load_dotenv
from flask_appbuilder.security.manager import (
    AUTH_REMOTE_USER,
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
)

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv("SECRET_KEY", "01234567890123456789")

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@localhost:3306/z_helpdesk_db"

# Protección CSRF
CSRF_ENABLED = True

APP_NAME = "HelpDesk Pro"
APP_THEME = "flatly.css"

AUTH_TYPE = AUTH_DB

BABEL_DEFAULT_LOCALE = "es"
BABEL_DEFAULT_FOLDER = "translations"
LANGUAGES = {
    "es": {"flag": "es", "name": "Español"},
    "en": {"flag": "gb", "name": "English"},
}

UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_URL = "/static/uploads/"

API_PROVIDER = os.getenv("API_PROVIDER", "groq")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-20b")
AI_URL = os.getenv("AI_URL", "https://api.groq.com/openai/v1")