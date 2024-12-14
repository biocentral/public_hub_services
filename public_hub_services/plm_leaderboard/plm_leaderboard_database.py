import os
import json
import yaml
import redis
import logging

from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class PLMLeaderboardDatabase:
    _metadata_keys = ['model_name', 'dataset_name', 'split_name', 'biotrainer_version', 'training_date']

    def __init__(self, backup_data: Optional[Path] = None):
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))

        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

        if backup_data is not None:
            self._clear_database()
            self.load_leaderboard_to_redis(backup_data=backup_data)

    def load_leaderboard_to_redis(self, backup_data: Path):
        if backup_data.suffix in ['.yml', '.yaml']:
            self.import_from_yaml(backup_data)
        else:
            raise ValueError("Unsupported file format. Use .csv, .yml, or .yaml")

    def add_entry(self, entry: Dict[str, Dict[str, Any]]) -> bool:
        # Separate metadata and metrics
        metadata = entry["metadata"]
        metrics = entry["metrics"]

        # Store metadata and metrics in a hash
        entry_id = f"{metadata['model_name']}:{metadata['dataset_name']}:{metadata['split_name']}"
        self.redis_client.hset(f"plm-leaderboard:{entry_id}", mapping={
            'metadata': json.dumps(metadata),
            'metrics': json.dumps(metrics)
        })

        # Add to set of all entries
        self.redis_client.sadd('plm-leaderboard:all_entries', entry_id)

        return True

    def add_publishing_data(self, results: List[Dict[str, Any]]) -> bool:
        # TODO Verification
        for entry in results:
            self.add_entry(entry)

        # TODO Remove, only debug
        self.export_to_yaml(output_path=Path("published.yml"))
        return True

    def get_entry(self, model_name: str, dataset_name: str, split_name: str) -> Optional[Dict[str, any]]:
        entry_id = f"{model_name}:{dataset_name}:{split_name}"
        entry = self.redis_client.hgetall(f"plm-leaderboard:{entry_id}")
        if not entry:
            return None

        metadata = json.loads(entry['metadata'])
        metrics = json.loads(entry['metrics'])
        return {"metadata": metadata, "metrics": metrics}

    def get_all_data(self) -> Dict[str, Dict[str, any]]:
        all_entry_ids = self.redis_client.smembers('plm-leaderboard:all_entries')
        return {str(idx): self.get_entry(*entry_id.split(':')) for idx, entry_id in enumerate(all_entry_ids)}

    def update_entry(self, entry: Dict[str, any]) -> bool:
        return self.add_entry(entry)  # add_entry will overwrite if the key already exists

    def delete_entry(self, model_name: str, dataset_name: str, split_name: str) -> bool:
        entry_id = f"{model_name}:{dataset_name}:{split_name}"
        key = f"plm-leaderboard:{entry_id}"
        if self.redis_client.exists(key):
            self.redis_client.delete(key)
            self.redis_client.srem('plm-leaderboard:all_entries', entry_id)
            return True
        return False

    def _clear_database(self) -> bool:
        try:
            all_keys = self.redis_client.keys('plm-leaderboard:*')
            if all_keys:
                self.redis_client.delete(*all_keys)
            return True
        except Exception as e:
            logger.error(f"An error occurred while clearing the database: {str(e)}")
            return False

    def export_to_yaml(self, output_path: Path):
        data = self.get_all_data()
        with open(output_path, 'w') as file:
            yaml.dump(data, file)

    def import_from_yaml(self, input_path: Path):
        with open(input_path, 'r') as file:
            data = yaml.safe_load(file)
        for entry in data:
            self.add_entry(entry)
