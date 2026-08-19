from fastapi import FastAPI, HTTPException , status
from pydantic import BaseModel, Field
from enum import Enum

app = FastAPI()

issues = []
next_id = 1

class Priority(str, Enum):
    low ="low"
    medium="medium"
    high="high"
    critical="critical"

class Issue(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=100)
    description: str= Field(min_length=10)
    priority: Priority


class IssueData(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str= Field(min_length=10)
    priority: Priority

class IssuePatch(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, min_length=10)
    priority: Priority | None = None


@app.post("/issues", response_model=Issue,
    status_code=status.HTTP_201_CREATED)
def create_issue(issue: IssueData):
    global next_id

    new_issue = Issue(
        id=next_id,
        title=issue.title,
        description=issue.description,
        priority=issue.priority
    )

    issues.append(new_issue)
    next_id += 1

    return new_issue

@app.get("/issues", response_model=list[Issue])
def get_issues(
    priority: Priority | None = None,
    search: str | None = None,
    sort: str | None = None,
    skip: int = 0,
    limit: int = 10
):
    result = issues

    # FILTER
    if priority is not None:
        result = [
            issue for issue in result
            if issue.priority == priority
        ]

    # SEARCH
    if search is not None:
        result = [
            issue for issue in result
            if search.lower() in issue.title.lower()
            or search.lower() in issue.description.lower()
        ]

    # SORT
    if sort == "id":
        result = sorted(
            result,
            key=lambda issue: issue.id
        )

    if sort == "priority":
        priority_order = {
            Priority.low: 1,
            Priority.medium: 2,
            Priority.high: 3,
            Priority.critical: 4
        }

        result = sorted(
            result,
            key=lambda issue: priority_order[issue.priority]
        )

    # PAGINATION
    return result[skip:skip + limit]

@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue_by_ID(issue_id:int):
    for issue in issues:
        if issue_id == issue.id:
            return issue   

    raise HTTPException(
        status_code=404,
        detail="Issue not found"
    )
@app.put("/issues/{issue_id}", response_model=Issue)
def update_issue(issue_id: int, issue_data: IssueData):

    for issue in issues:
        if issue_id == issue.id:
            issue.title = issue_data.title
            issue.description = issue_data.description
            issue.priority = issue_data.priority

            return issue

    raise HTTPException(
        status_code=404,
        detail="Issue not found"
    )

@app.patch("/issues/{issue_id}",response_model=Issue)
def patch_issue(issue_id: int, issue_data: IssuePatch):
    for issue in issues:
        if issue_id == issue.id:

            updates = issue_data.model_dump(exclude_unset=True)

            for field, value in updates.items():
                setattr(issue, field, value)

            return issue

    raise HTTPException(
        status_code=404,
        detail="Issue not found"
    )

@app.delete("/issues/{issue_id}", response_model=Issue)
def delete_issue(issue_id: int):

    for issue in issues:
        if issue_id == issue.id:
            issues.remove(issue)
            return issue
        
    raise HTTPException(
    status_code=404,
    detail="Issue not found"
)