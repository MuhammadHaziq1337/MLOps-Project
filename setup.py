from setuptools import find_packages, setup

setup(
    name="mlops_project",
    version="0.1.0",
    description="MLOps Project for Innovate Analytics Inc.",
    author="MLOps Team",
    author_email="mlops@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Data Processing
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.2.0",
        
        # MLOps Tools
        "mlflow>=2.0.0",
        "dvc>=2.50.0",
        
        # API
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pydantic>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
) 