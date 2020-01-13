import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from SessionClasses.Exceptions.PortalExceptions import *


class Portal:
    """
    Handles all site-specific work for the selenium web driver, and any
    endpoint-related work as well.
    """
    def __init__(self, browser, endpoint):
        """
        Opens browser and navigates to the first page.
        """
        self.browser = browser
        self.endpoint = endpoint

        self.inverse_endpoint = self.get_inverse_endpoint(self.endpoint)
        self.implicit_wait_amt = 2

        self.driver = self.set_driver(browser)
        self.driver.implicitly_wait(self.implicit_wait_amt)
        self.driver.maximize_window()

    @staticmethod
    def get_inverse_endpoint(endpoint):
        """
        Return non-SSL endpoint if the endpoint already is SSL-enabled, and
        vice-reversa if not. See InteractiveSession.set_current_page for more.
        :return: string or None, but will only return None if the endpoint
            provided by the user is incorrect in the first place.
        """
        if endpoint.startswith('https:'):
            return endpoint.replace('https:', 'http:')
        elif endpoint.startswith('http:'):
            return endpoint.replace('http:', 'https:')
        else:
            return None

    def navigate_to_page(self, url):
        """
        Joins the endpoint and a PageObject's url to navigate to the page. This
        function is probably only going to be used when starting a new test
        session. Most redirects will occur from click or submit actions.
        :param url: URL provided in main.py or from command-prompt (in Interactive Mode)
        """
        try:
            self.driver.get(url)
        except WebDriverException:
            print("Unable to load page. Is the URL correct?")
            print(url)
        else:
            pass

    def set_portal_driver(self, browser):
        self.driver = self.set_driver(browser)

    @staticmethod
    def set_driver(browser):
        """
        Set the working browser for testing.
        """
        accepted_browsers = {
            'chrome': webdriver.Chrome,
            'edge': webdriver.Edge,
            'firefox': webdriver.Firefox,
            'internetexplorer': webdriver.Ie,
            'safari': webdriver.Safari
        }
        if browser.lower() not in accepted_browsers:
            raise UnrecognizedBrowserException(browser)
        else:
            try:
                accepted_browser = accepted_browsers[browser.lower()]()
            except WebDriverException as err:
                m = "ERROR: WebDriverException was found.\n" \
                    "Resolve this by following the steps outlined in the repo's ReadMe:\n" \
                    "https://devtopia.esri.com/andr7495/Portal-UI-Harness#how-to-get-started\n" \
                    "Error {0}".format(err)
                sys.exit(m)
            else:
                return accepted_browser

    def close_window(self):
        """
        This comment takes up more space than the rest of the function.
        """
        self.driver.close()
