from functools import lru_cache
from collections import defaultdict
from statistics import mean
from typing import Dict, List, Any

from autoeval.utilities.FLIP import FLIP_DATASETS


def _get_dataset_categories():
    FLIP_CATEGORIES = [["aav", "gb1"]]
    return FLIP_CATEGORIES


def _ascending_metrics():
    return ['loss', 'rmse', 'mse', 'mae', 'mean_squared_error', 'mean_absolute_error']


def get_recommended_metrics():
    return {dataset: values["recommended_evaluation_metric"] for dataset, values in FLIP_DATASETS.items()}


def calculate_ranking(leaderboard_data) -> Dict[str, float]:
    # TODO [Optimization] Add caching as long as data did not change
    recommended_metrics = get_recommended_metrics()
    dataset_categories = _get_dataset_categories()

    # Step 1: Get ranking for each dataset split by recommended metric
    split_rankings = defaultdict(lambda: defaultdict(list))
    for entry in leaderboard_data:
        metadata = entry["metadata"]
        dataset = metadata['dataset_name']
        split = metadata['split_name']
        model = metadata['model_name']
        metric_value = entry['metrics'].get(recommended_metrics[dataset])

        if metric_value is not None:
            split_rankings[dataset][split].append((model, metric_value))

    # Sort and assign rankings
    for dataset in split_rankings:
        for split in split_rankings[dataset]:
            reverse_ranking = recommended_metrics[dataset] not in _ascending_metrics()
            split_rankings[dataset][split].sort(key=lambda x: x[1], reverse=reverse_ranking)
            for rank, (model, _) in enumerate(split_rankings[dataset][split], 1):
                split_rankings[dataset][split][rank - 1] = (model, rank)

    # Step 2: Take mean over ranking for datasets with multiple splits
    dataset_rankings = defaultdict(lambda: defaultdict(list))
    for dataset in split_rankings:
        for split in split_rankings[dataset]:
            for model, rank in split_rankings[dataset][split]:
                dataset_rankings[dataset][model].append(rank)

    for dataset in dataset_rankings:
        for model in dataset_rankings[dataset]:
            dataset_rankings[dataset][model] = mean(dataset_rankings[dataset][model])

    # Step 3: Take mean over category for final ranking
    category_rankings = defaultdict(lambda: defaultdict(list))
    for category in dataset_categories:
        for dataset in category:
            if dataset in dataset_rankings:
                for model, rank in dataset_rankings[dataset].items():
                    category_rankings[tuple(category)][model].append(rank)

    for category in category_rankings:
        for model in category_rankings[category]:
            category_rankings[category][model] = mean(category_rankings[category][model])

    # Step 4: Calculate final ranking
    final_rankings = defaultdict(list)
    for category in category_rankings:
        for model, rank in category_rankings[category].items():
            final_rankings[model].append(rank)

    # Add rankings for datasets not in any category
    for dataset in dataset_rankings:
        if not any(dataset in category for category in dataset_categories):
            for model, rank in dataset_rankings[dataset].items():
                final_rankings[model].append(rank)

    # Calculate mean ranking for each model
    final_scores = {model: mean(ranks) for model, ranks in final_rankings.items()}

    # Sort final scores (lower is better)
    sorted_final_scores = dict(sorted(final_scores.items(), key=lambda item: item[1]))

    return sorted_final_scores
