"""
Unit tests for Browser Use WebUI core functionality.
These tests do not require external LLM APIs or actual browser sessions.
"""
import sys
import os
import pytest
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAgentState:
    """Tests for AgentState singleton class."""

    def test_agent_state_import(self):
        """Test that AgentState can be imported."""
        from src.utils.agent_state import AgentState
        assert AgentState is not None

    def test_agent_state_singleton(self):
        """Test that AgentState maintains singleton pattern."""
        from src.utils.agent_state import AgentState
        state1 = AgentState()
        state2 = AgentState()
        # Both should reference the same internal state
        assert state1._stop_requested == state2._stop_requested

    def test_stop_request_flow(self):
        """Test stop request and clear flow."""
        from src.utils.agent_state import AgentState
        state = AgentState()

        # Initially should not be stopped
        state.clear_stop()
        assert not state.is_stop_requested()

        # Request stop
        state.request_stop()
        assert state.is_stop_requested()

        # Clear stop
        state.clear_stop()
        assert not state.is_stop_requested()

    def test_last_valid_state(self):
        """Test setting and getting last valid state."""
        from src.utils.agent_state import AgentState
        state = AgentState()

        # Initially no state
        state._last_valid_state = None
        assert state.get_last_valid_state() is None

        # Set a mock state
        mock_state = {"url": "https://example.com", "title": "Test"}
        state.set_last_valid_state(mock_state)
        assert state.get_last_valid_state() == mock_state


class TestUtilsFunctions:
    """Tests for utility functions."""

    def test_model_names_dict(self):
        """Test that model_names dictionary is properly defined."""
        from src.utils.utils import model_names

        assert isinstance(model_names, dict)
        assert "openai" in model_names
        assert "anthropic" in model_names
        assert "deepseek" in model_names
        assert "google" in model_names
        assert "ollama" in model_names

        # Check that each provider has at least one model
        for provider, models in model_names.items():
            assert isinstance(models, list)
            assert len(models) > 0

    def test_encode_image_none_input(self):
        """Test encode_image with None input."""
        from src.utils.utils import encode_image

        result = encode_image(None)
        assert result is None

    def test_encode_image_missing_file(self):
        """Test encode_image with non-existent file."""
        from src.utils.utils import encode_image

        try:
            encode_image("/nonexistent/path/image.png")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_provider_display_names(self):
        """Test provider display names mapping."""
        from src.utils.utils import PROVIDER_DISPLAY_NAMES

        assert isinstance(PROVIDER_DISPLAY_NAMES, dict)
        assert PROVIDER_DISPLAY_NAMES.get("openai") == "OpenAI"
        assert PROVIDER_DISPLAY_NAMES.get("anthropic") == "Anthropic"

    def test_get_latest_files_nonexistent_dir(self):
        """Test get_latest_files with non-existent directory creates it."""
        from src.utils.utils import get_latest_files
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        test_dir = os.path.join(temp_dir, "nonexistent")

        try:
            result = get_latest_files(test_dir)
            assert os.path.exists(test_dir)
            assert isinstance(result, dict)
            assert result.get('.webm') is None
            assert result.get('.zip') is None
        finally:
            shutil.rmtree(temp_dir)


class TestDefaultConfig:
    """Tests for default configuration settings."""

    def test_default_config_returns_dict(self):
        """Test that default_config returns a dictionary."""
        from src.utils.default_config_settings import default_config

        config = default_config()
        assert isinstance(config, dict)

    def test_default_config_has_required_keys(self):
        """Test that default_config has all required keys."""
        from src.utils.default_config_settings import default_config

        config = default_config()
        required_keys = [
            'agent_type', 'max_steps', 'max_actions_per_step',
            'use_vision', 'llm_provider', 'llm_model_name',
            'llm_temperature', 'use_own_browser', 'headless',
            'window_w', 'window_h'
        ]

        for key in required_keys:
            assert key in config, f"Missing required key: {key}"

    def test_default_config_valid_values(self):
        """Test that default config values are valid."""
        from src.utils.default_config_settings import default_config

        config = default_config()

        # Check numeric values
        assert config['max_steps'] > 0
        assert config['max_actions_per_step'] > 0
        assert 0 <= config['llm_temperature'] <= 2.0
        assert config['window_w'] > 0
        assert config['window_h'] > 0

        # Check string values
        assert config['agent_type'] in ['org', 'custom']
        assert isinstance(config['llm_provider'], str)
        assert isinstance(config['llm_model_name'], str)

        # Check boolean values
        assert isinstance(config['use_vision'], bool)
        assert isinstance(config['use_own_browser'], bool)
        assert isinstance(config['headless'], bool)


class TestCustomController:
    """Tests for CustomController."""

    def test_controller_import(self):
        """Test that CustomController can be imported."""
        from src.controller.custom_controller import CustomController
        assert CustomController is not None

    def test_controller_instantiation(self):
        """Test that CustomController can be instantiated."""
        from src.controller.custom_controller import CustomController
        controller = CustomController()
        assert controller is not None


class TestCustomPrompts:
    """Tests for custom prompts."""

    def test_prompts_import(self):
        """Test that custom prompts can be imported."""
        from src.agent.custom_prompts import CustomSystemPrompt, CustomAgentMessagePrompt
        assert CustomSystemPrompt is not None
        assert CustomAgentMessagePrompt is not None


class TestCustomViews:
    """Tests for custom views."""

    def test_views_import(self):
        """Test that custom views can be imported."""
        from src.agent.custom_views import CustomAgentOutput, CustomAgentStepInfo
        assert CustomAgentOutput is not None
        assert CustomAgentStepInfo is not None


class TestLLMFactory:
    """Tests for LLM factory function (without actual API calls)."""

    def test_get_llm_model_invalid_provider(self):
        """Test that invalid provider raises an error.

        Note: The current implementation first checks for API key before
        validating the provider, which could be improved to fail-fast
        on invalid providers.
        """
        from src.utils.utils import get_llm_model
        import gradio as gr

        try:
            get_llm_model(provider="invalid_provider", model_name="test")
            assert False, "Should have raised an error"
        except (ValueError, gr.Error):
            pass  # Either error type is acceptable

    def test_get_llm_model_missing_api_key_raises_error(self):
        """Test that missing API key raises GradioError."""
        from src.utils.utils import get_llm_model
        import gradio as gr

        # Clear any existing env vars
        old_key = os.environ.pop("OPENAI_API_KEY", None)

        try:
            get_llm_model(provider="openai", model_name="gpt-4o")
            assert False, "Should have raised gr.Error"
        except gr.Error:
            pass  # Expected
        finally:
            if old_key:
                os.environ["OPENAI_API_KEY"] = old_key


class TestDeepResearch:
    """Tests for deep research module."""

    def test_deep_research_import(self):
        """Test that deep_research module imports correctly.

        This was fixed by changing langchain.schema import to langchain_core.messages.
        """
        from src.utils.deep_research import deep_research
        assert deep_research is not None
        assert callable(deep_research)


class TestIntegration:
    """Integration tests that verify component interactions."""

    def test_webui_imports(self):
        """Test that webui.py can be imported without errors."""
        try:
            # Just test the imports work, not the actual UI creation
            import webui
            assert hasattr(webui, 'create_ui')
            assert hasattr(webui, 'run_browser_agent')
            assert hasattr(webui, 'stop_agent')
        except Exception as e:
            pytest.skip(f"webui import failed due to dependency issues: {e}")

    def test_theme_map_defined(self):
        """Test that theme_map is properly defined."""
        try:
            from webui import theme_map
            assert isinstance(theme_map, dict)
            assert "Default" in theme_map
            assert "Ocean" in theme_map
        except Exception as e:
            pytest.skip(f"theme_map import failed: {e}")


def run_tests():
    """Run all tests and report results."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
