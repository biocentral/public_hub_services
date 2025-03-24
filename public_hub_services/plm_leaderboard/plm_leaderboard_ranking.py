from autoeval.utilities.FLIP import FLIP_DATASETS


def get_recommended_metrics():
    return {dataset: values["recommended_evaluation_metric"] for dataset, values in FLIP_DATASETS.items()}
