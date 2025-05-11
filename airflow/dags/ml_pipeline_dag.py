"""
Airflow DAG for ML pipeline execution.

This DAG orchestrates the entire ML pipeline, from data ingestion to model deployment.
"""

from datetime import datetime, timedelta

from airflow.models.param import Param
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

from airflow import DAG

# Default arguments for DAG
default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'email': ['mlops@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'ml_pipeline',
    default_args=default_args,
    description='End-to-end ML pipeline for Innovate Analytics',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ml', 'pipeline', 'production'],
    params={
        'dataset': Param(
            default='iris',
            type='string',
            description='Dataset to use (iris or california_housing)'
        ),
        'model_type': Param(
            default='classification',
            type='string',
            description='Type of model to train (classification or regression)'
        ),
        'use_mlflow': Param(
            default=True,
            type='boolean',
            description='Whether to use MLflow for tracking'
        )
    }
)

# Define Python functions for tasks
def extract_data(**kwargs):
    """Extract data from source."""
    import os
    from datetime import datetime

    import pandas as pd
    from sklearn.datasets import fetch_california_housing, load_iris

    # Get parameters
    dataset = kwargs['params']['dataset']
    
    # Create output directory
    os.makedirs('/opt/airflow/data/raw', exist_ok=True)
    
    # Load dataset based on parameter
    if dataset == 'iris':
        # Load Iris dataset
        iris = load_iris()
        df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
        df['target'] = iris.target
    elif dataset == 'california_housing':
        # Load California Housing dataset
        housing = fetch_california_housing()
        df = pd.DataFrame(data=housing.data, columns=housing.feature_names)
        df['target'] = housing.target
    else:
        raise ValueError(f"Unknown dataset: {dataset}")
    
    # Save to a file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'/opt/airflow/data/raw/{dataset}_{timestamp}.csv'
    df.to_csv(output_path, index=False)
    
    # Return the file path for the next task
    return output_path


def transform_data(**kwargs):
    """Transform raw data into features for training."""
    import os
    from datetime import datetime

    import pandas as pd
    from sklearn.model_selection import train_test_split

    # Get the file path from the previous task
    ti = kwargs['ti']
    input_path = ti.xcom_pull(task_ids='extract_data')
    dataset = kwargs['params']['dataset']
    
    # Create output directory
    os.makedirs('/opt/airflow/data/processed', exist_ok=True)
    
    # Load the data
    df = pd.read_csv(input_path)
    
    # Split data
    X = df.drop(columns=['target'])
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Save processed data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = f'/opt/airflow/data/processed/{dataset}_{timestamp}'
    
    X_train.to_csv(f'{base_path}_X_train.csv', index=False)
    X_test.to_csv(f'{base_path}_X_test.csv', index=False)
    y_train.to_csv(f'{base_path}_y_train.csv', index=False)
    y_test.to_csv(f'{base_path}_y_test.csv', index=False)
    
    # Return the base path for the next task
    return base_path


def train_model(**kwargs):
    """Train ML model on processed data."""
    import os
    import pickle
    from datetime import datetime

    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

    import mlflow

    # Get the base path from the previous task
    ti = kwargs['ti']
    base_path = ti.xcom_pull(task_ids='transform_data')
    dataset = kwargs['params']['dataset']
    model_type = kwargs['params']['model_type']
    
    # Load the data
    X_train = pd.read_csv(f'{base_path}_X_train.csv')
    X_test = pd.read_csv(f'{base_path}_X_test.csv')
    y_train = pd.read_csv(f'{base_path}_y_train.csv').squeeze()
    y_test = pd.read_csv(f'{base_path}_y_test.csv').squeeze()
    
    # Configure MLflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000'))
    mlflow.set_experiment(f'airflow_{dataset}_{model_type}')
    
    # Train model with MLflow tracking
    with mlflow.start_run() as run:
        # Set model parameters based on model type
        if model_type == 'classification':
            model_params = {
                'n_estimators': 100,
                'max_depth': 5,
                'random_state': 42
            }
            model = RandomForestClassifier(**model_params)
        else:  # regression
            model_params = {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            }
            model = RandomForestRegressor(**model_params)
        
        # Log parameters
        mlflow.log_params(model_params)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate model
        if model_type == 'classification':
            accuracy = model.score(X_test, y_test)
            mlflow.log_metric('accuracy', accuracy)
        else:  # regression
            r2 = model.score(X_test, y_test)
            mlflow.log_metric('r2', r2)
        
        # Log the model
        mlflow.sklearn.log_model(model, 'model')
        
        # Save the run ID for model registration
        run_id = run.info.run_id
    
    # Create directory for model output
    os.makedirs('/opt/airflow/models', exist_ok=True)
    
    # Save run ID to file
    output_path = f'/opt/airflow/models/run_id_{dataset}_{model_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(output_path, 'w') as f:
        f.write(run_id)
    
    # Also save the model as a pickle file
    model_path = f'/opt/airflow/models/{dataset}_{model_type}_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Create metrics directory
    os.makedirs('/opt/airflow/metrics', exist_ok=True)
    
    # Save metrics
    metrics_path = f'/opt/airflow/metrics/{dataset}_{model_type}_metrics.json'
    import json
    metrics = {'accuracy' if model_type == 'classification' else 'r2': model.score(X_test, y_test)}
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return {'run_id': run_id, 'model_path': model_path}


def register_model(**kwargs):
    """Register the trained model in MLflow Model Registry."""
    import os

    import mlflow

    # Get the run ID from the previous task
    ti = kwargs['ti']
    result = ti.xcom_pull(task_ids='train_model')
    run_id = result['run_id']
    dataset = kwargs['params']['dataset']
    model_type = kwargs['params']['model_type']
    
    # Configure MLflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000'))
    
    # Register the model
    model_uri = f'runs:/{run_id}/model'
    model_name = f"innovate_analytics_{dataset}_{model_type}_model"
    model_version = mlflow.register_model(model_uri, model_name)
    
    return {'model_name': model_name, 'model_version': model_version.version}


def deploy_model(**kwargs):
    """Deploy the registered model."""
    import os
    import shutil

    import mlflow

    # Get the model information from the previous task
    ti = kwargs['ti']
    result = ti.xcom_pull(task_ids='register_model')
    model_name = result['model_name']
    model_version = result['model_version']
    
    # Configure MLflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000'))
    
    # Transition the model to Production stage
    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=model_version,
        stage='Production'
    )
    
    # Create a symbolic link to the latest model for the API
    model_path = f'/opt/airflow/models/latest'
    f'/opt/airflow/mlruns'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Create or update latest model directory
    if os.path.exists(model_path):
        # Remove existing directory
        if os.path.isdir(model_path):
            shutil.rmtree(model_path)
        else:
            os.remove(model_path)
    
    # Download the model to the latest directory
    downloaded_model = mlflow.sklearn.load_model(f"models:/{model_name}/{model_version}")
    mlflow.sklearn.save_model(downloaded_model, model_path)
    
    return {'model_name': model_name, 'model_version': model_version, 'model_path': model_path}


# Create tasks
start = DummyOperator(
    task_id='start_pipeline',
    dag=dag,
)

extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    provide_context=True,
    dag=dag,
)

register = PythonOperator(
    task_id='register_model',
    python_callable=register_model,
    provide_context=True,
    dag=dag,
)

deploy = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    provide_context=True,
    dag=dag,
)

# Create a notification task
notify = BashOperator(
    task_id='notify_deployment',
    bash_command='echo "ML pipeline completed successfully and model deployed to production at $(date)" > /opt/airflow/logs/deployment_notification.txt && echo "Model deployed successfully"',
    dag=dag,
)

# Add a task to test the API if it's running
test_api = BashOperator(
    task_id='test_api',
    bash_command='python -m scripts.test_api --api-url http://app:8000 --dataset {{ params.dataset }} || echo "Note: API test failed, the FastAPI app might not be running."',
    dag=dag,
)

end = DummyOperator(
    task_id='end_pipeline',
    dag=dag,
)

# Define task dependencies
start >> extract >> transform >> train >> register >> deploy >> notify >> test_api >> end 