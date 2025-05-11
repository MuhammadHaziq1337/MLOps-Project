# Sprint Planning Guide

This document outlines the sprint planning process for the MLOps project at Innovate Analytics Inc.

## Sprint Cycle

We follow a 2-week sprint cycle:
- **Sprint Planning**: Monday (Day 1)
- **Daily Standups**: Every weekday at 10:00 AM
- **Sprint Review**: Friday (Day 10)
- **Sprint Retrospective**: Friday (Day 10, after review)
- **Backlog Refinement**: Wednesday (Day 8)

## Sprint Planning Meeting

### Preparation
1. Product Owner ensures the backlog is prioritized
2. Scrum Master prepares the meeting agenda
3. Team members review the backlog items before the meeting

### During the Meeting
1. **Sprint Goal Definition** (15 minutes)
   - Define the objective for the upcoming sprint
   - Align on business value and expected outcomes

2. **Capacity Planning** (15 minutes)
   - Review team capacity (availability, vacations, etc.)
   - Determine story points capacity for the sprint

3. **Sprint Backlog Creation** (60 minutes)
   - Select user stories from the product backlog
   - Break down stories into tasks
   - Estimate tasks using story points (1, 2, 3, 5, 8, 13)
   - Commit to stories that can be completed within the sprint

4. **Risk Assessment** (15 minutes)
   - Identify potential risks or blockers
   - Create mitigation plans for identified risks

5. **Sprint Planning Wrap-up** (15 minutes)
   - Confirm sprint goal and commitments
   - Ensure all tasks have assignees
   - Set up the sprint board in GitHub Projects

## GitHub Projects Setup

We use GitHub Projects for sprint tracking:

1. **Sprint Milestone Creation**
   - Create a new milestone for each sprint
   - Set the start and end dates
   - Include the sprint goal in the description

2. **Issue Creation and Assignment**
   - Create issues using the appropriate templates
   - Link issues to the current sprint milestone
   - Assign story points using labels (SP1, SP2, SP3, SP5, SP8, SP13)
   - Assign issues to team members

3. **Sprint Board Columns**
   - **Backlog**: Issues prioritized but not yet started
   - **To Do**: Issues committed to for the current sprint
   - **In Progress**: Issues actively being worked on
   - **Review**: Issues ready for code review/testing
   - **Done**: Issues completed and meeting the Definition of Done

## Definition of Done

An issue is considered "Done" when:
- Code is implemented according to requirements
- Unit tests are written and passing
- Integration tests are passing
- Documentation is updated
- Code is reviewed and approved by at least one team member
- Changes are merged to the development branch
- CI/CD pipeline completes successfully

## Sprint Review

During the Sprint Review:
- Demo the completed work
- Get feedback from stakeholders
- Review what was completed vs. what was committed
- Discuss any challenges or blockers encountered

## Sprint Retrospective

During the Sprint Retrospective:
- What went well?
- What could be improved?
- What actions can we take to improve in the next sprint?

## Templates and Resources

- [Feature Request Template](/.github/ISSUE_TEMPLATE/feature_request.md)
- [Bug Report Template](/.github/ISSUE_TEMPLATE/bug_report.md)
- [Sprint Task Template](/.github/ISSUE_TEMPLATE/sprint_task.md)
- [Technical Debt Template](/.github/ISSUE_TEMPLATE/tech_debt.md) 