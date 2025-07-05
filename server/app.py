from flask import Flask
from config import get_config


def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize the app with config-specific settings
    config_class.init_app(app)

    return app


# Usage
app = create_app()  # Uses FLASK_ENV environment variable
# or
app = create_app('testing')  # Force testing config