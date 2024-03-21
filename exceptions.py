"""
This module contains a custom exception class for handling Selenium exceptions.
"""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
    ElementNotVisibleException,
    ElementNotSelectableException,
    InvalidElementStateException,
    InvalidSelectorException,
    NoSuchWindowException,
    SessionNotCreatedException,
    TimeoutException,
    JavascriptException,
    MoveTargetOutOfBoundsException,
    ImeNotAvailableException,
    ImeActivationFailedException,
    NoSuchFrameException,
    NoAlertPresentException,
    NoSuchAttributeException,
    UnexpectedAlertPresentException,
    InvalidCookieDomainException,
    UnableToSetCookieException,
    ScreenshotException,
    InvalidArgumentException,
    InvalidCoordinatesException,
    InvalidSessionIdException,
    UnknownMethodException,
    UnexpectedTagNameException,
    InvalidSwitchToTargetException
)


class SeleniumException(Exception):
    """
    Custom exception class for handling Selenium exceptions.
    """

    def __init__(self, message):
        """
        Initializes a new instance of the SeleniumException class.

        Args:
            message (str): The error message.
        """
        self.message = message

    @staticmethod
    def handle_exceptions(func):
        """
        Decorator function that catches all Selenium exceptions.

        Args:
            func (function): The function to decorate.

        Returns:
            function: The decorated function.
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                    NoSuchElementException,
                    StaleElementReferenceException,
                    WebDriverException,
                    ElementNotVisibleException,
                    ElementNotSelectableException,
                    InvalidElementStateException,
                    InvalidSelectorException,
                    NoSuchWindowException,
                    SessionNotCreatedException,
                    TimeoutException,
                    JavascriptException,
                    MoveTargetOutOfBoundsException,
                    ImeNotAvailableException,
                    ImeActivationFailedException,
                    NoSuchFrameException,
                    NoAlertPresentException,
                    NoSuchAttributeException,
                    UnexpectedAlertPresentException,
                    InvalidCookieDomainException,
                    UnableToSetCookieException,
                    ScreenshotException,
                    InvalidArgumentException,
                    InvalidCoordinatesException,
                    InvalidSessionIdException,
                    UnknownMethodException,
                    UnexpectedTagNameException,
                    InvalidSwitchToTargetException
            ) as err:
                raise SeleniumException(f"Exception occurred: {err}") from err

        return wrapper
