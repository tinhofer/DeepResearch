"""Event handlers for the WebUI (agent execution, stop, deep research)."""

import asyncio
import glob
import logging
import os

import gradio as gr

from browser_use.agent.service import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import (
    BrowserContextConfig,
    BrowserContextWindowSize,
)

from src.agent.custom_agent import CustomAgent
from src.agent.custom_prompts import CustomSystemPrompt, CustomAgentMessagePrompt
from src.browser.custom_browser import CustomBrowser
from src.browser.custom_context import BrowserContextConfig as CustomBrowserContextConfig, CustomBrowserContext
from src.controller.custom_controller import CustomController
from src.utils import utils
from src.utils.utils import get_latest_files, capture_screenshot

from . import browser_state as bs

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Stop handlers
# ---------------------------------------------------------------------------

async def stop_agent():
    """Request the agent to stop and update UI with enhanced feedback."""
    try:
        bs.global_agent_state.request_stop()
        message = "Stop requested - the agent will halt at the next safe point"
        logger.info(message)
        return (
            message,
            gr.update(value="Stopping...", interactive=False),
            gr.update(interactive=False),
        )
    except Exception as e:
        error_msg = f"Error during stop: {e}"
        logger.error(error_msg)
        return (
            error_msg,
            gr.update(value="Stop", interactive=True),
            gr.update(interactive=True),
        )


async def stop_research_agent():
    """Request the research agent to stop."""
    try:
        bs.global_agent_state.request_stop()
        logger.info("Stop requested - the agent will halt at the next safe point")
        return (
            gr.update(value="Stopping...", interactive=False),
            gr.update(interactive=False),
        )
    except Exception as e:
        logger.error("Error during stop: %s", e)
        return (
            gr.update(value="Stop", interactive=True),
            gr.update(interactive=True),
        )


# ---------------------------------------------------------------------------
# Agent runners
# ---------------------------------------------------------------------------

async def run_org_agent(
    llm, use_own_browser, keep_browser_open, headless, disable_security,
    window_w, window_h, save_recording_path, save_agent_history_path,
    save_trace_path, task, max_steps, use_vision, max_actions_per_step,
    tool_calling_method,
):
    try:
        bs.global_agent_state.clear_stop()

        extra_chromium_args = [f"--window-size={window_w},{window_h}"]
        if use_own_browser:
            chrome_path = os.getenv("CHROME_PATH", None)
            if chrome_path == "":
                chrome_path = None
            chrome_user_data = os.getenv("CHROME_USER_DATA", None)
            if chrome_user_data:
                extra_chromium_args += [f"--user-data-dir={chrome_user_data}"]
        else:
            chrome_path = None

        if bs.global_browser is None:
            bs.global_browser = Browser(
                config=BrowserConfig(
                    headless=headless,
                    disable_security=disable_security,
                    chrome_instance_path=chrome_path,
                    extra_chromium_args=extra_chromium_args,
                )
            )

        if bs.global_browser_context is None:
            bs.global_browser_context = await bs.global_browser.new_context(
                config=BrowserContextConfig(
                    trace_path=save_trace_path if save_trace_path else None,
                    save_recording_path=save_recording_path if save_recording_path else None,
                    no_viewport=False,
                    browser_window_size=BrowserContextWindowSize(width=window_w, height=window_h),
                )
            )

        agent = Agent(
            task=task, llm=llm, use_vision=use_vision,
            browser=bs.global_browser, browser_context=bs.global_browser_context,
            max_actions_per_step=max_actions_per_step, tool_calling_method=tool_calling_method,
        )
        history = await agent.run(max_steps=max_steps)

        history_file = os.path.join(save_agent_history_path, f"{agent.agent_id}.json")
        agent.save_history(history_file)

        final_result = history.final_result()
        errors = history.errors()
        model_actions = history.model_actions()
        model_thoughts = history.model_thoughts()
        trace_file = get_latest_files(save_trace_path)

        return final_result, errors, model_actions, model_thoughts, trace_file.get('.zip'), history_file
    except Exception as e:
        import traceback
        traceback.print_exc()
        return '', str(e) + "\n" + traceback.format_exc(), '', '', None, None
    finally:
        if not keep_browser_open:
            if bs.global_browser_context:
                await bs.global_browser_context.close()
                bs.global_browser_context = None
            if bs.global_browser:
                await bs.global_browser.close()
                bs.global_browser = None


async def run_custom_agent(
    llm, use_own_browser, keep_browser_open, headless, disable_security,
    window_w, window_h, save_recording_path, save_agent_history_path,
    save_trace_path, task, add_infos, max_steps, use_vision,
    max_actions_per_step, tool_calling_method,
):
    try:
        bs.global_agent_state.clear_stop()

        extra_chromium_args = [f"--window-size={window_w},{window_h}"]
        if use_own_browser:
            chrome_path = os.getenv("CHROME_PATH", None)
            if chrome_path == "":
                chrome_path = None
            chrome_user_data = os.getenv("CHROME_USER_DATA", None)
            if chrome_user_data:
                extra_chromium_args += [f"--user-data-dir={chrome_user_data}"]
        else:
            chrome_path = None

        controller = CustomController()

        if bs.global_browser is None:
            bs.global_browser = CustomBrowser(
                config=BrowserConfig(
                    headless=headless,
                    disable_security=disable_security,
                    chrome_instance_path=chrome_path,
                    extra_chromium_args=extra_chromium_args,
                )
            )

        if bs.global_browser_context is None:
            bs.global_browser_context = await bs.global_browser.new_context(
                config=BrowserContextConfig(
                    trace_path=save_trace_path if save_trace_path else None,
                    save_recording_path=save_recording_path if save_recording_path else None,
                    no_viewport=False,
                    browser_window_size=BrowserContextWindowSize(width=window_w, height=window_h),
                )
            )

        agent = CustomAgent(
            task=task, add_infos=add_infos, use_vision=use_vision, llm=llm,
            browser=bs.global_browser, browser_context=bs.global_browser_context,
            controller=controller, system_prompt_class=CustomSystemPrompt,
            agent_prompt_class=CustomAgentMessagePrompt,
            max_actions_per_step=max_actions_per_step,
            agent_state=bs.global_agent_state, tool_calling_method=tool_calling_method,
        )
        history = await agent.run(max_steps=max_steps)

        history_file = os.path.join(save_agent_history_path, f"{agent.agent_id}.json")
        agent.save_history(history_file)

        final_result = history.final_result()
        errors = history.errors()
        model_actions = history.model_actions()
        model_thoughts = history.model_thoughts()
        trace_file = get_latest_files(save_trace_path)

        return final_result, errors, model_actions, model_thoughts, trace_file.get('.zip'), history_file
    except Exception as e:
        import traceback
        traceback.print_exc()
        return '', str(e) + "\n" + traceback.format_exc(), '', '', None, None
    finally:
        if not keep_browser_open:
            if bs.global_browser_context:
                await bs.global_browser_context.close()
                bs.global_browser_context = None
            if bs.global_browser:
                await bs.global_browser.close()
                bs.global_browser = None


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

async def run_browser_agent(
    agent_type, llm_provider, llm_model_name, llm_temperature, llm_base_url,
    llm_api_key, use_own_browser, keep_browser_open, headless, disable_security,
    window_w, window_h, save_recording_path, save_agent_history_path,
    save_trace_path, enable_recording, task, add_infos, max_steps, use_vision,
    max_actions_per_step, tool_calling_method,
):
    bs.global_agent_state.clear_stop()

    try:
        if not enable_recording:
            save_recording_path = None
        if save_recording_path:
            os.makedirs(save_recording_path, exist_ok=True)

        existing_videos = set()
        if save_recording_path:
            existing_videos = set(
                glob.glob(os.path.join(save_recording_path, "*.[mM][pP]4"))
                + glob.glob(os.path.join(save_recording_path, "*.[wW][eE][bB][mM]"))
            )

        llm = utils.get_llm_model(
            provider=llm_provider, model_name=llm_model_name,
            temperature=llm_temperature, base_url=llm_base_url, api_key=llm_api_key,
        )

        if agent_type == "org":
            final_result, errors, model_actions, model_thoughts, trace_file, history_file = await run_org_agent(
                llm=llm, use_own_browser=use_own_browser, keep_browser_open=keep_browser_open,
                headless=headless, disable_security=disable_security,
                window_w=window_w, window_h=window_h,
                save_recording_path=save_recording_path,
                save_agent_history_path=save_agent_history_path,
                save_trace_path=save_trace_path, task=task, max_steps=max_steps,
                use_vision=use_vision, max_actions_per_step=max_actions_per_step,
                tool_calling_method=tool_calling_method,
            )
        elif agent_type == "custom":
            final_result, errors, model_actions, model_thoughts, trace_file, history_file = await run_custom_agent(
                llm=llm, use_own_browser=use_own_browser, keep_browser_open=keep_browser_open,
                headless=headless, disable_security=disable_security,
                window_w=window_w, window_h=window_h,
                save_recording_path=save_recording_path,
                save_agent_history_path=save_agent_history_path,
                save_trace_path=save_trace_path, task=task, add_infos=add_infos,
                max_steps=max_steps, use_vision=use_vision,
                max_actions_per_step=max_actions_per_step,
                tool_calling_method=tool_calling_method,
            )
        else:
            raise ValueError(f"Invalid agent type: {agent_type}")

        latest_video = None
        if save_recording_path:
            new_videos = set(
                glob.glob(os.path.join(save_recording_path, "*.[mM][pP]4"))
                + glob.glob(os.path.join(save_recording_path, "*.[wW][eE][bB][mM]"))
            )
            if new_videos - existing_videos:
                latest_video = list(new_videos - existing_videos)[0]

        return (
            final_result, errors, model_actions, model_thoughts, latest_video,
            trace_file, history_file,
            gr.update(value="Stop", interactive=True),
            gr.update(interactive=True),
        )

    except gr.Error:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        errors = str(e) + "\n" + traceback.format_exc()
        return (
            '', errors, '', '', None, None, None,
            gr.update(value="Stop", interactive=True),
            gr.update(interactive=True),
        )


async def run_with_stream(
    agent_type, llm_provider, llm_model_name, llm_temperature, llm_base_url,
    llm_api_key, use_own_browser, keep_browser_open, headless, disable_security,
    window_w, window_h, save_recording_path, save_agent_history_path,
    save_trace_path, enable_recording, task, add_infos, max_steps, use_vision,
    max_actions_per_step, tool_calling_method,
):
    stream_vw = 80
    stream_vh = int(80 * window_h // window_w)

    if not headless:
        result = await run_browser_agent(
            agent_type=agent_type, llm_provider=llm_provider,
            llm_model_name=llm_model_name, llm_temperature=llm_temperature,
            llm_base_url=llm_base_url, llm_api_key=llm_api_key,
            use_own_browser=use_own_browser, keep_browser_open=keep_browser_open,
            headless=headless, disable_security=disable_security,
            window_w=window_w, window_h=window_h,
            save_recording_path=save_recording_path,
            save_agent_history_path=save_agent_history_path,
            save_trace_path=save_trace_path, enable_recording=enable_recording,
            task=task, add_infos=add_infos, max_steps=max_steps,
            use_vision=use_vision, max_actions_per_step=max_actions_per_step,
            tool_calling_method=tool_calling_method,
        )
        html_content = f"<h1 style='width:{stream_vw}vw; height:{stream_vh}vh'>Using browser...</h1>"
        yield [html_content] + list(result)
    else:
        try:
            bs.global_agent_state.clear_stop()
            agent_task = asyncio.create_task(
                run_browser_agent(
                    agent_type=agent_type, llm_provider=llm_provider,
                    llm_model_name=llm_model_name, llm_temperature=llm_temperature,
                    llm_base_url=llm_base_url, llm_api_key=llm_api_key,
                    use_own_browser=use_own_browser, keep_browser_open=keep_browser_open,
                    headless=headless, disable_security=disable_security,
                    window_w=window_w, window_h=window_h,
                    save_recording_path=save_recording_path,
                    save_agent_history_path=save_agent_history_path,
                    save_trace_path=save_trace_path, enable_recording=enable_recording,
                    task=task, add_infos=add_infos, max_steps=max_steps,
                    use_vision=use_vision, max_actions_per_step=max_actions_per_step,
                    tool_calling_method=tool_calling_method,
                )
            )

            html_content = f"<h1 style='width:{stream_vw}vw; height:{stream_vh}vh'>Using browser...</h1>"
            final_result = errors = model_actions = model_thoughts = ""
            latest_videos = trace = history_file = None

            while not agent_task.done():
                try:
                    encoded_screenshot = await capture_screenshot(bs.global_browser_context)
                    if encoded_screenshot is not None:
                        html_content = f'<img src="data:image/jpeg;base64,{encoded_screenshot}" style="width:{stream_vw}vw; height:{stream_vh}vh ; border:1px solid #ccc;">'
                    else:
                        html_content = f"<h1 style='width:{stream_vw}vw; height:{stream_vh}vh'>Waiting for browser session...</h1>"
                except Exception:
                    html_content = f"<h1 style='width:{stream_vw}vw; height:{stream_vh}vh'>Waiting for browser session...</h1>"

                if bs.global_agent_state and bs.global_agent_state.is_stop_requested():
                    yield [
                        html_content, final_result, errors, model_actions,
                        model_thoughts, latest_videos, trace, history_file,
                        gr.update(value="Stopping...", interactive=False),
                        gr.update(interactive=False),
                    ]
                    break
                else:
                    yield [
                        html_content, final_result, errors, model_actions,
                        model_thoughts, latest_videos, trace, history_file,
                        gr.update(value="Stop", interactive=True),
                        gr.update(interactive=True),
                    ]
                await asyncio.sleep(0.05)

            try:
                result = await agent_task
                final_result, errors, model_actions, model_thoughts, latest_videos, trace, history_file, stop_button, run_button = result
            except gr.Error:
                final_result = ""
                errors = "Gradio Error"
                model_actions = ""
                model_thoughts = ""
                latest_videos = trace = history_file = None
                stop_button = gr.update(value="Stop", interactive=True)
                run_button = gr.update(interactive=True)
            except Exception as e:
                errors = f"Agent error: {e}"

            yield [
                html_content, final_result, errors, model_actions, model_thoughts,
                latest_videos, trace, history_file, stop_button, run_button,
            ]

        except Exception as e:
            import traceback
            yield [
                f"<h1 style='width:{stream_vw}vw; height:{stream_vh}vh'>Waiting for browser session...</h1>",
                "", f"Error: {e}\n{traceback.format_exc()}", "", "",
                None, None, None,
                gr.update(value="Stop", interactive=True),
                gr.update(interactive=True),
            ]


# ---------------------------------------------------------------------------
# Deep Research
# ---------------------------------------------------------------------------

async def run_deep_search(
    research_task, max_search_iteration_input, max_query_per_iter_input,
    llm_provider, llm_model_name, llm_temperature, llm_base_url, llm_api_key,
    use_vision, use_own_browser, headless,
):
    from src.utils.deep_research import deep_research

    bs.global_agent_state.clear_stop()

    llm = utils.get_llm_model(
        provider=llm_provider, model_name=llm_model_name,
        temperature=llm_temperature, base_url=llm_base_url, api_key=llm_api_key,
    )
    markdown_content, file_path = await deep_research(
        research_task, llm, bs.global_agent_state,
        max_search_iterations=max_search_iteration_input,
        max_query_num=max_query_per_iter_input,
        use_vision=use_vision, headless=headless,
        use_own_browser=use_own_browser,
    )

    return (
        markdown_content, file_path,
        gr.update(value="Stop", interactive=True),
        gr.update(interactive=True),
    )
