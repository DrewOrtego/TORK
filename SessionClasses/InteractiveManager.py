"""
Handles general Portal functions and UI interaction. Provides logic for
interacting with the site and driver.
"""

import os
from random import randint
import sys

from SessionClasses.PortalHandler import Portal
from SessionClasses.PageHandler import PageHandler
from .CommandHandler import CommandHandler


class InteractiveSession:
    """
    Invokes a test session controlled by the commands line.
    """
    def __init__(self):
        """
        Preps all objects (portal, commands, pages) and begins infinite
        command-accepting loop for user input.
        """
        print("Starting Interactive Mode...")
        os.chdir(os.sep.join(os.path.dirname(os.path.realpath(__file__)).split(os.sep)[:-1]))
        self.current_page_object = None
        self.prompt = '> '
        self.save_enabled = False
        self.try_mode = False
        self.portal = Portal(*self.get_config_params())
        self.ready_messages = [
            'reporting for duty!',
            'is ready for orders!',
            'is now listening!',
            'prepped and ready!',
            'ready to roll out!'
        ]

        self.commands = CommandHandler()
        self.commands.set_static_commands()

        self.pages = PageHandler()
        self.pages.set_page_objects()

        print("Navigating to page {0}...".format(self.portal.endpoint))
        self.portal.navigate_to_page(self.portal.endpoint)
        self.current_page_object = self.pages.get_current_page(self.portal)
        self.commands.set_current_page_commands(self.current_page_object)
        self.commands.set_visible_element_commands(self.portal, self.current_page_object)
        self.pages.verify_page_has_loaded(self.current_page_object, self.portal)

        print("\nInteractive Session {}\n".format(self.ready_messages[randint(0, len(self.ready_messages)-1)]))
        self.start_input_loop()

    def get_config_params(self):
        """
        Checks the script arguments for a browser and endpoint string.
        Prompts user for any missing arguments.
        :return: (Tuple - String) All required parameters.
        """
        try:
            browser = sys.argv[2]
        except IndexError:
            browser = self.get_browser()

        try:
            endpoint = sys.argv[3]
        except IndexError:
            endpoint = self.get_endpoint()

        return browser, endpoint

    def get_portal_commands(self):
        return list(map(lambda x: x.lower(), list(self.portal_commands.keys())))

    def start_input_loop(self):
        """
        Infinite loop which prompts user for input and updates the page, command,
        and session attributes based on the web-driver's current page.
        :return: You can never return from here. NEVER!
        """
        self.portal.driver.test = dict()
        while True:
            user_input = input(self.prompt)
            self.current_page_object = self.pages.get_current_page(self.portal)
            self.commands.set_current_page_commands(self.current_page_object)
            self.commands.set_visible_element_commands(self.portal, self.current_page_object)
            self.pages.verify_page_has_loaded(self.current_page_object, self.portal)
            try:
                self.commands.execute_command(user_input, self)
            except:  # Accepts any Exception to prevent crashes and log useful info
                print('{0}: {1}'.format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
            else:
                pass
