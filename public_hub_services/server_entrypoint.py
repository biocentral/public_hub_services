import os
from pathlib import Path

from flask import Flask

from .utils import Constants, str2bool
from .plm_leaderboard import plm_leaderboard_service_route, init_leaderboard_database_instance


def create_app():
    app = Flask("Biocentral Public Hub Services")

    app.register_blueprint(plm_leaderboard_service_route)

    # Setup services
    USE_BACKUP_DATA = False
    backup_data_path = Path("data/leaderboard-13-12-2024.yml") if USE_BACKUP_DATA else None
    app.config["PLM_LEADERBOARD_DATABASE"] = init_leaderboard_database_instance(backup_data=backup_data_path)

    return app


def run_server():
    app = create_app()
    debug = str2bool(str(os.environ.get('SERVER_DEBUG', True)))
    app.run(debug=True, port=Constants.SERVER_DEFAULT_PORT)  # Set debug=False for production
