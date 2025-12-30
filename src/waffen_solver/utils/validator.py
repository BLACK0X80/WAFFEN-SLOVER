"""
Input validation utilities for Waffen-Solver.

Provides validation for various inputs including
error messages, paths, and configuration values.
"""

import re
from pathlib import Path
from typing import Any, List, Optional, Type

from waffen_solver.exceptions import WaffenSolverException


class ValidationException(WaffenSolverException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize with optional field context."""
        details = {"field": field} if field else {}
        super().__init__(message, "VALIDATION_ERROR", details)


class Validator:
    """
    Validates various inputs for the application.

    Provides static methods for validating different
    types of input data.
    """

    @staticmethod
    def validate_not_empty(value: str, field_name: str = "value") -> str:
        """
        Validate that string is not empty.

        Args:
            value: String to validate.
            field_name: Name of field for error messages.

        Returns:
            The validated string.

        Raises:
            ValidationException: If string is empty.
        """
        if not value or not value.strip():
            raise ValidationException(f"{field_name} cannot be empty", field_name)
        return value.strip()

    @staticmethod
    def validate_path_exists(path: Path, field_name: str = "path") -> Path:
        """
        Validate that path exists.

        Args:
            path: Path to validate.
            field_name: Name of field for error messages.

        Returns:
            The validated path.

        Raises:
            ValidationException: If path does not exist.
        """
        if not path.exists():
            raise ValidationException(f"Path does not exist: {path}", field_name)
        return path

    @staticmethod
    def validate_file_exists(path: Path, field_name: str = "file") -> Path:
        """
        Validate that file exists.

        Args:
            path: Path to validate.
            field_name: Name of field for error messages.

        Returns:
            The validated path.

        Raises:
            ValidationException: If file does not exist.
        """
        if not path.is_file():
            raise ValidationException(f"File does not exist: {path}", field_name)
        return path

    @staticmethod
    def validate_directory_exists(path: Path, field_name: str = "directory") -> Path:
        """
        Validate that directory exists.

        Args:
            path: Path to validate.
            field_name: Name of field for error messages.

        Returns:
            The validated path.

        Raises:
            ValidationException: If directory does not exist.
        """
        if not path.is_dir():
            raise ValidationException(f"Directory does not exist: {path}", field_name)
        return path

    @staticmethod
    def validate_in_range(
        value: int,
        min_val: int,
        max_val: int,
        field_name: str = "value",
    ) -> int:
        """
        Validate that integer is in range.

        Args:
            value: Value to validate.
            min_val: Minimum allowed value.
            max_val: Maximum allowed value.
            field_name: Name of field for error messages.

        Returns:
            The validated value.

        Raises:
            ValidationException: If value is out of range.
        """
        if value < min_val or value > max_val:
            raise ValidationException(
                f"{field_name} must be between {min_val} and {max_val}",
                field_name,
            )
        return value

    @staticmethod
    def validate_type(
        value: Any,
        expected_type: Type[Any],
        field_name: str = "value",
    ) -> Any:
        """
        Validate that value is of expected type.

        Args:
            value: Value to validate.
            expected_type: Expected type.
            field_name: Name of field for error messages.

        Returns:
            The validated value.

        Raises:
            ValidationException: If value is wrong type.
        """
        if not isinstance(value, expected_type):
            raise ValidationException(
                f"{field_name} must be of type {expected_type.__name__}",
                field_name,
            )
        return value

    @staticmethod
    def validate_list_not_empty(
        value: List[Any],
        field_name: str = "list",
    ) -> List[Any]:
        """
        Validate that list is not empty.

        Args:
            value: List to validate.
            field_name: Name of field for error messages.

        Returns:
            The validated list.

        Raises:
            ValidationException: If list is empty.
        """
        if not value:
            raise ValidationException(f"{field_name} cannot be empty", field_name)
        return value

    @staticmethod
    def validate_error_message(message: str) -> str:
        """
        Validate and sanitize error message.

        Args:
            message: Error message to validate.

        Returns:
            Sanitized error message.

        Raises:
            ValidationException: If message is invalid.
        """
        message = Validator.validate_not_empty(message, "error_message")
        message = message[:10000]
        return message

    @staticmethod
    def validate_api_key(key: str, field_name: str = "api_key") -> str:
        """
        Validate API key format.

        Args:
            key: API key to validate.
            field_name: Name of field for error messages.

        Returns:
            The validated API key.

        Raises:
            ValidationException: If key is invalid.
        """
        key = Validator.validate_not_empty(key, field_name)
        if len(key) < 10:
            raise ValidationException(f"{field_name} appears to be invalid", field_name)
        return key

    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize a string by removing control characters.

        Args:
            value: String to sanitize.

        Returns:
            Sanitized string.
        """
        control_chars = "".join(chr(i) for i in range(32) if i not in (9, 10, 13))
        return re.sub(f"[{re.escape(control_chars)}]", "", value)
