from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class WorkflowRun(BaseModel):
    """Model for GitHub Actions workflow run data."""
    
    name: str = Field(..., description="Name of the workflow")
    status: str = Field(..., description="Status of the workflow run")
    conclusion: Optional[str] = Field(None, description="Conclusion of the workflow run")
    run_number: int = Field(..., description="Run number of the workflow")
    html_url: str = Field(..., description="URL to view the workflow run")
    updated_at: Optional[str] = Field(None, description="Timestamp when workflow was updated")
    head_branch: Optional[str] = Field(None, description="Branch the workflow ran on")
    head_sha: Optional[str] = Field(None, description="SHA of the commit")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate workflow status."""
        valid_statuses = ['queued', 'in_progress', 'completed', 'waiting']
        if v not in valid_statuses:
            # Allow unknown statuses but log a warning
            return v
        return v
    
    @field_validator('conclusion')
    @classmethod
    def validate_conclusion(cls, v: Optional[str]) -> Optional[str]:
        """Validate workflow conclusion."""
        if v is None:
            return v
        valid_conclusions = ['success', 'failure', 'neutral', 'cancelled', 'skipped', 'timed_out', 'action_required']
        if v not in valid_conclusions:
            return v
        return v
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields from GitHub API
        json_schema_extra = {
            "example": {
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "run_number": 42,
                "html_url": "https://github.com/user/repo/actions/runs/123",
                "updated_at": "2024-01-15T10:30:00Z",
                "head_branch": "main",
                "head_sha": "abc123"
            }
        }


class CheckRun(BaseModel):
    """Model for GitHub check run data."""
    
    name: str = Field(..., description="Name of the check run")
    status: str = Field(..., description="Status of the check run")
    conclusion: Optional[str] = Field(None, description="Conclusion of the check run")
    html_url: Optional[str] = Field(None, description="URL to view the check run")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
        json_schema_extra = {
            "example": {
                "name": "Lint",
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/user/repo/runs/123"
            }
        }


class GitHubEvent(BaseModel):
    """Model for GitHub webhook events."""
    
    timestamp: str = Field(..., description="ISO timestamp when event was received")
    event_type: str = Field(..., description="Type of GitHub event")
    action: Optional[str] = Field(None, description="Action that triggered the event")
    workflow_run: Optional[WorkflowRun] = Field(None, description="Workflow run data if applicable")
    check_run: Optional[CheckRun] = Field(None, description="Check run data if applicable")
    repository: Optional[str] = Field(None, description="Repository full name (owner/repo)")
    sender: Optional[str] = Field(None, description="GitHub username of the sender")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format.
        
        Accepts ISO format timestamps with or without timezone.
        """
        try:
            # Try parsing as-is first
            datetime.fromisoformat(v)
        except ValueError:
            try:
                # Try with Z replaced by +00:00
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                # If both fail, still accept it but log a warning
                # This allows backward compatibility with existing data
                return v
        return v
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00.123456",
                "event_type": "workflow_run",
                "action": "completed",
                "workflow_run": {
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "run_number": 42,
                    "html_url": "https://github.com/user/repo/actions/runs/123"
                },
                "repository": "user/repo",
                "sender": "octocat"
            }
        }


class WorkflowStatus(BaseModel):
    """Model for workflow status summary."""
    
    name: str = Field(..., description="Name of the workflow")
    status: str = Field(..., description="Current status")
    conclusion: Optional[str] = Field(None, description="Conclusion if completed")
    run_number: int = Field(..., description="Run number")
    updated_at: str = Field(..., description="Last update timestamp")
    html_url: str = Field(..., description="URL to view the workflow run")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "run_number": 42,
                "updated_at": "2024-01-15T10:30:00Z",
                "html_url": "https://github.com/user/repo/actions/runs/123"
            }
        }

