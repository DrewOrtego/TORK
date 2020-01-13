import decorator
import textwrap
import time

from selenium.common.exceptions import NoSuchElementException

from SessionClasses.Exceptions.PortalExceptions import *

from ControlObjects.ControlBase import ControlBase
from ControlObjects.Button import Button
from ControlObjects.TimeTextBox import TimeTextBox


class FailedAssertion(Exception):
    def __init__(self, message):
        self.message = message


class AssertionCommands:
    """
    Assert-related functions to be called by users. Exceptions raised here are picked
    up by the session class, and reporting-decisions are made there.
    """
    function_args = {}

    @decorator.decorator  # Required to prevent "inspect" from recognizing this
    def __switch_frame(func, driver, page, *tokens):
        """
        Searches a PageHandler Object's "frame" attribute for the name of the web
        element. If found, that element is located in a frame, and the driver
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
            driver.switch_to_frame(frame)
            try:
                func(driver, page, *tokens)
            finally:
                driver.switch_to_default_content()
        else:
            func(driver, page, *tokens)
        return func

    @__switch_frame
    def assert_contains(_driver, _, page_element_container, arb_text_pattern, default_int_seconds=5):
        """
        Determine whether an element with the given text is present within
        another element (e.g. drop-down menu, table of contents, etc.).
        :param _driver: Web-driver object.
        :param page_element_container: The element "containing" other elements. DOM searching starts here.
        :param arb_text_pattern: The text-pattern to be searched for among the sub-elements within the page_element_container.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-visible.
        """
        for t in range(default_int_seconds.name):
            try:
                elem = _driver.find_element_by_xpath(page_element_container.func)
                found_elem = elem.find_element_by_xpath('//*[contains(text(), "{}")]'.format(arb_text_pattern.name))
                if found_elem:
                    break
                else:
                    time.sleep(1)
            except Exception as err:
                time.sleep(1)
        else:
            m = 'Could not find an element within "{0}" containing the text pattern "{1}"'.format(
                page_element_container.name,
                arb_text_pattern.name
            )
            raise FailedAssertion(m)

    @__switch_frame
    def assert_clickable(_driver, _, page_element, default_int_seconds=5):
        """
        Determine whether an element is interable with the mouse
        for the given number of seconds.
        :param _driver: Web-driver object.
        :param page_element: After parsing/lexing, must contain a page element and
            optional arbitrary command.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-visible.
        """
        control = AssertionCommands.control_from_element(_driver, page_element)
        for t in range(default_int_seconds.name):
            if control.clickable:
                break
            else:
                time.sleep(1)
        else:
            if control.visible and not control.enabled:
                raise FailedAssertion('Element "{}" is visible but not enabled'.format(page_element.name))
            elif not control.visible and control.enabled:
                raise FailedAssertion('Element "{}" is enabled but not visible'.format(page_element.name))
            else:
                raise FailedAssertion('Element "{}" is not visible or enabled'.format(page_element.name))

    @staticmethod
    def assert_credits_required(_driver, _, arb_text_expected_amount, default_int_seconds=5):
        """
        Compares the credit-estimator's pop-up data-- in this case the credits required-- with an expected amount.
        :param _driver: web driver object
        :param arb_text_expected_amount: User-provided integer which is compared to the UI's reported number of records
        """
        for i in range(default_int_seconds.name):
            try:
                total_records_elem = _driver.find_element_by_xpath('(//div[@class="dijitDialogPaneContent"]//td[@data-dojo-attach-point="_creditsReqNode"])[last()]')
            except NoSuchElementException:
                pass
            else:
                total_records = total_records_elem.text
                if str(total_records) == arb_text_expected_amount.name:
                    break
                else:
                    raise FailedAssertion('The expected number of credits is "{0}", not "{1}"'.format(total_records, arb_text_expected_amount.name))
        else:
            raise FailedAssertion('The credit estimator pop-up could not be found.')

    @staticmethod
    def assert_total_records(_driver, _, arb_text_expected_amount, default_int_seconds=5):
        """
        Compares the credit-estimator's pop-up data-- in this case the total records-- with an expected amount.
        :param _driver: web driver object
        :param arb_text_expected_amount: User-provided integer which is compared to the UI's reported number of records
        """
        for i in range(default_int_seconds.name):
            try:
                total_records_elem = _driver.find_element_by_xpath('(//div[@class="dijitDialogPaneContent"]//td[@data-dojo-attach-point="_totalRecordsNode"])[last()]')
            except NoSuchElementException:
                pass
            else:
                total_records = total_records_elem.text
                if str(total_records) == arb_text_expected_amount.name:
                    break
                else:
                    raise FailedAssertion('The expected number of records is "{0}", not "{1}"'.format(total_records, arb_text_expected_amount.name))
        else:
            raise FailedAssertion('The credit estimator pop-up could not be found.')

    @__switch_frame
    def assert_disabled(_driver, _, page_element, default_int_seconds=5):
        """
        Determine whether an element is currently disabled in the UI for the given number of seconds.
        :param _driver: Web-driver object.
        :param page_element: A page element to be identified.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-disabled.
        """
        control = AssertionCommands.control_from_element(_driver, page_element)
        for t in range(default_int_seconds.name):
            if not control.enabled:
                break
            else:
                time.sleep(1)
        else:
            raise FailedAssertion('Element "{}" is enabled'.format(page_element.name))

    @__switch_frame
    def assert_enabled(_driver, _, page_element, default_int_seconds=5):
        """
        Determine whether an element is currently disabled in the UI for the given number of seconds.
        :param _driver: Web-driver object.
        :param page_element: A page element to be identified.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-disabled.
        """
        control = AssertionCommands.control_from_element(_driver, page_element)
        for t in range(default_int_seconds.name):
            if control.enabled:
                break
            else:
                time.sleep(1)
        else:
            raise FailedAssertion('Element "{}" is not enabled'.format(page_element.name))

    @staticmethod
    def assert_in_toc(_driver, _, arb_text_pattern):
        """
        Checks the table of content for a layer with the matching name provided by the user.
        :param _driver: webdriver object
        :param arb_text_pattern: Name of the layer to be searched for
        """
        toc_exp = '//div[@id="tocContentPane"]//div[@id="toc-main"]//div[@class="toc_layer  dojoDndItem"]//table//td//span[@class="toc_name toc_layerName"]'
        toc_elements = _driver.find_elements_by_xpath(toc_exp)
        if toc_elements:
            for elem in toc_elements:
                if elem.text == arb_text_pattern.name:
                    break
            else:
                raise ItemNotFoundException(arb_text_pattern.name, "Table of Contents")
        else:
            raise ElementNotFoundException("Table of Contents")

    @__switch_frame
    def assert_not_contains(_driver, _, page_element_container, arb_text_pattern, default_int_seconds=5):
        """
        Determine whether an element with the given text is NOT present within
        another element (e.g. drop-down menu, table of contents, etc.).
        :param _driver: Web-driver object.
        :param page_element_container: The element "containing" other elements. DOM searching starts here.
        :param arb_text_pattern: The text-pattern to be searched for among the sub-elements within the page_element_container.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-visible.
        """
        for t in range(default_int_seconds.name):
            try:
                elem = _driver.find_element_by_xpath(page_element_container.func)
                found_elem = elem.find_element_by_xpath('{0}//*[contains(text(), "{1}")]'.format(page_element_container.func, arb_text_pattern.name))
                time.sleep(1)
            except NoSuchElementException:
                break
            except Exception as err:
                time.sleep(1)
        else:
            m = 'Found an element within "{0}" containing the text pattern "{1}"'.format(
                page_element_container.name,
                arb_text_pattern.name
            )
            raise FailedAssertion(m)

    @__switch_frame
    def assert_not_visible(_driver, _, page_element, default_int_seconds=5):
        """
        Determine whether an element is currently invisible in the UI for the given number of seconds.
        :param _driver: Web-driver object.
        :param page_element: A page element to be identified.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-invisible.
        """
        control = AssertionCommands.control_from_element(_driver, page_element)
        for t in range(default_int_seconds.name):
            if not control.visible:
                break
            else:
                time.sleep(1)
        else:
            raise FailedAssertion('Element "{}" is visible'.format(page_element.name))

    @__switch_frame
    def assert_text(_driver, _, page_element, arb_text, default_int_seconds=5):
        """
        Compares the text-attribute or value of an element to the text-argument in a command
        for the given number of seconds.
        :param _driver: Web-driver object.
        :param page_element: Element with a text property.
        :param arb_text: Expected text value of the provided element.
        :param default_int_seconds: Number of seconds to continue pinging until the element's text is read.
        """
        for t in range(default_int_seconds.name):
            try:
                element = _driver.find_element_by_xpath(page_element.func)
                elem_text = element.text or element.get_attribute('value')
                if elem_text == arb_text.name:
                    break
                else:
                    time.sleep(1)
            except Exception:
                time.sleep(1)
        else:
            m = '{0}\'s text is not equal to "{1}"'.format(page_element.name, arb_text.name)
            raise FailedAssertion(m)

    @staticmethod
    def assert_title(_driver, _, page_title, default_int_seconds=5):
        """
        Compares the text-attribute or value of a page's title to the text-argument in a command
        for the given number of seconds.
        :param _driver: Web-driver object.
        :param page_title: Contains the user-expected title of the current page.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-visible.
        """
        for t in range(default_int_seconds.name):
            try:
                driver_title = _driver.title.strip()
                if driver_title == page_title:
                    break
                else:
                    time.sleep(1)
            except Exception:
                time.sleep(1)
        else:
            m = 'Page title "{0}" does not equal {1}'.format(driver_title, page_title.name)
            raise FailedAssertion(m)

    @__switch_frame
    def assert_visible(_driver, _, page_element, default_int_seconds=5):
        """
        Determine whether an element is currently visible in the UI for the given number of seconds.
        It might be possible that a visible element is inactive in the DOM,
        in which case this assert would throw an erroneous exception.
        :param _driver: Web-driver object.
        :param page_element: A page element to be identified.
        :param default_int_seconds: Number of seconds to continue pinging until the element is considered non-visible.
        """
        control = AssertionCommands.control_from_element(_driver, page_element)
        for t in range(default_int_seconds.name):
            if control.visible:
                break
            else:
                time.sleep(1)
        else:
            raise FailedAssertion('Element "{}" is not visible'.format(page_element.name))

    @staticmethod
    def control_from_element(_driver, page_element):
        """
        Get control object from page element
        :param _driver: Web-driver object.
        :param page_element: A page element
        """
        try:
            element = _driver.find_element_by_xpath(page_element.func)
        except NoSuchElementException:
            raise ElementNotFoundException(page_element.name)
        # Initialize a control object
        control = ControlBase(element)
        # If element has dijit parent, then use the dijit parent to get the control's clases. This is
        # used to figure out control's type.
        element = control.element if control.dijit_parent_element is None else control.dijit_parent_element
        class_attrs = element.get_attribute("class").split(" ")
        if "dijitTimeTextBox" in class_attrs:
            # TimeTextBox control has a class named dijitTimeTextBox
            return TimeTextBox(element)
        elif "dijitButton" in class_attrs:
            # Button control has a class named dijitButton
            return Button(element)
        else:
            # If none supporting object is detected, using the base control object.
            return control
