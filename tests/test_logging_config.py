"""Tests for the centralized logging configuration."""

import json
import logging

import pytest

from src.utils.logging_config import ReadableFormatter, StructuredFormatter, setup_logging


class TestReadableFormatter:
    def test_format_contains_level_and_message(self):
        formatter = ReadableFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="hello %s", args=("world",), exc_info=None,
        )
        output = formatter.format(record)
        assert "INFO" in output
        assert "hello world" in output
        assert "test" in output


class TestStructuredFormatter:
    def test_outputs_valid_json(self):
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="mymodule", level=logging.WARNING, pathname="", lineno=0,
            msg="something happened", args=(), exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["level"] == "WARNING"
        assert data["msg"] == "something happened"
        assert data["logger"] == "mymodule"
        assert "ts" in data

    def test_includes_exception(self):
        formatter = StructuredFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test", level=logging.ERROR, pathname="", lineno=0,
                msg="failed", args=(), exc_info=sys.exc_info(),
            )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert "ValueError" in data["exception"]


class TestSetupLogging:
    def test_does_not_duplicate_handlers(self):
        root = logging.getLogger()
        original_count = len(root.handlers)
        setup_logging(level=logging.DEBUG)
        setup_logging(level=logging.DEBUG)
        assert len(root.handlers) <= original_count + 2
