#!/usr/bin/env python
"""
GitHub Issues Setup Script

This script sets up GitHub Issues for sprint planning by creating milestones,
labels, and initial issues for an MLOps project.
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client for managing issues."""
    
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        """
        Initialize the GitHub client.
        
        Args:
            owner: GitHub username or organization
            repo: Repository name
            token: GitHub personal access token (defaults to GITHUB_TOKEN env var)
        """
        self.owner = owner
        self.repo = repo
        self.token = token or os.environ.get("GITHUB_TOKEN")
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
        
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_milestone(self, title: str, description: str, due_on: Optional[str] = None) -> Dict:
        """
        Create a new milestone.
        
        Args:
            title: Milestone title
            description: Milestone description
            due_on: Due date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
            
        Returns:
            Created milestone data
        """
        url = f"{self.base_url}/milestones"
        payload = {
            "title": title,
            "state": "open",
            "description": description
        }
        
        if due_on:
            payload["due_on"] = due_on
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            logger.info(f"Created milestone: {title}")
            return response.json()
        else:
            logger.error(f"Failed to create milestone: {response.text}")
            response.raise_for_status()
    
    def create_label(self, name: str, color: str, description: str) -> Dict:
        """
        Create a new label.
        
        Args:
            name: Label name
            color: Label color (hex code without #)
            description: Label description
            
        Returns:
            Created label data
        """
        url = f"{self.base_url}/labels"
        payload = {
            "name": name,
            "color": color.lstrip('#'),
            "description": description
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            logger.info(f"Created label: {name}")
            return response.json()
        elif response.status_code == 422:
            # Label already exists, try to update it
            logger.info(f"Label {name} already exists, updating...")
            return self.update_label(name, color, description)
        else:
            logger.error(f"Failed to create label: {response.text}")
            response.raise_for_status()
    
    def update_label(self, name: str, color: str, description: str) -> Dict:
        """
        Update an existing label.
        
        Args:
            name: Label name
            color: Label color (hex code without #)
            description: Label description
            
        Returns:
            Updated label data
        """
        url = f"{self.base_url}/labels/{name}"
        payload = {
            "color": color.lstrip('#'),
            "description": description
        }
        
        response = requests.patch(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            logger.info(f"Updated label: {name}")
            return response.json()
        else:
            logger.error(f"Failed to update label: {response.text}")
            response.raise_for_status()
    
    def create_issue(self, title: str, body: str, 
                    milestone_id: Optional[int] = None,
                    labels: Optional[List[str]] = None,
                    assignees: Optional[List[str]] = None) -> Dict:
        """
        Create a new issue.
        
        Args:
            title: Issue title
            body: Issue description
            milestone_id: Milestone ID to assign
            labels: List of label names to apply
            assignees: List of usernames to assign
            
        Returns:
            Created issue data
        """
        url = f"{self.base_url}/issues"
        payload = {
            "title": title,
            "body": body
        }
        
        if milestone_id:
            payload["milestone"] = milestone_id
        
        if labels:
            payload["labels"] = labels
        
        if assignees:
            payload["assignees"] = assignees
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 201:
            logger.info(f"Created issue: {title}")
            return response.json()
        else:
            logger.error(f"Failed to create issue: {response.text}")
            response.raise_for_status()


def setup_mlops_project(github_client: GitHubClient) -> None:
    """
    Set up GitHub Issues for an MLOps project.
    
    Args:
        github_client: Initialized GitHub client
    """
    # Create sprint milestones
    sprint_start = datetime.now()
    sprint_end = sprint_start + timedelta(days=14)
    sprint_1 = github_client.create_milestone(
        title="Sprint 1",
        description="First sprint focusing on project setup and basic infrastructure",
        due_on=sprint_end.strftime("%Y-%m-%dT23:59:59Z")
    )
    
    sprint_start = sprint_end
    sprint_end = sprint_start + timedelta(days=14)
    sprint_2 = github_client.create_milestone(
        title="Sprint 2",
        description="Second sprint focusing on data pipeline and model training",
        due_on=sprint_end.strftime("%Y-%m-%dT23:59:59Z")
    )
    
    # Create custom labels
    github_client.create_label(
        name="data-pipeline",
        color="0075ca",
        description="Issues related to data ingestion and processing"
    )
    
    github_client.create_label(
        name="model-training",
        color="d876e3",
        description="Issues related to model training and evaluation"
    )
    
    github_client.create_label(
        name="deployment",
        color="fbca04",
        description="Issues related to model deployment"
    )
    
    github_client.create_label(
        name="monitoring",
        color="0e8a16",
        description="Issues related to model monitoring and observability"
    )
    
    github_client.create_label(
        name="documentation",
        color="1d76db",
        description="Issues related to documentation and guides"
    )
    
    github_client.create_label(
        name="priority-high",
        color="d73a4a",
        description="High priority tasks that should be addressed first"
    )
    
    github_client.create_label(
        name="priority-medium",
        color="fbca04",
        description="Medium priority tasks"
    )
    
    github_client.create_label(
        name="priority-low",
        color="0e8a16",
        description="Low priority tasks that can be addressed later"
    )
    
    # Create initial issues for Sprint 1
    initial_issues = [
        {
            "title": "Set up GitHub Issue Templates",
            "body": """
## Description
Create GitHub Issue templates for feature requests, bug reports, sprint tasks, and technical debt.

## Acceptance Criteria
- [ ] Create feature request template
- [ ] Create bug report template
- [ ] Create sprint task template
- [ ] Create technical debt template
- [ ] Update README with information about issue templates

## Estimation
Story points: 2
            """,
            "milestone_id": sprint_1["number"],
            "labels": ["documentation", "priority-high"]
        },
        {
            "title": "Set up Data Versioning with DVC",
            "body": """
## Description
Set up Data Version Control (DVC) for the project to track datasets and ML pipelines.

## Acceptance Criteria
- [ ] Initialize DVC in the project
- [ ] Configure DVC remote storage
- [ ] Create example datasets
- [ ] Track datasets with DVC
- [ ] Define ML pipeline in dvc.yaml
- [ ] Document DVC usage in the project

## Estimation
Story points: 5
            """,
            "milestone_id": sprint_1["number"],
            "labels": ["data-pipeline", "priority-high"]
        },
        {
            "title": "Implement CI/CD Pipeline with GitHub Actions",
            "body": """
## Description
Set up CI/CD pipeline using GitHub Actions to automate testing, building, and deployment.

## Acceptance Criteria
- [ ] Create workflow for running tests
- [ ] Create workflow for linting and code quality checks
- [ ] Create workflow for building Docker images
- [ ] Create workflow for deploying to test environment
- [ ] Document CI/CD process in the project

## Estimation
Story points: 8
            """,
            "milestone_id": sprint_1["number"],
            "labels": ["deployment", "priority-high"]
        }
    ]
    
    # Create the issues
    for issue_data in initial_issues:
        github_client.create_issue(
            title=issue_data["title"],
            body=issue_data["body"],
            milestone_id=issue_data["milestone_id"],
            labels=issue_data["labels"]
        )
    
    logger.info("MLOps project setup complete")


def main():
    """Parse command line arguments and run setup."""
    parser = argparse.ArgumentParser(description="Set up GitHub Issues for MLOps project")
    parser.add_argument("--owner", required=True, help="GitHub username or organization")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--token", help="GitHub personal access token (defaults to GITHUB_TOKEN env var)")
    
    args = parser.parse_args()
    
    try:
        github_client = GitHubClient(args.owner, args.repo, args.token)
        setup_mlops_project(github_client)
        return 0
    
    except Exception as e:
        logger.error(f"Error setting up GitHub Issues: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 