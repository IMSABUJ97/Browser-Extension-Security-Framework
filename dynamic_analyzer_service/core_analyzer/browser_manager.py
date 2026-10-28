import asyncio
import os
from playwright.async_api import async_playwright
from interceptors.network_monitor import log_network_request
from interceptors.dom_observer import get_injection_script

class BrowserManager:
    def __init__(self, extension_path: str, target_url: str):
        self.extension_path = extension_path
        self.target_url = target_url
        self.logs = {"network": [], "dom": []}

    async def start_analysis(self, duration: int = 15):
        
        abs_extension_path = os.path.abspath(self.extension_path)
        
        
        profile_dir = os.path.join(os.getcwd(), "analyzer_profile")

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=[
                    f"--disable-extensions-except={abs_extension_path}",
                    f"--load-extension={abs_extension_path}",
                    "--mute-audio"
                ]
            )
            page = await context.new_page()

            page.on("request", lambda req: log_network_request(req, self.logs["network"]))
            page.on("console", lambda msg: self._log_console(msg))

            await page.add_init_script(get_injection_script())

            await page.goto(self.target_url)
            
            await asyncio.sleep(duration)
            
            await context.close()
            return self.logs

    def _log_console(self, msg):
        if "[HOOK]" in msg.text:
            self.logs["dom"].append(msg.text)