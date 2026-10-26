import json
import os
import uuid

import gradio as gr
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration with validation via Pydantic."""

    agent_type: str = "custom"
    max_steps: int = 100
    max_actions_per_step: int = 10
    use_vision: bool = True
    tool_calling_method: str = "auto"
    llm_provider: str = "openai"
    llm_model_name: str = "gpt-4o"
    llm_temperature: float = 1.0
    llm_base_url: str = ""
    llm_api_key: str = ""
    use_own_browser: bool = Field(
        default_factory=lambda: os.getenv("CHROME_PERSISTENT_SESSION", "true").lower() == "true"
    )
    keep_browser_open: bool = True
    headless: bool = False
    disable_security: bool = True
    enable_recording: bool = True
    window_w: int = 1280
    window_h: int = 1100
    save_recording_path: str = "./tmp/record_videos"
    save_trace_path: str = "./tmp/traces"
    save_agent_history_path: str = "./tmp/agent_history"
    task: str = "go to google.com and type 'OpenAI' click search and give me the first url"


def default_config() -> dict:
    """Return the default configuration as a dict."""
    return AppConfig().model_dump()


def load_config_from_file(config_file: str) -> dict | str:
    """Load settings from a JSON file. Falls back to legacy pickle files."""
    try:
        if config_file.endswith(".json"):
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validate through Pydantic
            return AppConfig(**data).model_dump()
        else:
            # Legacy pickle support for existing configs
            import pickle
            with open(config_file, "rb") as f:
                settings = pickle.load(f)
            return settings
    except Exception as e:
        return f"Error loading configuration: {e}"


def save_config_to_file(settings: dict, save_dir: str = "./tmp/webui_settings") -> str:
    """Save the current settings to a JSON file."""
    os.makedirs(save_dir, exist_ok=True)
    # Validate through Pydantic before saving
    validated = AppConfig(**settings)
    config_file = os.path.join(save_dir, f"{uuid.uuid4()}.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(validated.model_dump(), f, indent=2)
    return f"Configuration saved to {config_file}"


def save_current_config(*args):
    current_config = {
        "agent_type": args[0],
        "max_steps": args[1],
        "max_actions_per_step": args[2],
        "use_vision": args[3],
        "tool_calling_method": args[4],
        "llm_provider": args[5],
        "llm_model_name": args[6],
        "llm_temperature": args[7],
        "llm_base_url": args[8],
        "llm_api_key": args[9],
        "use_own_browser": args[10],
        "keep_browser_open": args[11],
        "headless": args[12],
        "disable_security": args[13],
        "enable_recording": args[14],
        "window_w": args[15],
        "window_h": args[16],
        "save_recording_path": args[17],
        "save_trace_path": args[18],
        "save_agent_history_path": args[19],
        "task": args[20],
    }
    return save_config_to_file(current_config)


def update_ui_from_config(config_file):
    if config_file is not None:
        loaded_config = load_config_from_file(config_file.name)
        if isinstance(loaded_config, dict):
            return (
                gr.update(value=loaded_config.get("agent_type", "custom")),
                gr.update(value=loaded_config.get("max_steps", 100)),
                gr.update(value=loaded_config.get("max_actions_per_step", 10)),
                gr.update(value=loaded_config.get("use_vision", True)),
                gr.update(value=loaded_config.get("tool_calling_method", True)),
                gr.update(value=loaded_config.get("llm_provider", "openai")),
                gr.update(value=loaded_config.get("llm_model_name", "gpt-4o")),
                gr.update(value=loaded_config.get("llm_temperature", 1.0)),
                gr.update(value=loaded_config.get("llm_base_url", "")),
                gr.update(value=loaded_config.get("llm_api_key", "")),
                gr.update(value=loaded_config.get("use_own_browser", False)),
                gr.update(value=loaded_config.get("keep_browser_open", False)),
                gr.update(value=loaded_config.get("headless", False)),
                gr.update(value=loaded_config.get("disable_security", True)),
                gr.update(value=loaded_config.get("enable_recording", True)),
                gr.update(value=loaded_config.get("window_w", 1280)),
                gr.update(value=loaded_config.get("window_h", 1100)),
                gr.update(value=loaded_config.get("save_recording_path", "./tmp/record_videos")),
                gr.update(value=loaded_config.get("save_trace_path", "./tmp/traces")),
                gr.update(value=loaded_config.get("save_agent_history_path", "./tmp/agent_history")),
                gr.update(value=loaded_config.get("task", "")),
                "Configuration loaded successfully."
            )
        else:
            return (
                gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
                gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
                gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
                gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
                gr.update(), "Error: Invalid configuration file."
            )
    return (
        gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        gr.update(), gr.update(), gr.update(), gr.update(), gr.update(),
        gr.update(), "No file selected."
    )
