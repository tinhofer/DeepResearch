# CLAUDE.md - Browser Use WebUI

## Project Overview

Browser Use WebUI is a Python-based Gradio web application that enables AI agents to automate web browser interactions using various LLM providers.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the application
python webui.py --ip 127.0.0.1 --port 7788

# Run tests
python -m pytest tests/test_unit.py -v
```

## Project Structure

```
├── webui.py                    # Main Gradio application
├── src/
│   ├── agent/                  # AI agent customization
│   │   ├── custom_agent.py     # Extended Agent class
│   │   ├── custom_prompts.py   # System and message prompts
│   │   ├── custom_views.py     # Output structures
│   │   └── custom_message_manager.py
│   ├── browser/                # Browser automation
│   │   ├── custom_browser.py   # Extended Browser with CDP
│   │   └── custom_context.py   # Browser context config
│   ├── controller/
│   │   └── custom_controller.py # Action controller
│   └── utils/
│       ├── utils.py            # LLM factory, utilities
│       ├── llm.py              # Custom LLM implementations
│       ├── agent_state.py      # Singleton state management
│       ├── deep_research.py    # Multi-iteration research
│       └── default_config_settings.py
└── tests/
    ├── test_unit.py            # Unit tests (20 tests)
    ├── test_browser_use.py     # Browser integration tests
    ├── test_deep_research.py   # Deep research tests
    └── test_llm_api.py         # LLM provider tests
```

## Key Dependencies

- `browser-use==0.1.29` - Core browser automation
- `gradio>=5.10.0` - Web UI framework
- `playwright` - Browser control
- `langchain-*` - LLM integrations

## LLM Providers

Supported providers in `src/utils/utils.py`:
- OpenAI (`openai`)
- Anthropic (`anthropic`)
- Google Gemini (`google`)
- Azure OpenAI (`azure_openai`)
- DeepSeek (`deepseek`)
- Ollama (`ollama`)
- Mistral (`mistral`)

## Environment Variables

```bash
# LLM API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
DEEPSEEK_API_KEY=
AZURE_OPENAI_API_KEY=
MISTRAL_API_KEY=

# Browser Settings
CHROME_PATH=           # Custom Chrome executable
CHROME_USER_DATA=      # Browser profile directory

# Endpoints
OPENAI_ENDPOINT=https://api.openai.com/v1
DEEPSEEK_ENDPOINT=https://api.deepseek.com
AZURE_OPENAI_ENDPOINT=
```

## Key Components

### AgentState (`src/utils/agent_state.py`)
Singleton class managing agent state with stop/resume functionality.

### CustomAgent (`src/agent/custom_agent.py`)
Extended browser-use Agent with:
- DeepSeek R1 reasoning support
- Custom message management
- Step info tracking
- Stop request handling

### LLM Factory (`src/utils/utils.py:get_llm_model`)
Creates LLM instances based on provider string. Validates API keys from environment or UI input.

## Testing

```bash
# Unit tests (no external deps)
python -m pytest tests/test_unit.py -v

# All tests (requires API keys)
python -m pytest tests/ -v
```

## Known Issues

1. **Dependency Version**: `browser-use==0.1.29` is pinned due to breaking API changes in 0.2+
   - Upgrading requires refactoring telemetry and context APIs
   - See requirements.txt for version constraints
2. **Debug Code**: Some `pdb` imports remain in test files

## Common Tasks

### Adding a New LLM Provider
1. Add to `model_names` dict in `src/utils/utils.py`
2. Add provider handling in `get_llm_model()` function
3. Add to `PROVIDER_DISPLAY_NAMES` if needed

### Running with Custom Browser
Set environment variables:
```bash
export CHROME_PATH=/path/to/chrome
export CHROME_USER_DATA=/path/to/profile
```
Then enable "Use Own Browser" in the UI.

### Deep Research Feature
Located in `src/utils/deep_research.py`. Performs multi-iteration web research with automatic query generation and report synthesis.
