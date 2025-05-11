# GitHub Labels for MLOps Project

This document defines the labels we use for our GitHub issues and pull requests.

## Issue Types

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `#d73a4a` | Something isn't working as expected |
| `enhancement` | `#a2eeef` | New feature or request |
| `documentation` | `#0075ca` | Improvements or additions to documentation |
| `task` | `#7057ff` | A task that needs to be completed |
| `tech-debt` | `#fbca04` | Technical debt that needs to be addressed |
| `question` | `#d876e3` | Further information is requested |
| `duplicate` | `#cfd3d7` | This issue or pull request already exists |
| `invalid` | `#e4e669` | This doesn't seem right |
| `wontfix` | `#ffffff` | This will not be worked on |

## Priority Labels

| Label | Color | Description |
|-------|-------|-------------|
| `priority:critical` | `#b60205` | Must be fixed ASAP |
| `priority:high` | `#d93f0b` | Should be fixed in the current sprint |
| `priority:medium` | `#fbca04` | Should be addressed soon |
| `priority:low` | `#0e8a16` | Nice to have |

## Status Labels

| Label | Color | Description |
|-------|-------|-------------|
| `status:blocked` | `#d73a4a` | Work is blocked by another issue |
| `status:needs-review` | `#0075ca` | Ready for review |
| `status:in-progress` | `#0e8a16` | Currently being worked on |
| `status:ready` | `#0075ca` | Ready to be worked on |

## Component Labels

| Label | Color | Description |
|-------|-------|-------------|
| `component:data-processing` | `#bfdadc` | Related to data processing |
| `component:model-training` | `#c5def5` | Related to model training |
| `component:model-serving` | `#d4c5f9` | Related to model serving |
| `component:ci-cd` | `#c2e0c6` | Related to CI/CD pipeline |
| `component:kubernetes` | `#fef2c0` | Related to Kubernetes deployment |
| `component:monitoring` | `#f9d0c4` | Related to monitoring |

## Effort Labels

| Label | Color | Description |
|-------|-------|-------------|
| `SP1` | `#c5def5` | 1 Story Point |
| `SP2` | `#c5def5` | 2 Story Points |
| `SP3` | `#c5def5` | 3 Story Points |
| `SP5` | `#c5def5` | 5 Story Points |
| `SP8` | `#c5def5` | 8 Story Points |
| `SP13` | `#c5def5` | 13 Story Points |

## Sprint Labels

| Label | Color | Description |
|-------|-------|-------------|
| `sprint:current` | `#0e8a16` | Assigned to current sprint |
| `sprint:next` | `#fbca04` | Planned for next sprint |
| `sprint:backlog` | `#d4c5f9` | In the product backlog |

## Creating Labels in GitHub

To create these labels in your repository:
1. Go to your repository on GitHub
2. Click on "Issues" tab
3. Click on "Labels"
4. Click on "New label"
5. Enter the name, select a color, and add a description
6. Click "Create label"

You can also use GitHub CLI or the GitHub API to create these labels programmatically. 