import json

from .plm_leaderboard_database import PLMLeaderboardDatabase
from .plm_leaderboard_ranking import calculate_ranking

from flask import Blueprint, jsonify, current_app, request

plm_leaderboard_service_route = Blueprint('plm_leaderboard', __name__)


@plm_leaderboard_service_route.route('/plm_leaderboard/', methods=['GET'])
def plm_leaderboard():
    plm_leaderboard_db: PLMLeaderboardDatabase = current_app.config["PLM_LEADERBOARD_DATABASE"]
    all_data = plm_leaderboard_db.get_all_data()
    ranking = calculate_ranking(all_data.values())
    return jsonify({"ranking": ranking, "leaderboard": all_data})


@plm_leaderboard_service_route.route('/plm_leaderboard_publish/', methods=['POST'])
def plm_leaderboard_publish():
    publish_data = request.get_json()
    results = json.loads(publish_data["results"])

    plm_leaderboard_db: PLMLeaderboardDatabase = current_app.config["PLM_LEADERBOARD_DATABASE"]

    if plm_leaderboard_db.add_publishing_data(results=results):
        all_data = plm_leaderboard_db.get_all_data()
        ranking = calculate_ranking(all_data.values())
        return jsonify({"ranking": ranking, "leaderboard": all_data})

    # TODO
    return jsonify({"error": "Could not publish data successfully!"})
