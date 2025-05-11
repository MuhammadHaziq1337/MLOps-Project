#!/usr/bin/env python
"""
Script to create a new sprint milestone and setup initial tasks in GitHub.
Requires GitHub CLI (gh) to be installed and authenticated.
"""

import argparse
import datetime
import json
import subprocess
import sys
from typing import List, Optional


def run_command(command: List[str]) -> str:
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Error message: {e.stderr}")
        sys.exit(1)


def create_milestone(title: str, description: str, due_date: str) -> int:
    """Create a new milestone in GitHub and return its ID."""
    command = [
        "gh", "api", "--method", "POST", "repos/:owner/:repo/milestones",
        "-f", f"title={title}",
        "-f", f"description={description}",
        "-f", f"due_on={due_date}",
    ]
    
    response = run_command(command)
    milestone_data = json.loads(response)
    print(f"Created milestone: {title} (ID: {milestone_data['number']})")
    return milestone_data["number"]


def create_issue(title: str, body: str, labels: List[str], milestone: int) -> int:
    """Create a new issue in GitHub and return its ID."""
    labels_arg = ",".join(labels)
    
    command = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
        "--label", labels_arg,
        "--milestone", str(milestone),
    ]
    
    response = run_command(command)
    # Extract issue number from response like "https://github.com/user/repo/issues/123"
    issue_url = response.strip()
    issue_number = issue_url.split("/")[-1]
    print(f"Created issue: {title} (#{issue_number})")
    return int(issue_number)


def create_sprint_planning_issue(milestone: int, sprint_number: int, start_date: datetime.date) -> int:
    """Create a sprint planning issue."""
    title = f"[TASK] Sprint {sprint_number} Planning"
    
    body = f"""## Sprint {sprint_number} Planning

### Date
{start_date.strftime('%Y-%m-%d')}

### Agenda
1. Review previous sprint (if applicable)
2. Define sprint goal
3. Capacity planning
4. Select user stories from backlog
5. Break down stories into tasks
6. Estimate tasks
7. Risk assessment
8. Sprint planning wrap-up

### Preparation
- Product Owner: Ensure backlog is prioritized
- Scrum Master: Prepare meeting agenda
- Team: Review backlog items before the meeting

### Output
- Sprint goal
- Sprint backlog
- Task assignments
- Risk mitigation plan

### Reference
See [Sprint Planning Guide](/docs/sprint_planning.md) for more details.
"""
    
    labels = ["task", "priority:high", "component:ci-cd", "sprint:current"]
    return create_issue(title, body, labels, milestone)


def create_sprint_review_issue(milestone: int, sprint_number: int, review_date: datetime.date) -> int:
    """Create a sprint review issue."""
    title = f"[TASK] Sprint {sprint_number} Review and Retrospective"
    
    body = f"""## Sprint {sprint_number} Review and Retrospective

### Date
{review_date.strftime('%Y-%m-%d')}

### Review Agenda
1. Demo completed work
2. Get feedback from stakeholders
3. Review sprint goal achievement
4. Discuss challenges encountered

### Retrospective Agenda
1. What went well?
2. What could be improved?
3. Action items for next sprint

### Preparation
- Team: Prepare demos
- Scrum Master: Prepare metrics on sprint performance
- Product Owner: Collect stakeholder feedback

### Output
- Sprint review notes
- Retrospective action items
- Updated product backlog
"""
    
    labels = ["task", "priority:high", "component:ci-cd", "sprint:current"]
    return create_issue(title, body, labels, milestone)


def setup_sprint(sprint_number: int, start_date_str: Optional[str] = None) -> None:
    """Set up a new sprint with milestone and initial issues."""
    # Parse start date or use today
    if start_date_str:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    else:
        start_date = datetime.date.today()
    
    # Calculate sprint dates (2-week sprint)
    end_date = start_date + datetime.timedelta(days=13)
    review_date = end_date - datetime.timedelta(days=3)
    
    # Create milestone
    milestone_title = f"Sprint {sprint_number}"
    milestone_description = f"Sprint {sprint_number} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
    milestone_due_date = f"{end_date.strftime('%Y-%m-%d')}T23:59:59Z"
    
    milestone_id = create_milestone(milestone_title, milestone_description, milestone_due_date)
    
    # Create sprint planning issue
    planning_issue_id = create_sprint_planning_issue(milestone_id, sprint_number, start_date)
    
    # Create sprint review issue
    review_issue_id = create_sprint_review_issue(milestone_id, sprint_number, review_date)
    
    print("\nSprint setup complete!")
    print(f"Sprint {sprint_number}: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Milestone ID: {milestone_id}")
    print(f"Planning Issue: #{planning_issue_id}")
    print(f"Review Issue: #{review_issue_id}")


def main() -> None:
    """Main function to parse arguments and set up the sprint."""
    parser = argparse.ArgumentParser(description="Create a new sprint in GitHub")
    parser.add_argument("sprint_number", type=int, help="Sprint number")
    parser.add_argument("--start-date", type=str, help="Sprint start date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    setup_sprint(args.sprint_number, args.start_date)


if __name__ == "__main__":
    main() 