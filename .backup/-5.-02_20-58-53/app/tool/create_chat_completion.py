from typing import Any, List, Optional, Type, Union, get_args, get_origin

from pydantic import BaseModel, Field

from app.tool import BaseTool


class CreateChatCompletion(BaseTool):
    """Creates a structured completion with specified output formatting."""

    name: str = "create_chat_completion"
    description: str = "Creates a structured completion with specified output formatting."

    # Стандартные параметры
    parameters: dict = {
        "type": "object",
        "properties": {
            "response": {
                "type": "string",
                "description": "The response text that should be delivered to the user.",
            },
        },
        "required": ["response"],
    }

    # Вспомогательные статические переменные
    _type_mapping: dict = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }

    _response_type = str
    _required = ["response"]

    def __init__(self, response_type: Optional[Type] = str):
        """Initialize with a specific response type."""
        super().__init__(
            name="create_chat_completion",
            description="Creates a structured completion with specified output formatting.",
            parameters=self._generate_parameters(response_type)
        )
        self._response_type = response_type

    @classmethod
    def _generate_parameters(cls, response_type: Type) -> dict:
        """Генерирует параметры на основе типа ответа."""
        if response_type == str:
            return {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "string",
                        "description": "The response text that should be delivered to the user.",
                    },
                },
                "required": ["response"],
            }

        if isinstance(response_type, type) and issubclass(response_type, BaseModel):
            schema = response_type.model_json_schema()
            return {
                "type": "object",
                "properties": schema["properties"],
                "required": schema.get("required", ["response"]),
            }

        return cls._create_type_schema(response_type)

    @classmethod
    def _create_type_schema(cls, type_hint: Type) -> dict:
        """Create a JSON schema for the given type."""
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        # Handle primitive types
        if origin is None:
            return {
                "type": "object",
                "properties": {
                    "response": {
                        "type": cls._type_mapping.get(type_hint, "string"),
                        "description": f"Response of type {type_hint.__name__}",
                    }
                },
                "required": ["response"],
            }

        # Handle List type
        if origin is list:
            item_type = args[0] if args else Any
            return {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "array",
                        "items": cls._get_type_info(item_type),
                    }
                },
                "required": ["response"],
            }

        # Handle Dict type
        if origin is dict:
            value_type = args[1] if len(args) > 1 else Any
            return {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "object",
                        "additionalProperties": cls._get_type_info(value_type),
                    }
                },
                "required": ["response"],
            }

        # Handle Union type
        if origin is Union:
            return cls._create_union_schema(args)

        return {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "The response text that should be delivered to the user.",
                },
            },
            "required": ["response"],
        }

    @classmethod
    def _get_type_info(cls, type_hint: Type) -> dict:
        """Get type information for a single type."""
        if isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
            return type_hint.model_json_schema()

        return {
            "type": cls._type_mapping.get(type_hint, "string"),
            "description": f"Value of type {getattr(type_hint, '__name__', 'any')}",
        }

    @classmethod
    def _create_union_schema(cls, types: tuple) -> dict:
        """Create schema for Union types."""
        return {
            "type": "object",
            "properties": {
                "response": {"anyOf": [cls._get_type_info(t) for t in types]}
            },
            "required": ["response"],
        }

    async def execute(self, required: list | None = None, **kwargs) -> Any:
        """Execute the chat completion with type conversion.

        Args:
            required: List of required field names or None
            **kwargs: Response data

        Returns:
            Converted response based on response_type
        """
        required = required or ["response"]

        # Handle case when required is a list
        if isinstance(required, list) and len(required) > 0:
            if len(required) == 1:
                required_field = required[0]
                result = kwargs.get(required_field, "")
            else:
                # Return multiple fields as a dictionary
                return {field: kwargs.get(field, "") for field in required}
        else:
            required_field = "response"
            result = kwargs.get(required_field, "")

        # Type conversion logic
        if self._response_type == str:
            return result

        if isinstance(self._response_type, type) and issubclass(
            self._response_type, BaseModel
        ):
            return self._response_type(**kwargs)

        if get_origin(self._response_type) in (list, dict):
            return result  # Assuming result is already in correct format

        try:
            return self._response_type(result)
        except (ValueError, TypeError):
            return result
