import pytest
from datetime import datetime
from pr_agent.models.events import (
    WorkflowRun,
    CheckRun,
    GitHubEvent,
    WorkflowStatus,
)


class TestWorkflowRun:
    """Test WorkflowRun model."""
    
    def test_valid_workflow_run(self):
        """Test creating a valid WorkflowRun."""
        workflow = WorkflowRun(
            name="CI",
            status="completed",
            conclusion="success",
            run_number=42,
            html_url="https://github.com/user/repo/actions/runs/123",
            updated_at="2024-01-15T10:30:00Z"
        )
        assert workflow.name == "CI"
        assert workflow.status == "completed"
        assert workflow.conclusion == "success"
        assert workflow.run_number == 42
    
    def test_workflow_run_with_optional_fields(self):
        """Test WorkflowRun with optional fields."""
        workflow = WorkflowRun(
            name="CI",
            status="in_progress",
            run_number=1,
            html_url="https://github.com/user/repo/actions/runs/123"
        )
        assert workflow.conclusion is None
        assert workflow.updated_at is None
    
    def test_workflow_run_extra_fields(self):
        """Test that extra fields are allowed."""
        workflow = WorkflowRun(
            name="CI",
            status="completed",
            run_number=1,
            html_url="https://github.com/user/repo/actions/runs/123",
            extra_field="allowed"
        )
        assert hasattr(workflow, "extra_field")


class TestGitHubEvent:
    """Test GitHubEvent model."""
    
    def test_valid_event(self):
        """Test creating a valid GitHubEvent."""
        workflow_run = WorkflowRun(
            name="CI",
            status="completed",
            conclusion="success",
            run_number=42,
            html_url="https://github.com/user/repo/actions/runs/123"
        )
        
        event = GitHubEvent(
            timestamp="2024-01-15T10:30:00.123456",
            event_type="workflow_run",
            action="completed",
            workflow_run=workflow_run,
            repository="user/repo",
            sender="octocat"
        )
        
        assert event.event_type == "workflow_run"
        assert event.action == "completed"
        assert event.workflow_run is not None
        assert event.workflow_run.name == "CI"
        assert event.repository == "user/repo"
    
    def test_event_without_workflow_run(self):
        """Test event without workflow_run."""
        event = GitHubEvent(
            timestamp="2024-01-15T10:30:00.123456",
            event_type="push",
            repository="user/repo"
        )
        assert event.workflow_run is None
        assert event.check_run is None
    
    def test_event_timestamp_validation(self):
        """Test timestamp validation."""
        # Valid timestamp
        event = GitHubEvent(
            timestamp="2024-01-15T10:30:00.123456",
            event_type="workflow_run"
        )
        assert event.timestamp == "2024-01-15T10:30:00.123456"
        
        # Invalid timestamp should raise error
        with pytest.raises(Exception):  # Pydantic validation error
            GitHubEvent(
                timestamp="invalid-timestamp",
                event_type="workflow_run"
            )


class TestWorkflowStatus:
    """Test WorkflowStatus model."""
    
    def test_valid_workflow_status(self):
        """Test creating a valid WorkflowStatus."""
        status = WorkflowStatus(
            name="CI",
            status="completed",
            conclusion="success",
            run_number=42,
            updated_at="2024-01-15T10:30:00Z",
            html_url="https://github.com/user/repo/actions/runs/123"
        )
        assert status.name == "CI"
        assert status.status == "completed"
        assert status.conclusion == "success"
    
    def test_workflow_status_model_dump(self):
        """Test converting to dict."""
        status = WorkflowStatus(
            name="CI",
            status="completed",
            conclusion="success",
            run_number=42,
            updated_at="2024-01-15T10:30:00Z",
            html_url="https://github.com/user/repo/actions/runs/123"
        )
        data = status.model_dump(exclude_none=True)
        assert isinstance(data, dict)
        assert data["name"] == "CI"
        assert "conclusion" in data


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_event_serialization(self):
        """Test event can be serialized to dict."""
        workflow_run = WorkflowRun(
            name="CI",
            status="completed",
            conclusion="success",
            run_number=42,
            html_url="https://github.com/user/repo/actions/runs/123"
        )
        
        event = GitHubEvent(
            timestamp="2024-01-15T10:30:00.123456",
            event_type="workflow_run",
            action="completed",
            workflow_run=workflow_run,
            repository="user/repo"
        )
        
        # Convert to dict
        event_dict = event.model_dump(exclude_none=True)
        assert isinstance(event_dict, dict)
        assert event_dict["event_type"] == "workflow_run"
        assert "workflow_run" in event_dict
        
        # Convert back from dict
        event_restored = GitHubEvent.model_validate(event_dict)
        assert event_restored.event_type == event.event_type
        assert event_restored.workflow_run is not None
        assert event_restored.workflow_run.name == "CI"

