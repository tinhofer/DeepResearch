"""Global browser state management for the WebUI.

Centralises the mutable globals that were previously scattered across webui.py
so the rest of the codebase can import and mutate them from one place.
"""

from src.utils.agent_state import AgentState

# Global variables for persistence
global_browser = None
global_browser_context = None

# Create the global agent state instance
global_agent_state = AgentState()


async def close_global_browser():
    """Tear down any open global browser/context."""
    global global_browser, global_browser_context

    if global_browser_context:
        await global_browser_context.close()
        global_browser_context = None

    if global_browser:
        await global_browser.close()
        global_browser = None
