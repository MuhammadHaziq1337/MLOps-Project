"""
Airflow DAG for ML pipeline execution.

This DAG orchestrates the entire ML pipeline, from data ingestion to model deployment.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

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
)

# Define Python functions for tasks
def extract_data(**kwargs):
    """Extract data from source."""
    import pandas as pd
    from datetime import datetime
    
    # In a real-world scenario, you would extract data from a database or API
    # For demo purposes, we're creating a dummy dataset
    df = pd.DataFrame({
        'feature1': range(100),
        'feature2': range(100, 200),
        'target': [i % 2 for i in range(100)]
    })
    
    # Save to a file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'/opt/airflow/data/raw/data_{timestamp}.csv'
    df.to_csv(output_path, index=False)
    
    # Return the file path for the next task
    return output_path


def transform_data(**kwargs):
    """Transform raw data into features for training."""
    import pandas as pd
    from datetime import datetime
    import os
    
    # Get the file path from the previous task
    ti = kwargs['ti']
    input_path = ti.xcom_pull(task_ids='extract_data')
    
    # Load the data
    df = pd.read_csv(input_path)
    
    # Perform transformations (dummy example)
    df['feature3'] = df['feature1'] * df['feature2']
    df['feature4'] = df['feature1'] + df['feature2']
    
    # Save processed data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'/opt/airflow/data/processed/processed_data_{timestamp}.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    return output_path


def train_model(**kwargs):
    """Train ML model on processed data."""
    import pandas as pd
    import mlflow
    import os
    import pickle
    from datetime import datetime
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Get the file path from the previous task
    ti = kwargs['ti']
    input_path = ti.xcom_pull(task_ids='transform_data')
    
    # Load the data
    df = pd.read_csv(input_path)
    
    # Prepare features and target
    X = df.drop(columns=['target'])
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Configure MLflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
    mlflow.set_experiment('airflow_ml_pipeline')
    
    # Train model with MLflow tracking
    with mlflow.start_run() as run:
        # Set model parameters
        model_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        }
        
        # Log parameters
        mlflow.log_params(model_params)
        
        # Train model
        model = RandomForestClassifier(**model_params)
        model.fit(X_train, y_train)
        
        # Evaluate model
        accuracy = model.score(X_test, y_test)
        mlflow.log_metric('accuracy', accuracy)
        
        # Log the model
        mlflow.sklearn.log_model(model, 'model')
        
        # Save the run ID for model registration
        run_id = run.info.run_id
    
    # Save run ID for the next task
    output_path = f'/opt/airflow/models/run_id_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(run_id)
    
    return output_path


def register_model(**kwargs):
    """Register the trained model in MLflow Model Registry."""
    import mlflow
    import os
    
    # Get the run ID file path from the previous task
    ti = kwargs['ti']
    run_id_file = ti.xcom_pull(task_ids='train_model')
    
    # Read the run ID
    with open(run_id_file, 'r') as f:
        run_id = f.read().strip()
    
    # Configure MLflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
    
    # Register the model
    model_uri = f'runs:/{run_id}/model'
    model_name = 'innovate_analytics_model'
    model_version = mlflow.register_model(model_uri, model_name)
    
    return model_version.version


def deploy_model(**kwargs):
    """Deploy the registered model."""
    import mlflow
    import os
    
    # Get the model version from the previous task
    ti = kwargs['ti']
    model_version = ti.xcom_pull(task_ids='register_model')
    
    # Configure MLflow
    mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
    
    # Transition the model to Production stage
    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name='innovate_analytics_model',
        version=model_version,
        stage='Production'
    )
    
    # Update the latest model symlink for the API
    model_path = f'/opt/airflow/models/latest'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Create or update symlink
    if os.path.exists(model_path):
        os.remove(model_path)
    
    os.symlink(
        f'/opt/airflow/mlruns/models/innovate_analytics_model/{model_version}',
        model_path
    )
    
    return True


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

notify = BashOperator(
    task_id='notify_deployment',
    bash_command='echo "ML pipeline completed successfully and model deployed to production!" > /opt/airflow/logs/deployment_notification.txt',
    dag=dag,
)

end = DummyOperator(
    task_id='end_pipeline',
    dag=dag,
)

# Define task dependencies
start >> extract >> transform >> train >> register >> deploy >> notify >> end 