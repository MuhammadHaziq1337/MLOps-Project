# Sprint Planning Tools

This document provides instructions for using the sprint planning tools in our MLOps project.

## Overview

Our MLOps project uses an agile development process with 2-week sprints. We've created several tools to help streamline the sprint planning and management process:

1. GitHub Issue Templates
2. GitHub Labels
3. Sprint Creation Script
4. Pull Request Template

## GitHub CLI Installation

Some of our tools require the GitHub CLI to be installed. To install:

### Windows
```powershell
# Install with winget
winget install GitHub.cli

# Or with Chocolatey
choco install gh
```

### macOS
```bash
# Install with Homebrew
brew install gh
```

### Linux
```bash
# Debian/Ubuntu
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

After installation, authenticate with your GitHub account:
```bash
gh auth login
```

## Using the Sprint Creation Script

The sprint creation script (`scripts/create_sprint.py`) helps to set up a new sprint by:
- Creating a milestone for the sprint
- Creating sprint planning and review issues
- Assigning the correct labels and milestones

To use the script:

```bash
# Start a new sprint (sprint number 1) with today's date as the start date
python scripts/create_sprint.py 1

# Or specify a start date
python scripts/create_sprint.py 1 --start-date 2023-01-15
```

This will:
1. Create a new milestone for Sprint 1
2. Create a Sprint Planning issue
3. Create a Sprint Review and Retrospective issue
4. Output the milestone and issue IDs for reference

## GitHub Issue Templates

We have several issue templates to standardize our workflow:

### Creating a New Issue
1. Go to the repository on GitHub
2. Click on "Issues" tab
3. Click on "New Issue"
4. Select one of the templates:
   - Feature Request
   - Bug Report
   - Sprint Task
   - Technical Debt
5. Fill out the required information
6. Assign appropriate labels, milestone, and assignees

## GitHub Labels

We use standardized labels to categorize and prioritize our work. See [GitHub Labels](github_labels.md) for the complete list of labels and their meanings.

## Pull Request Process

All code changes should follow our pull request process:

1. Create a feature branch from `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. Push your branch to GitHub:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Create a pull request:
   - Go to the repository on GitHub
   - Click on "Pull Requests" tab
   - Click on "New Pull Request"
   - Select your feature branch
   - Fill out the pull request template
   - Request a review from at least one team member

5. After approval, merge your changes:
   - Click "Merge Pull Request"
   - Confirm the merge
   - Delete the branch (optional)

## Sprint Metrics and Reporting

At the end of each sprint, we track and report on several metrics:

1. **Velocity**: Number of story points completed
2. **Burndown Chart**: Progress throughout the sprint
3. **Completion Rate**: Percentage of committed stories completed
4. **Bug Count**: Number of bugs identified during the sprint

These metrics help us improve our estimation and planning for future sprints.

## GitHub Project Boards

We use GitHub Project boards to visualize our sprint progress:

1. **Sprint Board**: Tasks for the current sprint
2. **Product Backlog**: Upcoming features and tasks
3. **Bug Tracking**: Active bugs and their status

To access these boards, go to the "Projects" tab in the repository.

## Further Reading

- [Sprint Planning Guide](sprint_planning.md): Detailed guide for sprint planning
- [Definition of Done](../README.md#definition-of-done): Criteria for when a task is complete 