import os
from abc import ABC
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from browser import Browser


class Edge(Browser, ABC):
    """
    This class is responsible for the browser Microsoft Edge.
    """

    def __init__(self):
        super().__init__(
            'msedge',
            adguard='chrome/AdGuard-AdBlocker.crx',
            ublock='chrome/uBlock-Origin.crx',
            touch_vpn='chrome/Touch-vpn.crx'
        )

    def setup_driver(self):
        """ Implementation of setup_driver abstract method. """
        self.chromium_browsers_config()

        # driver_path = EdgeChromiumDriverManager().install()
        #
        # assert os.path.exists(
        #     self.browser["path"]), "The path to the Chrome binary is incorrect."
        # assert os.path.exists(
        #     driver_path), "The path to the Chrome driver is incorrect."

        # driver = webdriver.Edge(service=EdgeService(
        #     driver_path), options=self.options)
        driver = webdriver.Edge(options=self.options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def setup_touch_vpn(self):
        index_page = "chrome-extension://" + "bihmplhobchoageeokmgbdihknkjbknd" + "/panel/index.html"
        sleep(5)
        self.get(index_page)

        sleep(10)
        self.get_clickable_element(By.ID, "ConnectionButton").click()
