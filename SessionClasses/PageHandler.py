import os

from SessionClasses.Exceptions.TestSessionExceptions import *
from SessionClasses.WaitCommands import *


class PageHandler:
    """
    Functions for working with the current PageObject. Retrieves page-relevant
    information. This never sees the web-driver: that code is in PortalHandler.py.
    """
    def __init__(self):
        self.page_objects = dict()  # Set in import_page_objects

    def get_current_page(self, portal):
        """
        Returns a page object based on the web-driver's current URL.
        Searches all the Page Objects for a match before raising an UnknownPageObject error.
        Still a work in progress as paradigms for parsing URL's are developed.
        """
        for _, page_object in self.page_objects.items():
            # Check whether current URL is an exact match of the Page Object's id
            if portal.driver.current_url == page_object.id:
                return page_object
            # Check whether the URL without a query matches the id
            if '?' in portal.driver.current_url:
                url_no_params = portal.driver.current_url.split('?')[0]
                if url_no_params == page_object.id:
                    return page_object
            # Check whether the URL without a click-through matches the id
            if '#' in portal.driver.current_url:
                url_no_params = portal.driver.current_url.split('#')[0]
                if url_no_params == page_object.id:
                    return page_object
            # Check whether the complete path is recognized
            url_no_params = portal.driver.current_url.split('?')[0]
            url_no_click_through = url_no_params.split('#')[0]
            path = url_no_click_through.split('/')
            if page_object.id == path[-1]:
                return page_object
            # Check whether a partial path is recognized
            else:
                partial_path = path[-1]
                for p in path[-2:0:-1]:
                    # if p.count('.') > 1:
                    #     break
                    if page_object.id == partial_path:
                        return page_object
                    else:
                        partial_path = '/'.join([p, partial_path])
        else:
            raise UnknownPageError("Could not find a corresponding Page Object for the current page.")

    def get_page_objects(self):
        """
        :return dict: references to page objects in PageObjects directory
        """
        return self.page_objects

    def set_page_objects(self):
        """
        Iterates through the PageObjects directory to import each class from
        each module. It's important to keep the module and class names the same
        for this code to work.
        TODO Create dict with module-class pairs if there's a mismatch, then report.
        """
        def get_page_names():
            """
            Returns all the page object names from the PageObjects directory.
            This is designed to recognize all .py files and consider them as PageObjects.
            This is agnostic to the constraints set in import_page_objects.
            :return: list of page names.
            """
            found_page_object_names = list()
            file_path = '\\'.join(os.path.realpath(__file__).split('\\')[:-2])
            for _, __, f in os.walk(os.path.join(file_path, 'PageObjects')):
                for i in f:
                    if i.endswith('.py'):
                        found_page_object_names.append(i[:-3])
            return found_page_object_names

        for module_name in get_page_names():
            try:
                exec('from PageObjects.{0} import {0}'.format(module_name))
            except Exception as err:
                m = "Detected a naming convention issue in the file '{1}.py'.\n"\
                    "Update the module or class name to match each other.\n"\
                    "Error: {0}".format(err, module_name)
                print(m)
            else:
                self.page_objects.setdefault(
                    module_name,
                    eval('locals()["{0}"]()'.format(module_name))
                )

    @staticmethod
    def verify_page_has_loaded(current_page_object, portal):
        """
        Utilizes wait commands to ensure that the expected element of a page
        has loaded before assuming that the entire page is ready to respond
        to user input.
        :param current_page_object: (PageObject) derived page from the browser's URL.
        :param portal: (Portal) from PortalManager, contains web driver.
        """
        select_wait_function = {
            'clickable': wait_for_element_to_be_clickable,
            'visible': wait_for_element_to_be_visible
        }
        try:
            select_wait_function[current_page_object.wait_method](
                portal.driver, expression=current_page_object.wait_element
            )
        except KeyError:
            raise UnknownPageObjectWaitMethod(
                current_page_object.__class__.__name__,
                current_page_object.wait_method
            )
