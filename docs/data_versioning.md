# Data Versioning Guide

This guide explains how to use Data Version Control (DVC) for managing datasets and ML pipelines in the Innovate Analytics MLOps project.

## Overview

Data Version Control (DVC) allows us to:
- Track and version large data files without storing them in Git
- Create reproducible ML pipelines
- Track experiments and metrics
- Share data across team members

## Prerequisites

- DVC installed (run `dvc --version` to check)
- Git repository initialized

## Basic Workflow

### 1. Tracking Datasets

To start tracking a dataset:

```bash
# Using command-line
dvc add data/raw/iris.csv

# Using the Python script
python -m scripts.data_versioning track data/raw/iris.csv --message "Add initial iris dataset"
```

This creates a `.dvc` file that references the actual data, which is stored in the DVC cache.

### 2. Updating Datasets

When a dataset changes:

```bash
# Using command-line
dvc add --force data/raw/iris.csv
git add data/raw/iris.csv.dvc
git commit -m "Update iris dataset"

# Using the Python script
python -m scripts.data_versioning update data/raw/iris.csv --message "Update iris dataset"
```

### 3. Versioning Datasets

To add a specific version tag to a dataset:

```bash
# Using command-line
dvc tag add -d data/raw/iris.csv v1.0 -m "Version 1.0 of iris dataset"

# Using the Python script
python -m scripts.data_versioning tag data/raw/iris.csv v1.0 --message "Version 1.0 of iris dataset"
```

### 4. Creating ML Pipelines

Define reproducible pipelines in `dvc.yaml`:

```yaml
stages:
  process_data:
    cmd: python -m src.data.process --dataset iris
    deps:
      - src/data/process.py
      - data/raw/iris.csv
    outs:
      - data/processed/iris_X_train.csv
      - data/processed/iris_X_test.csv
      - data/processed/iris_y_train.csv
      - data/processed/iris_y_test.csv

  train_model:
    cmd: python -m src.models.run_training --dataset iris
    deps:
      - src/models/run_training.py
      - data/processed/iris_X_train.csv
      - data/processed/iris_X_test.csv
      - data/processed/iris_y_train.csv
      - data/processed/iris_y_test.csv
    outs:
      - models/iris_classification_model.pkl
    metrics:
      - metrics/model_metrics.json
```

Run the pipeline:

```bash
# Run the entire pipeline
dvc repro

# Using the Python script
python -m scripts.data_versioning run
```

### 5. Sharing Data

To share data with teammates, set up a DVC remote:

```bash
# Add a remote storage (e.g., S3, Google Drive, or a local directory)
dvc remote add -d myremote s3://mybucket/dvcstore

# Push data to the remote
dvc push

# Pull data from the remote
dvc pull
```

## Data Versioning Script

We provide a Python script (`scripts/data_versioning.py`) to simplify DVC operations:

```bash
# Initialize DVC
python -m scripts.data_versioning init

# Track a dataset
python -m scripts.data_versioning track data/raw/iris.csv --message "Add iris dataset"

# Update a dataset and add a tag
python -m scripts.data_versioning update data/raw/iris.csv --tag v1.0 --message "Update iris dataset"

# Pull datasets from remote
python -m scripts.data_versioning pull

# Run the DVC pipeline
python -m scripts.data_versioning run
```

## Best Practices

1. **Commit .dvc files to Git**: Always commit the `.dvc` files to Git so others can access the data references.

2. **Use meaningful tags**: When tagging dataset versions, use meaningful tags like `v1.0`, `production`, or `experiment-xyz`.

3. **Keep raw data immutable**: Treat raw data as immutable and use processed data for experiments.

4. **Document data changes**: Include clear messages when updating datasets to track the purpose and nature of changes.

5. **Use metrics for model comparison**: Track model metrics with DVC to easily compare different experiments.

## Common Issues and Solutions

### Issue: Unable to access data after cloning repository

Solution: Run `dvc pull` to download data from the remote storage.

### Issue: Conflicts in .dvc files

Solution: Resolve Git conflicts in `.dvc` files, then run `dvc checkout` to update the data.

### Issue: Pipeline failing due to missing dependencies

Solution: Ensure all dependencies are correctly specified in the `dvc.yaml` file.

## Conclusion

DVC is a powerful tool for data versioning and pipeline management in ML projects. By following this guide, you can ensure that your data is properly versioned, your workflows are reproducible, and your team can collaborate effectively. 