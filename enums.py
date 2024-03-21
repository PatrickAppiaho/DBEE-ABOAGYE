from enum import Enum


class SearchEnum(Enum):
    """
    This class is an enum for the search type.
    """
    SEARCH = 'search'
    RELATED = 'related'
    HOME = 'home'


class BrowserEnum(Enum):
    """
    This class is an enum for the browser type.
    """
    CHROME = 'chrome'
    CHROMIUM = 'chromium'
    FIREFOX = 'firefox'
    EDGE = 'msedge'
    SAFARI = 'safari'
