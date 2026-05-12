"""Tests for the Pydantic configuration model."""

import os
import tempfile

import pytest

from src.utils.default_config_settings import (
    AppConfig,
    default_config,
    load_config_from_file,
    save_config_to_file,
)


class TestAppConfig:
    def test_default_values(self):
        config = AppConfig()
        assert config.agent_type == "custom"
        assert config.max_steps == 100
        assert config.llm_provider == "openai"
        assert config.llm_model_name == "gpt-4o"
        assert config.window_w == 1280
        assert config.window_h == 1100

    def test_custom_values(self):
        config = AppConfig(
            agent_type="org",
            max_steps=50,
            llm_provider="anthropic",
            llm_model_name="claude-3-5-sonnet-20240620",
        )
        assert config.agent_type == "org"
        assert config.max_steps == 50
        assert config.llm_provider == "anthropic"

    def test_model_dump_roundtrip(self):
        config = AppConfig(max_steps=42)
        data = config.model_dump()
        restored = AppConfig(**data)
        assert restored.max_steps == 42
        assert data == restored.model_dump()

    def test_validates_types(self):
        config = AppConfig(max_steps="50")  # string coerced to int
        assert config.max_steps == 50
        assert isinstance(config.max_steps, int)


class TestDefaultConfig:
    def test_returns_dict(self):
        cfg = default_config()
        assert isinstance(cfg, dict)
        assert "agent_type" in cfg
        assert "llm_provider" in cfg

    def test_has_all_keys(self):
        cfg = default_config()
        model_fields = set(AppConfig.model_fields.keys())
        assert set(cfg.keys()) == model_fields


class TestSaveAndLoad:
    def test_save_and_load_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = default_config()
            settings["max_steps"] = 77
            result_msg = save_config_to_file(settings, save_dir=tmpdir)
            assert "saved" in result_msg.lower()

            files = [f for f in os.listdir(tmpdir) if f.endswith(".json")]
            assert len(files) == 1

            loaded = load_config_from_file(os.path.join(tmpdir, files[0]))
            assert isinstance(loaded, dict)
            assert loaded["max_steps"] == 77

    def test_load_nonexistent_file_returns_error_string(self):
        result = load_config_from_file("/tmp/nonexistent_config_file_xyz.json")
        assert isinstance(result, str)
        assert "error" in result.lower()

    def test_validates_on_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_settings = default_config()
            bad_settings["max_steps"] = "not_a_number"
            with pytest.raises(Exception):
                save_config_to_file(bad_settings, save_dir=tmpdir)

    def test_legacy_pickle_load(self):
        import pickle

        with tempfile.TemporaryDirectory() as tmpdir:
            pkl_path = os.path.join(tmpdir, "legacy.pkl")
            settings = {"agent_type": "org", "max_steps": 200}
            with open(pkl_path, "wb") as f:
                pickle.dump(settings, f)

            loaded = load_config_from_file(pkl_path)
            assert isinstance(loaded, dict)
            assert loaded["agent_type"] == "org"
            assert loaded["max_steps"] == 200
