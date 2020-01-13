"""
Handles web-element and _driver related commands.
Acts as a wrapper around Selenium commands.
Each function must be static and accept at least two arguments.
Since the session loops catch Exceptions, no try/except blocks
are required as the error-types and messages will be reported,
unless you want to customize error messages.
"""

import decorator
import time
import textwrap
import uuid

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import \
    ElementClickInterceptedException, \
    ElementNotInteractableException, \
    NoSuchElementException

from SessionClasses.Exceptions.PortalExceptions import *


class PortalCommands:
    """
    Command-based class for controlling selenium commands. Function names
    which are not preceeded by "__" are available to the user as commands.
    """
    function_args = {}

    @decorator.decorator  # Required to prevent "inspect" from recognizing this
    def __switch_frame(f, func, _driver, page, *tokens):
        """
        Searches a PageHandler Object's "frame" attribute for the name of the web
        element. If found, that element is located in a frame, and the _driver
        needs to switch it's "active view" to that frame before the element can
        be interacted with.
        """
        element = tokens[0].name
        if page.frame_elements:
            for fr, elms in page.frame_elements.items():
                if element.lower() in list(map(lambda x: x.lower(), elms)):
                    frame = fr
                    break
            else:
                frame = None
        else:
            frame = None
        if frame is not None:
            _driver.switch_to_frame(frame)
            try:
                f(func, _driver, page, *tokens)
            finally:
                _driver.switch_to_default_content()
        else:
            f(func, _driver, page, *tokens)
        return func

    @decorator.decorator
    @__switch_frame
    def __verify_enabled(func, _driver, page, *tokens):
        for token in tokens:
            if token.type in ['PAGE_ELEMENT', 'WINDOWED_ELEMENT']:
                if isinstance(token.func, list):
                    for xpath in token.func:
                        try:
                            av = _driver.find_element_by_xpath(xpath.format(page.visible_pane)).is_enabled()
                        except NoSuchElementException as err:
                            pass
                        else:
                            if av:
                                func(_driver, page, *tokens)
                                break
                            else:
                                print("Element unavailable!")
                else:
                    try:
                        av = _driver.find_element_by_xpath(token.func).is_enabled()
                    except NoSuchElementException as err:
                        err_str = textwrap.dedent(str(err)).strip()
                        print("{0}".format(textwrap.fill(err_str, width=80)))
                    else:
                        if av:
                            func(_driver, page, *tokens)
                        else:
                            print("Element unavailable!")

    @staticmethod
    def back(_driver, _):
        """
        Acts as a "back" button in the browser. Selenium warns that this
        function can have unpredictable behavior on some sites, so if there's an
        issue with this commands, it might be best to write a new work flow.
        Generally it works though.
        :param _driver: web _driver.
        """
        _driver.back()

    @__verify_enabled
    def clear(_driver, _page, page_element):
        """
        Clears text in a textbox.
        :param _driver: Webdriver object.
        :param _page: Current page object.
        :param page_element: Token object containing the web element xpath.
        """
        elem = _driver.find_element_by_xpath(page_element.func)
        elem.clear()

    @__verify_enabled
    def click(_driver, _page, page_element):
        """
        Sends the click commands to a web element.
        :param _driver: Webdriver object.
        :param _page: Current page object.
        :param page_element: Token object containing the web element xpath.
        """
        elem = _driver.find_element_by_xpath(page_element.func)
        try:
            elem.click()
        except ElementClickInterceptedException:
            print("The element is obscured by another element. Close any",
                  "windows or pop-up's which might be in the way.")
        except ElementNotInteractableException:
            print("Unable to click the element: {0}".format(page_element.func))
            print("The element is likely within a drop-down menu or pop-up s",
                  "window which must be clicked before it is available.")
        else:
            time.sleep(3)

    @__verify_enabled
    def fill(_driver, _page, page_element, arb_text):
        """
        Enters text into a textbox.
        :param _driver: Webdriver object.
        :param _page: PageObject for the current page.
        :param page_element: Token object containing the web element xpath.
        :param arb_text: Token object with string to enter into the text box.
        """
        elem = _driver.find_element_by_xpath(page_element.func)
        elem.send_keys(arb_text.name)  # don't include "'s in text

    @__verify_enabled
    def fill_unique(_driver, _, page_element, default_arb_prefix="", default_arb_variable=""):
        """
        Enters text into a textbox and appends a unique string to the end of that text.
        :param _driver: Webdriver object.
        :param page_element: Token object containing the web element xpath.
        :param default_arb_prefix: The prefix to the unique string. Default is blank.
        :param default_arb_variable: Optional variable name created for the unique string. Saved as a command for the web driver's lifespan.
        """
        ustr = "{0}{1}".format(default_arb_prefix.name, uuid.uuid4().hex[:6].upper())
        elem = _driver.find_element_by_xpath(page_element.func)
        elem.send_keys(ustr)  # don't include "'s in text
        if default_arb_variable.name:
            _driver.test.setdefault(default_arb_variable.name, ustr)  # This was the only place I could put this to make it available to subsequent CommandHandler's.
            print('Temporary variable "{0}" created for the value "{1}"'.format(default_arb_variable.name, ustr))

    @__verify_enabled
    def enter(_driver, _page, page_element):
        """
        Enters text into a textbox.
        :param _driver: Web-_driver object.
        :param _page: PageObject for the current page.
        :param page_element: Token object containing the web element xpath.
        """
        elem = _driver.find_element_by_xpath(page_element.func)
        elem.send_keys(Keys.RETURN)  # don't include "'s in text

    @__verify_enabled
    def id(_driver, _page, page_element):
        """
        Highlight an element by briefly altering its CSS values.
        Useful for identifying the association between a command and a DOM element.
        :param _driver: webdriver object.
        :param _page: current page object.
        :param page_element: DOM element to be id'd.
        """
        # elem = _driver.find_element_by_xpath(page_element.func.format(_page.visible_pane))
        elem = _driver.find_element_by_xpath(page_element.func)
        original_style = elem.get_attribute('style')
        _driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            elem, 'background: yellow; border: 2px solid red;'
        )
        time.sleep(.5)
        _driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            elem, original_style
        )

    @staticmethod
    def refresh(_driver, _):
        """
        Refreshes the current page.
        :param _driver: Webdriver object.
        """
        _driver.refresh()

    @__verify_enabled
    def select_item(_driver, _page, page_element, arb_text):
        """
        Select a contained element, from a drop-down element, by identifying its text property.
        this should work for all the options in the given drop down when it is open.
        :param _driver: webdriver object.
        :param _page: current page object.
        :param page_element: DOM element containing another element.
        :param arb_text: expected value of the element's text property.
        """
        # '//*[contains(@class,"dijitMenuPopup") and not(contains(@style,"display") and contains(@style,"none"))]//table//tr//td[contains(@id, "dijit_MenuItem_") and contains(@class, "dijitMenuItemLabel")]'

        drop_down_elem = _driver.find_element_by_xpath(page_element.func)
        class_of_elem = drop_down_elem.get_attribute("class")

        drop_down_items = list()
        non_drop_down_items = list()
        multiselect_items = list()

        # get all the drop down items which are not dojo
        if 'dropdown' in class_of_elem:
            xpath = page_element.func + '//*[@class[contains(., "dropdown-link") and not(contains(., "hide"))]]'
            other_drop_down_items = xpath.format(_page.visible_pane)
            drop_down_items = _driver.find_elements_by_xpath(other_drop_down_items)

        # filtering drop down item xpath as in save-in
        elif 'dijitArrowButtonInner' in class_of_elem:
            filtering_menu_items = '//*[contains(@class,"dijitComboBoxMenuPopup") and not(contains(@style,"display") and contains(@style,"none"))]//*[contains(@class, "dijitMenuItem")]'
            drop_down_items = _driver.find_elements_by_xpath(filtering_menu_items)

        elif 'dijitMenuPopup' in class_of_elem:
            menu_items = '//tr[contains(@id, "dijit_MenuItem_")]'
            drop_down_items = _driver.find_elements_by_xpath(menu_items)

        elif 'dgrid-scroller' in class_of_elem:
            link_items = '//div[contains(@class,"dgrid-row")]//a'
            non_drop_down_items = _driver.find_elements_by_xpath(page_element.func + link_items)

        elif 'esriAnalysisLayersGrid' in class_of_elem:
            row_items = '//div[contains(@class,"dgrid-row")]'
            non_drop_down_items = _driver.find_elements_by_xpath(page_element.func + row_items)

        # detect the Filter-menu items
        elif 'accordion' in class_of_elem:
            li_elements = '//*[contains(@class,"drp-accordion__title")]'
            non_drop_down_items = _driver.find_elements_by_xpath(li_elements)

        # detect the Filter >> Folder items
        elif 'ftr-folder' in class_of_elem:
            li_elements = '//*[contains(@class,"ftr-folder__item")]'
            non_drop_down_items = _driver.find_elements_by_xpath(li_elements)

        elif 'MultiSelect' in class_of_elem:
            item_elements = '(//div[@role="tabpanel"]//table[@data-dojo-attach-point="_aggregateTable"]//div[@data-dojo-attach-point="wrapperDiv"])[last()-1]'
            multiselect_items = _driver.find_elements_by_xpath(item_elements)

        # get all the drop down items for dojo dropdown
        else:
            dojo_drop_down_items = '//*[contains(@class,"dijitMenuPopup") and not(contains(@style,"display") and contains(@style,"none"))]//table//tr'
            drop_down_items = _driver.find_elements_by_xpath(dojo_drop_down_items)

        # get each menu item text and select if the text is same
        if drop_down_items:
            for e in drop_down_items:
                # strip("\n") is only for ie
                if e.text.lower().strip('\n') == arb_text.name.strip('"').lower():
                    _driver.execute_script("arguments[0].click();", e)
                    break
        elif non_drop_down_items:
            for e in non_drop_down_items:
                if e.text.lower().strip('\n') == arb_text.name.strip('"').lower():
                    e.click()
                    break
        elif multiselect_items:
            for e in multiselect_items:
                if arb_text.name.strip('"').lower() in e.text.lower().split('\n'):
                    items = _driver.find_elements_by_xpath(item_elements + '//div[contains(@widgetid, "CheckedMultiSelectItem_")]')
                    for i, item in enumerate(items, 1):
                        if item.text.lower() == arb_text.name.strip('"').lower():
                            xpath = '(' + item_elements + '//div[contains(@widgetid, "CheckedMultiSelectItem_")]' + ')[{}]'.format(i)
                            checkbox = _driver.find_element_by_xpath(xpath + '//input[@role="checkbox"]')
                            checkbox.click()
                            break
        else:
            ItemNotFoundException(arb_text.name, page_element.name)

    @__verify_enabled
    def submit(_driver, _page, page_element):
        """
        Calls submit on the enclosing form of the provided element.
        :param _driver: webdriver object.
        :param _page: current page.
        :param page_element: Token object containing the web element xpath.
        """
        elem = _driver.find_element_by_xpath(page_element.func)
        elem.submit()
        time.sleep(2)
