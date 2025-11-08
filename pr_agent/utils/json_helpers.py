import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)


def to_json_string(
    data: Any,
    indent: int = 2,
    default: Optional[Any] = None
) -> str:
    """Convert data to JSON string with consistent formatting.
    
    Args:
        data: Data to serialize (can be dict, list, Pydantic model, etc.)
        indent: JSON indentation level (default: 2)
        default: Optional default function for JSON serialization
        
    Returns:
        JSON string representation of data
    """
    try:
        # Handle Pydantic models
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_none=True)
        # Handle lists of Pydantic models
        elif isinstance(data, list) and data and isinstance(data[0], BaseModel):
            data = [item.model_dump(exclude_none=True) if isinstance(item, BaseModel) else item for item in data]
        
        return json.dumps(data, indent=indent, default=default or str)
    except (TypeError, ValueError) as e:
        logger.error("Failed to serialize data to JSON", error=str(e), data_type=type(data).__name__)
        # Fallback to string representation
        return json.dumps({"error": "Failed to serialize data", "message": str(e)}, indent=indent)


def from_json_string(
    json_str: str,
    default: Optional[Any] = None
) -> Any:
    """Parse JSON string to Python object.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed Python object or default value
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON string", error=str(e), json_preview=json_str[:100])
        return default


def safe_model_validate(
    model_class: type[BaseModel],
    data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Optional[BaseModel]:
    """Safely validate data against a Pydantic model with error handling.
    
    Args:
        model_class: Pydantic model class to validate against
        data: Data dictionary to validate
        context: Optional context for logging (e.g., {"event_type": "workflow_run"})
        
    Returns:
        Validated model instance or None if validation fails
    """
    try:
        return model_class.model_validate(data)
    except Exception as e:
        log_context = context or {}
        logger.warning(
            "Failed to validate data against model",
            model=model_class.__name__,
            error=str(e),
            data_keys=list(data.keys()) if isinstance(data, dict) else [],
            **log_context
        )
        return None


def validate_models_batch(
    model_class: type[BaseModel],
    data_list: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None
) -> List[BaseModel]:
    """Validate a batch of data dictionaries against a Pydantic model.
    
    Args:
        model_class: Pydantic model class to validate against
        data_list: List of data dictionaries to validate
        context: Optional context for logging
        
    Returns:
        List of successfully validated model instances
    """
    validated: List[BaseModel] = []
    for item in data_list:
        model = safe_model_validate(model_class, item, context)
        if model:
            validated.append(model)
    return validated

