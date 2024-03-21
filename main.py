from random import choice
from threading import Thread
from time import sleep

import browsers

from chrome import Chrome
from common import VIDEO_TITLE_AND_TIME, CHANNEL_NAME
from enums import BrowserEnum
from firefox import Firefox
from msedge import Edge


def open_browser(browser_t: BrowserEnum):
    """
    This function is responsible for opening the browser.
    """
    browser_mapping = {
        BrowserEnum.CHROME: Chrome,
        BrowserEnum.FIREFOX: Firefox,
        BrowserEnum.EDGE: Edge
    }

    if browser_t in browser_mapping:
        return browser_mapping[browser_t]()
    else:
        print(f"Unsupported browser type: {browser_t}")
        return None


def youtube_time_to_seconds(time_text):
    """ This function converts the YouTube time to seconds. """
    time_parts = list(map(int, time_text.split(':')))
    if len(time_parts) == 3:  # HH:MM:SS format
        return time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
    elif len(time_parts) == 2:  # MM:SS format
        return time_parts[0] * 60 + time_parts[1]
    elif len(time_parts) == 1:  # SS format
        return time_parts[0]
    else:
        raise ValueError('Invalid YouTube time format')


def get_selected():
    """
    This function is responsible for selecting the title.
    """
    return choice(VIDEO_TITLE_AND_TIME)


def main(
        browser_t: BrowserEnum = BrowserEnum.CHROME
):
    """
    This function is responsible for the main program.
    """
    opened_browser = open_browser(browser_t)

    if opened_browser is None:
        return

    title, time_text = get_selected()
    sleep(5)
    opened_browser.close_other_tabs()
    sleep(2)
    opened_browser.get("https://youtube.com")
    sleep(3)
    opened_browser.search(title)
    sleep(5)
    opened_browser.play_searched_video(CHANNEL_NAME)
    # opened_browser.video_quality()
    sleep(5)
    opened_browser.playback_speed(15)
    video_time = youtube_time_to_seconds(time_text)
    sleep(video_time / 15)
    # opened_browser.searched_video(
    #     " ", choice(CHANNEL_NAMES), SearchEnum.RELATED)
    # sleep(30)
    # opened_browser.mini_player()
    # sleep(5)
    # opened_browser.home()
    # sleep(5)
    # opened_browser.play_searched_video(
    #     RANDOM_VIDEO_TIME, CHANNEL_NAME, SearchEnum.HOME)
    opened_browser.close()


if __name__ == "__main__":
    browsers_list = list(browsers.browsers())
    skip_browsers = ["msie", "safari", 'chromium', 'opera']
    for i in range(0, 2):
        for browser in browsers_list:
            browser_type = browser['browser_type']
            if browser_type in skip_browsers:
                continue
            print("====================================================")
            print(f"Loop ==> {i} Opened -->  {browser_type}")
            print("====================================================")
            print(" ")
            Thread(target=main, args=(BrowserEnum(browser_type),)).start()
            sleep(5)
