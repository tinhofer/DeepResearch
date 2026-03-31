import pyperclip
from typing import Optional, Type
from pydantic import BaseModel
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller, DoneAction
from main_content_extractor import MainContentExtractor
from browser_use.controller.views import (
    ClickElementAction,
    DoneAction,
    ExtractPageContentAction,
    GoToUrlAction,
    InputTextAction,
    OpenTabAction,
    ScrollAction,
    SearchGoogleAction,
    SendKeysAction,
    SwitchTabAction,
)
import logging

from src.utils.exceptions import ContentExtractionError

logger = logging.getLogger(__name__)


class CustomController(Controller):
    def __init__(self, exclude_actions: list[str] = [],
                 output_model: Optional[Type[BaseModel]] = None
                 ):
        super().__init__(exclude_actions=exclude_actions, output_model=output_model)
        self._register_custom_actions()

    def _register_custom_actions(self):
        """Register all custom browser actions"""

        @self.registry.action("Copy text to clipboard")
        def copy_to_clipboard(text: str):
            pyperclip.copy(text)
            return ActionResult(extracted_content=text)

        @self.registry.action("Paste text from clipboard", requires_browser=True)
        async def paste_from_clipboard(browser: BrowserContext):
            text = pyperclip.paste()
            # send text to browser
            page = await browser.get_current_page()
            await page.keyboard.type(text)

            return ActionResult(extracted_content=text)

        @self.registry.action(
            'Extract page content to get the pure text or markdown with links if include_links is set to true',
            param_model=ExtractPageContentAction,
            requires_browser=True,
        )
        async def extract_content(params: ExtractPageContentAction, browser: BrowserContext):
            page = await browser.get_current_page()
            url = page.url
            jina_url = f"https://r.jina.ai/{url}"
            try:
                response = await page.goto(jina_url, timeout=30000)
                if response and response.status >= 400:
                    raise ContentExtractionError(
                        f"Jina reader returned HTTP {response.status} for {url}"
                    )
                output_format = 'markdown' if params.include_links else 'text'
                content = MainContentExtractor.extract(  # type: ignore
                    html=await page.content(),
                    output_format=output_format,
                )
            except ContentExtractionError:
                raise
            except Exception as e:
                logger.warning("Jina reader failed for %s, falling back to direct extraction: %s", url, e)
                await page.goto(url)
                output_format = 'markdown' if params.include_links else 'text'
                content = MainContentExtractor.extract(  # type: ignore
                    html=await page.content(),
                    output_format=output_format,
                )
            finally:
                # Always go back to original url
                try:
                    if page.url != url:
                        await page.go_back()
                except Exception:
                    pass
            msg = f'Extracted page content:\n {content}\n'
            logger.info(msg)
            return ActionResult(extracted_content=msg)
