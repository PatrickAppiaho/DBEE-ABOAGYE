import abc
import os
from random import choice
from time import sleep

import browsers
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common import SEARCH_LIMIT, YOUTUBE_VIDEO_SHAREABLE_LINKS
from dictionary import VideoInfo
from enums import SearchEnum
from exceptions import SeleniumException as SE


def search_inner_elements(element):
    """ This function returns the inner elements of the search results. """
    inner_contents = element.find_element(By.ID, "contents")
    inner_elements = inner_contents.find_elements(
        By.TAG_NAME, 'ytd-video-renderer')
    return inner_elements


def home_inner_elements(element):
    """ This function returns the inner elements of the home page. """
    inner_contents = element.find_element(By.ID, "contents")
    inner_elements = inner_contents.find_elements(
        By.TAG_NAME, 'ytd-rich-item-renderer')
    return inner_elements


def get_channel_video_info(element) -> VideoInfo:
    """
    This function returns the channel video info.

    Args:
        - element (WebElement): The element to get the video info from.

    Returns:
        - dict: The video info.
    """
    thumbnail = element.find_element(By.CSS_SELECTOR, "#thumbnail")
    title = element.find_element(By.CSS_SELECTOR, "#meta > h3 > a")
    # channel = element.find_element(By.CSS_SELECTOR, "//*[@id="meta"]/h3").text

    return {
        'thumbnail': thumbnail,
        "title": title.text,
        "channel": '',
    }


class Browser(metaclass=abc.ABCMeta):
    """
    This class is the base class for the browser drivers.
    """

    def __init__(self, browser_type: str, adguard: str = None, ublock: str = None, touch_vpn: str = False):
        self.adguard = os.path.join(
            os.getcwd(), f'extensions/{adguard}')
        self.ublock = os.path.join(
            os.getcwd(), f'extensions/{ublock}')
        self.touch_vpn = os.path.join(
            os.getcwd(), f'extensions/{touch_vpn}')
        self.browser_type = browser_type
        self.browser = browsers.get(browser_type)
        self.options = self.setup_options()
        self.driver = self.setup_driver()

        self.setup_touch_vpn()

        self.video_found = False
        self.limit = 0
        self.dummy_list = []

    def setup_options(self):
        """
        This function is responsible for opening the browser.
        """
        options_mapping = {
            'chrome': webdriver.ChromeOptions,
            'firefox': webdriver.FirefoxOptions,
            'msedge': webdriver.EdgeOptions,
            'safari': webdriver.SafariOptions,
        }

        if self.browser_type in options_mapping:
            return options_mapping[self.browser_type]()
        else:
            print(f"Unsupported browser type: {self.browser_type}")
            return None

    @abc.abstractmethod
    def setup_driver(self):
        """
        Sets up the Browser driver with the correct path and options.

        Asserts:
            - The path to the Browser binary is correct.
            - The path to the Browser driver is correct.
        """

    def chromium_browsers_config(self):
        """
        This function sets up the configuration for the Chrome browsers.
        """
        self.options.binary_location = self.browser["path"]
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_extension(self.adguard)
        self.options.add_extension(self.ublock)
        self.options.add_extension(self.touch_vpn)

    @abc.abstractmethod
    @SE.handle_exceptions
    def setup_touch_vpn(self):
        """

        """

    def close_other_tabs(self):
        """ This function closes all other tabs except the current tab """
        original_window = self.driver.current_window_handle
        for window in self.driver.window_handles:
            if window != original_window:
                self.driver.switch_to.window(window)
                sleep(1.5)
                self.driver.close()
        self.driver.switch_to.window(original_window)

    def new_tab(self, url=None):
        """ This function opens a new tab """
        self.driver.execute_script(f"window.open('{url}')")
        sleep(1.5)
        # self.close_other_tabs()

    def maximize_window(self):
        """ This function maximizes the window """
        self.driver.maximize_window()

    def get(self, url):
        """
        Navigates to the specified URL.

        Args:
            - url (str): The URL to navigate to.
        """
        self.driver.get(url)

    def search(self, query: str):
        """ This function searches for the specified query. """
        # Check for cookie overlay immediately after page load
        if self.browser_type == 'chrome' or self.browser_type == 'msedge':
            try:
                cookie = self.get_clickable_element(
                    By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button')
                if cookie:
                    self.click_element(cookie)
                    sleep(2)  # Reduced sleep time
            except TimeoutException:
                pass
        # Wait for search bar to be clickable
        search_bar = self.get_clickable_element(
            By.XPATH, "//input[@id='search']")

        for key in query:
            search_bar.send_keys(key)
            sleep(0.05)
        sleep(0.5)  # Reduced sleep time
        search_bar.send_keys(Keys.ENTER)

    def not_found_reset(self):
        """ Resets the video_found and dummy_list variables if the video is not found.  """
        if not self.video_found and self.limit >= 5:
            self.limit = 0
            self.dummy_list = []
            print("Video not found")

    def after_found_reset(self):
        """ Resets the video_found and dummy_list variables after the video is found. """
        if self.video_found:
            self.video_found = False
            self.dummy_list = []
            self.limit = 0

    def search_outer_elements(self):
        """ This function returns the outer elements of the search results. """
        ytd_search = self.get_visible_element(
            By.XPATH, '//*[@id="container"]/ytd-two-column-search-results-renderer')
        contents = ytd_search.find_element(By.ID, "contents")
        elements = contents.find_elements(
            By.TAG_NAME, 'ytd-item-section-renderer')
        return elements

    def related_outer_elements(self):
        """ This function returns the outer elements of the related videos. """
        related = self.get_visible_element(By.ID, 'related')
        result_renderer = related.find_element(
            By.TAG_NAME, 'ytd-watch-next-secondary-results-renderer')
        items = result_renderer.find_element(By.ID, 'items')
        elements = items.find_elements(
            By.TAG_NAME, 'ytd-compact-video-renderer')
        return elements

    def home_outer_elements(self):
        """ This function returns the outer elements of the home page. """
        ytd_browse = self.get_visible_element(
            By.CSS_SELECTOR, 'ytd-browse > ytd-two-column-browse-results-renderer > div#primary')
        contents = ytd_browse.find_element(By.ID, "contents")
        elements = contents.find_elements(
            By.TAG_NAME, 'ytd-rich-grid-row')
        return elements

    def treat_video(self, inner_elements, video_title: str, channel: str, search_type: SearchEnum = SearchEnum.SEARCH):
        """
        This function treats the video from the search results.
        """
        for inner_element in inner_elements:
            video_info = self.search_video_info(inner_element, search_type)
            video_title = video_title.lower().strip()
            title = video_info["title"].lower().strip()
            channel = channel.lower().strip()
            if video_title in title and channel in video_info["channel"].lower().strip():
                self.video_found = True
                sleep(0.5)
                self.click_element(video_info["thumbnail"])
                print(f'Thumbnail clicked for ==>  {title}')
                sleep(5)
                break

    @SE.handle_exceptions
    def play_searched_video(self, channel: str, search_type: SearchEnum = SearchEnum.SEARCH, video_title: str = " ", ):
        """
        This function selects the video from the search results or related videos or home page.

        Args:
            - video_title (str): The title of the video to select.
            - channel (str): The channel of the video to select.
        """
        search_functions = {
            SearchEnum.SEARCH: self.search_outer_elements,
            SearchEnum.RELATED: self.related_outer_elements,
            SearchEnum.HOME: self.home_outer_elements
        }
        inner_functions = {
            SearchEnum.SEARCH: search_inner_elements,
            SearchEnum.HOME: home_inner_elements
        }
        while not self.video_found and self.limit < SEARCH_LIMIT:
            outer_elements = search_functions[search_type]()
            merged_list = [i for i in self.dummy_list +
                           outer_elements if i not in self.dummy_list or i not in outer_elements]
            self.dummy_list = outer_elements
            if search_type in (SearchEnum.SEARCH, SearchEnum.HOME):
                inner_function = inner_functions[search_type]
                for element in merged_list:
                    inner_elements = inner_function(element)
                    print(f'Treating video with ==>  {self.browser_type}')
                    self.treat_video(inner_elements, video_title, channel, search_type)
                    if not self.video_found and self.limit < SEARCH_LIMIT:
                        self.scroll_to_bottom()
                        sleep(5)
                    if self.video_found:
                        break
            elif search_type == SearchEnum.RELATED:
                self.treat_video(merged_list, video_title,
                                 channel, search_type)
                if not self.video_found and self.limit < SEARCH_LIMIT:
                    self.scroll_to_bottom()
                    sleep(5)

            if self.video_found:
                break

            self.limit += 1

        if not self.video_found and self.limit >= SEARCH_LIMIT:
            self.get(choice(YOUTUBE_VIDEO_SHAREABLE_LINKS))

        self.not_found_reset()
        self.after_found_reset()

    def go_to_channel(self, channel: str):
        """
        This function navigates to the channel page.

        Args:
            - channel (str): The channel to navigate to.
        """
        self.driver.get(f"https://www.youtube.com/{channel}/videos")

    def get_channel_videos(self, channel: str):
        """
        This function returns the channel videos.

        Args:
            - channel (str): The channel to get the videos from.

        Returns:
            - list: The channel videos.
        """
        self.go_to_channel(channel)
        sleep(5)
        wrapper = self.get_visible_element(
            By.CSS_SELECTOR, "#primary > ytd-rich-grid-renderer > #contents")

        contents = wrapper.find_elements(By.TAG_NAME, "ytd-rich-grid-row")

        for content in contents:
            videos = content.find_elements(
                By.TAG_NAME, "ytd-rich-item-renderer")

            for video in videos:
                yield video

    def treat_channel_video(self, channel_videos, video_title: str, channel: str):
        """
        This function treats the channel video.
        """
        for channel_video in channel_videos:
            video_info = get_channel_video_info(channel_video)
            video_title = video_title.lower().strip()
            title = video_info["title"].lower().strip()
            channel = channel.lower().strip()
            if video_title in title and channel in video_info["channel"].lower().strip():
                self.video_found = True
                sleep(0.5)
                self.click_element(video_info["thumbnail"])
                print('playing Video: ', title)
                break

    def searched_channel_video(self, video_title: str, channel: str):
        """
        This function selects the channel video.

        Args:
            - video_title (str): The title of the video to select.
            - channel (str): The channel of the video to select.
        """
        channel_videos = self.get_channel_videos(channel)
        self.treat_channel_video(
            channel_videos, video_title, channel)
        # self.not_found_reset()
        # self.after_found_reset()

    def get_random_channel_video(self, channel: str):
        """
        This function selects a random channel video.
        """
        channel_videos = self.get_channel_videos(channel)
        self.treat_channel_video(channel_videos, '', '')
        self.not_found_reset()
        self.after_found_reset()

    @SE.handle_exceptions
    def search_video_info(self, element, search_type: SearchEnum = SearchEnum.SEARCH) -> VideoInfo:
        """
        This function returns the video info.

        Args:
            - element (WebElement): The element to get the video info from.

        Returns:
            - VideoInfo: The video info.
        """
        self.scroll_to_element(
            element, -200 if search_type == SearchEnum.HOME else -50)
        sleep(0.25)

        title = None  # Default value
        channel = None  # Default value
        try:
            thumbnail = element.find_element(
                By.CSS_SELECTOR if search_type in (SearchEnum.SEARCH, SearchEnum.RELATED) else By.XPATH,
                "#dismissible > ytd-thumbnail > a#thumbnail" if search_type in (
                    SearchEnum.SEARCH, SearchEnum.RELATED) else '//a[@id="thumbnail"]')

            text_wrapper = element.find_element(By.CSS_SELECTOR if search_type in (
                SearchEnum.SEARCH, SearchEnum.RELATED) else By.XPATH, "#dismissible > div" if search_type in (
                SearchEnum.SEARCH, SearchEnum.RELATED) else '//div[@id="details"]')
        except TimeoutException:
            raise SE("Timeout while trying to find thumbnail or text wrapper.")

        try:
            if search_type == SearchEnum.SEARCH:
                title = text_wrapper.find_element(By.CSS_SELECTOR, "#title-wrapper > h3 > a#video-title").get_attribute(
                    "title")
                channel = text_wrapper.find_element(By.CSS_SELECTOR,
                                                    "#channel-info > #channel-name > #container > div#text-container > "
                                                    "yt-formatted-string#text > a").text
            elif search_type == SearchEnum.RELATED:
                title = text_wrapper.find_element(By.CSS_SELECTOR,
                                                  "div.metadata.style-scope.ytd-compact-video-renderer > a > h3 > "
                                                  "#video-title").get_attribute(
                    "title")
                channel = text_wrapper.find_element(By.CSS_SELECTOR,
                                                    "ytd-channel-name#channel-name > #container > div#text-container > "
                                                    "yt-formatted-string#text").get_attribute(
                    "title")
            elif search_type == SearchEnum.HOME:
                title = text_wrapper.find_element(
                    By.CSS_SELECTOR, "h3 > a#video-title-link").get_attribute("title")
                channel = text_wrapper.find_element(By.CSS_SELECTOR,
                                                    "ytd-video-meta-block > div#metadata > div#byline-container > "
                                                    "ytd-channel-name#channel-name > #container > div#text-container > "
                                                    "yt-formatted-string#text").get_attribute(
                    "title")
        except NoSuchElementException:
            raise SE("Element not found while trying to find title or channel.")

        return {
            'thumbnail': thumbnail,
            "title": title,
            "channel": channel
        }

    @SE.handle_exceptions
    def home(self):
        """
        This function navigates to the home page.
        """
        logo = self.get_visible_element(
            By.CSS_SELECTOR, '#start > ytd-topbar-logo-renderer > a')
        sleep(0.5)
        self.click_element(logo)

    def wait(self, condition: EC, wait_time: int = 120):
        """
        Waits until the condition is met.

        Args:
            - condition (EC): The condition to wait for.
            - time (int): The time to wait for the condition to be met.

        """
        return WebDriverWait(self.driver, wait_time).until(condition)

    # @SE.handle_exceptions
    def get_clickable_element(self, by: str, locator: str):
        """
        Waits until the element is clickable and returns it.

        Locaters:
            - ID | XPATH | LINK_TEXT | PARTIAL_LINK_TEXT | NAME | TAG_NAME | CLASS_NAME | CSS_SELECTOR
            - (str): The locator for the element.

        Returns:
            - WebElement: The clickable element.

        """
        return self.wait(EC.element_to_be_clickable((by, locator)))

    @SE.handle_exceptions
    def get_visible_element(self, by: str, locator: str):
        """
        Waits until the element is visible and returns it.

        Locaters:
            - id | xpath | link_text | partial_link_text | name | tag_name | class_name | css_selector
            - (str): The locator for the element.

        Returns:
            - WebElement: The visible element.

        """
        return self.wait(EC.visibility_of_element_located((by, locator)))

    def scroll_to_element(self, element, offset=0):
        """
        Scrolls to the specified element with an optional offset.

        Args:
            - element (WebElement): The element to scroll to.
            - offset (int): The number of pixels to offset the scroll position by.
        """
        script = "var rect = arguments[0].getBoundingClientRect();" \
                 f"window.scrollTo(0, rect.top + window.pageYOffset + {offset});"
        self.driver.execute_script(script, element)

    @SE.handle_exceptions
    def scroll_to_bottom(self):
        """
        Scrolls to the bottom of the page.
        """
        scroll_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight")
        ActionChains(self.driver) \
            .scroll_by_amount(0, scroll_height) \
            .perform()

    @SE.handle_exceptions
    def click_element(self, element):
        """
        Clicks the specified element.

        Args:
            - element (WebElement): The element to click.
        """
        ActionChains(self.driver) \
            .move_to_element(element) \
            .click(element) \
            .perform()

    def playback_speed(self, speed: float):
        """
        This function sets the playback speed.

        Args:
            - speed (float): The speed to set the playback to.
        """
        self.driver.execute_script(
            f'''document.querySelector('video').playbackRate = {speed};''')
        print(f"Playback speed set to ==> {speed}")

    def video_quality(self, quality: str = '144p'):
        """
        :param quality:
        :return:
        """
        settings_button = self.get_visible_element(By.CSS_SELECTOR, 'button.ytp-button.ytp-settings-button')
        settings_button.click()
        sleep(1)
        quality_button = self.get_visible_element(By.XPATH, "//div[contains(text(),'Quality')]")
        quality_button.click()
        sleep(2)  # you can adjust this time
        desired_quality = self.get_visible_element(By.XPATH, f"//span[contains(string(),'{quality}')]")
        desired_quality.click()
        print(f"Quality set to {quality}")
        
    def video_speed(self, speed: str = '1.5'):
        """
        :param speed:
        :return:
        """
        settings_button = self.get_visible_element(By.CSS_SELECTOR, 'button.ytp-button.ytp-settings-button')
        settings_button.click()
        sleep(1)
        quality_button = self.get_visible_element(By.XPATH, "//div[contains(text(),'Playback speed')]")
        quality_button.click()
        sleep(2)  # you can adjust this time
        desired_quality = self.get_visible_element(By.XPATH, f"//span[contains(string(),'{speed}')]")
        desired_quality.click()
        print(f"Video speed set to {speed}")

    def mini_player(self):
        """
        This function set the video to mini player.
        """
        self.driver.execute_script(
            '''document.querySelector('button.ytp-miniplayer-button').click();''')

    def close(self):
        """
        This function closes all the tabs and quits the driver.
        """
        self.close_other_tabs()
        sleep(3)
        self.driver.quit()
        print(f"Browser closed ==> {self.browser_type}")
