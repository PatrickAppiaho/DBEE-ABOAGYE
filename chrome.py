import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

from browser import Browser


class Chrome(Browser):
    """
    This class is responsible for the browser Chrome.
    """

    def __init__(self):
        super().__init__(
            'chrome',
            adguard='chrome/AdGuard-AdBlocker.crx',
            ublock='chrome/uBlock-Origin.crx',
            touch_vpn='chrome/Touch-vpn.crx'
        )

    def setup_driver(self):
        """ Implementation of setup_driver abstract method. """
        self.chromium_browsers_config()
        driver_path = ChromeDriverManager().install()
        #
        assert os.path.exists(
            self.browser["path"]), "The path to the Chrome binary is incorrect."
        # assert os.path.exists(
        #     driver_path), "The path to the Chrome driver is incorrect."

        # driver = webdriver.Chrome(options=self.options)
        driver = webdriver.Chrome(service=ChromeService(driver_path), options=self.options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def setup_touch_vpn(self):
        index_page = "chrome-extension://" + "bihmplhobchoageeokmgbdihknkjbknd" + "/panel/index.html"
        self.get(index_page)

        sleep(5)
        self.get_clickable_element(By.ID, "ConnectionButton").click()
