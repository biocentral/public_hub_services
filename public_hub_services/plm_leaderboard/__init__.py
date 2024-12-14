from pathlib import Path
from typing import Optional

from .plm_leaderboard_database import PLMLeaderboardDatabase
from .plm_leaderboard_endpoint import plm_leaderboard_service_route


def init_leaderboard_database_instance(backup_data: Optional[Path] = None) -> PLMLeaderboardDatabase:
    leaderboard_db_instance = PLMLeaderboardDatabase(backup_data=backup_data)
    return leaderboard_db_instance


__all__ = ["plm_leaderboard_service_route", "init_leaderboard_database_instance", "PLMLeaderboardDatabase"]
