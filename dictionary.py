from typing import TypedDict
from selenium.webdriver.remote.webdriver import WebElement


class VideoInfo(TypedDict):
    """
    TypedDict for video information
    """
    thumbnail: WebElement
    title: str
    channel: str
