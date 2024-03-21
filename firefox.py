import os

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from browser import Browser


class Firefox(Browser):
    """
    This class is responsible for the browser Firefox.
    """

    def __init__(self):
        super().__init__(
            'firefox',
            adguard='firefox/adguard_adblocker.xpi',
            ublock='firefox/ublock_origin.xpi',
            touch_vpn='firefox/touch_vpn.xpi'
        )

    def setup_driver(self):
        """ Implementation of setup_driver abstract method. """
        # Create a Firefox profile
        profile = FirefoxProfile()

        # Set the language preference to English
        profile.set_preference('intl.accept_languages', 'en-US')

        self.options.binary_location = self.browser["path"]
        self.options.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.options.set_preference("dom.webdriver.enabled", False)
        self.options.set_preference('useAutomationExtension', False)
        # driver_path = GeckoDriverManager(version=self.browser["version"]).install()

        # assert os.path.exists(
        #     self.browser["path"]), "The path to the Firefox binary is incorrect."

        driver = webdriver.Firefox(service=FirefoxService(), options=self.options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.install_addon(self.adguard)
        driver.install_addon(self.ublock)
        driver.install_addon(self.touch_vpn)
        return driver

    # def get_touch_vpn_id(self):
        # try:
        # self.get('about:debugging#/runtime/this-firefox')
        # sleep(5)
        # touch_vpn_id = self.get_visible_element(By.XPATH,
        # "/html/body/div/div/main/article/section[2]/div/ul/li["
        # "3]/section/dl/div[2]/dd").text
        # return touch_vpn_id
        # except (NoSuchElementException, TimeoutException) as e:
        # print(f"An error occurred while getting the Touch VPN ID: {e}")
        # return None

    def setup_touch_vpn(self):
        pass
        # vpn_id = self.get_touch_vpn_id()
        # if vpn_id is None:
        # return

        # try:
        # sleep(4)
        # index_page = "moz-extension://" + vpn_id + "/panel/index.html"
        # sleep(2)
        # self.get(index_page)

        # continue_button = self.get_clickable_element(By.XPATH, "/html/body/div/div/section[2]/button[1]")

        # if continue_button:
        # continue_button.click()
        # sleep(2)

        # sleep(5)
        # self.get_clickable_element(By.ID, "ConnectionButton").click()
        # except (NoSuchElementException, TimeoutException) as e:
        # print(f"An error occurred while setting up Touch VPN: {e}")
