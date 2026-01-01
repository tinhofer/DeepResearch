# Browser Use Web UI

## Overview

This project is a web-based UI for the browser-use library, which enables AI agents to interact with and automate web browsers. It provides a Gradio-based interface that allows users to configure and run browser automation tasks using various Large Language Models (LLMs). The system supports multiple LLM providers (OpenAI, Anthropic, Google, DeepSeek, Ollama, etc.), custom browser sessions, and persistent browser contexts. Key features include deep research capabilities, custom agent prompts, and the ability to use existing browser profiles to avoid re-authentication.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Gradio UI**: The interface is built with Gradio (v5.10.0), providing a web-based dashboard for configuring and running browser automation tasks
- **Configuration Management**: Settings are persisted using pickle files with UUID-based naming, stored in `./tmp/webui_settings/`
- **Theme Support**: Uses Gradio's built-in themes (Citrus, Default, Glass, etc.)

### Agent System
- **Custom Agent Layer**: Extends the base `browser-use` Agent class with custom prompts, message handling, and state management
- **Agent State Management**: Singleton pattern (`AgentState` class) tracks agent status, stop requests, and maintains the last valid browser state
- **Custom Prompts**: Extended system and agent message prompts with structured JSON response format for better action sequencing
- **Output Structure**: Agent responses include current state evaluation, task progress, future plans, and action sequences

### Browser Automation
- **Playwright Integration**: Uses Playwright for browser automation with anti-detection measures
- **Custom Browser Context**: Extended browser context supporting custom configurations and persistent sessions
- **Chrome Instance Reuse**: Can connect to existing Chrome instances via CDP (Chrome DevTools Protocol) on port 9222
- **Recording Support**: Captures videos and traces of browser sessions

### Controller Layer
- **Custom Controller**: Extends base controller with additional actions like clipboard operations (copy/paste)
- **Action Registry**: Modular action registration system for browser interactions

### Deep Research Feature
- **Multi-iteration Research**: Performs web research across multiple search iterations
- **Report Generation**: Produces markdown reports from research findings
- **Configurable Query Limits**: Controls maximum queries per iteration

### LLM Integration
- **Multi-Provider Support**: Abstraction layer supporting OpenAI, Azure OpenAI, Anthropic, Google Gemini, DeepSeek, Mistral, and Ollama
- **Custom DeepSeek R1 Implementation**: Special handling for DeepSeek R1 models with custom ChatOpenAI extension
- **Environment-based Configuration**: API keys and endpoints read from environment variables

## External Dependencies

### Python Packages
- `browser-use==0.1.29`: Core browser automation library
- `gradio==5.10.0`: Web UI framework
- `langchain-*`: LLM integration (OpenAI, Anthropic, Google, Mistral, Ollama)
- `playwright`: Browser automation engine
- `pyperclip`: Clipboard operations
- `json-repair`: JSON parsing with error recovery
- `python-dotenv`: Environment variable management

### External Services
- **LLM Providers**: OpenAI, Azure OpenAI, Anthropic, Google AI, DeepSeek, Mistral (via API keys)
- **Ollama**: Local LLM inference (connects to local Ollama instance)

### Environment Variables
- `CHROME_PATH`: Path to Chrome executable for custom browser
- `CHROME_USER_DATA`: Chrome user data directory for session persistence
- `CHROME_PERSISTENT_SESSION`: Enable persistent browser sessions
- `*_API_KEY`: API keys for various LLM providers (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc.)
- `*_ENDPOINT`: Custom endpoints for LLM providers

### File Storage
- `./tmp/record_videos`: Browser session recordings
- `./tmp/traces`: Playwright traces
- `./tmp/agent_history`: Agent execution history
- `./tmp/deep_research`: Research reports and data
- `./tmp/webui_settings`: Saved UI configurations