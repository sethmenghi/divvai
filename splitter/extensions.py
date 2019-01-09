"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
# from flask_caching import Cache
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy  # , Model
from flask_bootstrap import Bootstrap

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()

# from conduit.utils import jwt_identity, identity_loader  # noqa

# jwt = JWTManager()
# jwt.user_loader_callback_loader(jwt_identity)
# jwt.user_identity_loader(identity_loader)
