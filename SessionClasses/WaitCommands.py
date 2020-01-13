"""
Selenium-built wait logic, read more here:
http://selenium-python.readthedocs.io/waits.html

Check out the implicit wait set by the Portal class upon driver
creation-- that's basically a back-up for when we don't utilize these
wait functions.

PARAMETER DOC:
* driver: web driver provided by the Portal class.
* pattern: string used to find the element, based on method.
* timeout: implicit wait time; throws an exception if the polled element hasn't
    been found by this time. Default is 5.
* element_type: identifying attribute for a web element. Default is ID.
"""

import os
import sys

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Commands.AssertionCommands import *

by_types = {
    'class': By.CLASS_NAME,
    'css': By.CSS_SELECTOR,
    'id': By.ID,
    'name': By.NAME,
    'text': By.LINK_TEXT,
    'xpath': By.XPATH
}


def wait_for_element_to_be_clickable(driver, expression, timeout=5):
    """
    Waits for the specified element to be clickable before proceeding.
    :param driver: Web driver object.
    :param expression: XPath expression from PageObject used to detect visibility.
    :param timeout: amount of time (in seconds) to wait for visibility; default is 5 seconds.
    """
    elem = driver.find_element_by_xpath(expression)
    for s in range(timeout):
        try:
            href_data = elem.get_attribute('href')
            if href_data is None:
                time.sleep(1)
            else:
                break
        except Exception:
            print("Exception raised in wait_for_element_to_be_clickable; page might not be ready.")
            break
    else:
        print("Expression \"{}\" could not detect a clickable element; page might not be ready.").format(expression if expression else '')


def wait_for_element_to_be_visible(driver, expression, timeout=5):
    """
    Waits for the specified element to be "visible" before proceeding.
    :param driver: Web driver object.
    :param expression: XPath expression from PageObject used to detect visibility.
    :param timeout: amount of time (in seconds) to wait for visibility; default is 5 seconds.
    """
    try:
        elem = driver.find_element_by_xpath(expression)
    except NoSuchElementException:
        print("Unable to locate element: {}\nPage might not be ready.".format(expression))
    else:
        for s in range(timeout):
            try:
                if elem.is_displayed():
                    break
                else:
                    time.sleep(1)
            except Exception:
                print("Exception raised in wait_for_element_to_be_visible; page might not be ready.")
                break
        else:
            print("Expression \"{}\" could not detect a visible element; page might not be ready.").format(expression)


def wait_until_window_changed(driver, contain_str):
    """
    Implicit wait time for a window to update the DOM.
    :param contain_str: String with the window property to be searched.
    """
    try:
        WebDriverWait(driver, 3).until(ec.title_contains(contain_str))
    except Exception:
        print("Window did not change in the allotted time: {0}s. The page might still be loading.\n".format(2))
