"""
Controls the work flow for testing all tools. Includes all logic related to
organizing assertion files, instantiating page and commands objects, and logging.
"""

from datetime import datetime
import logging
import logging.handlers
import os
import sys
import time

from SessionClasses.PageHandler import PageHandler
from SessionClasses.PortalHandler import Portal
from .CommandHandler import CommandHandler
from .DatabaseManager import Database
from .TestHandler import TestHandler


class AutomatedSession:
    """
    Handles automation of running test files. Configured in main.py.
    """
    def __init__(self, assertion_levels, verbose, log_file_dir, test_file_dir, parameters,
                 browsers, selected_test_files, database, tasks):
        """
        Handles validation of all parameters from main.py as well as test file
        content. Calls functions for running test files.
        :param assertion_levels: (list - strings) level of test files to run.
            * 'sanity'
            * 'release'
        :param verbose: (bool) if True, prints maximum info to the console.
        :param log_file_dir: (string) path to the folder where you'd like to create log files.
        :param test_file_dir: (string) path to the folder which contains the test files.
        :param parameters: (dictionary) contains login info. (site, username, password)
        :param browsers: (list - strings) names of browsers to test. (Case-insensitive)
            * 'FireFox'
            * 'Chrome'
        :param selected_test_files: (list - strings) the only test files to run during the test session.
        :param database: (str) if used, posts results to the specified database.
        :param tasks: (dictionary) folder structure to follow when parsing for test files.
        """
        os.chdir(os.sep.join(os.path.dirname(os.path.realpath(__file__)).split(os.sep)[:-1]))
        self.arg_commands = dict()
        self.commands = None
        self.current_page_object = None
        self.end_time_ms = None
        self.failed_tests = dict()
        self.log = None
        self.log_file_dir = log_file_dir
        self.pages = None
        self.portal = None
        self.successful_tests = dict()
        self.start_time_ms = None
        self.test_file_dir = test_file_dir
        self.test_manager = None
        self.test_results = dict()
        self.try_mode = False
        self.verbose = verbose

        # Parameter-validation functions which will exit the program if any errors occur
        self.validate_log_file_path(log_file_dir)
        self.validate_browsers(browsers)
        self.validate_assertion_levels(assertion_levels)

        # Iterate over main.py parameters and create log file prior to running tests
        for params_name, params_dict in parameters.items():
            if not self.validate_parameters(params_dict):  # raises an except. if anything's wrong, so we can assume set_params will work next
                print("Skipping {}\n".format(params_name))
                break
            self.set_parameters(params_dict)
            for browser_name in list(map(lambda b: b.lower(), browsers)):
                for assertion_level in list(map(lambda a: a.lower(), assertion_levels)):
                    print(assertion_level, browser_name, params_dict)
                    self.start_time_ms = time.time()
                    self.current_assertion_level = assertion_level
                    self.current_browser = browser_name

                    # Set up the log file
                    self.set_log(log_file_dir)
                    self.log.info(self.endpoint)
                    self.log.info("{0}, {1}".format(browser_name, assertion_level))

                    # Validate test files and report any errors
                    self.test_manager = TestHandler(selected_test_files, test_file_dir, assertion_level, tasks)
                    if self.test_manager.invalid_files:
                        self.log.error(self.test_manager.invalid_files)  # Move onto next session
                    else:
                        self.endpoint = params_dict['endpoint']

                        # Get each test file, validate it, and run it
                        for test_file, analysis_category, tool in self.test_manager.get_next_test_file():
                            self.set_test_results(analysis_category, tool)
                            if self.validate_test_file(test_file):
                                self.run_test_file(test_file, analysis_category, tool)
                            else:
                                self.log.error("INVALID TEST FILE : {}".format(test_file))
                        self.end_time_ms = time.time()
                        self.log.info("\nEND OF SESSION")

                        # Update Database
                        if database:
                            Database(self, database)

    def run_test_file(self, test_file, analysis_category, tool):
        """
        Iterate and run through all commands in test file.
        Requires a new browser for each test, and available commands must be updated
        after each command is run.
        At this point we are sharing work flows with InteractiveManager.
        :param analysis_category: current category of the tool. Used here to update
            the test_results dict.
        :param tool: current tool being tested. Used here to update the test_results
            dict.
        :param test_file: (str) full path to the test file.
        """
        self.portal = Portal(self.current_browser, self.endpoint)

        self.commands = CommandHandler()
        self.commands.set_static_commands(self)

        self.pages = PageHandler()
        self.pages.set_page_objects()

        self.portal.navigate_to_page(self.endpoint)

        self.portal.driver.test = dict()  # Used for fill-unique command

        with open(test_file, 'r') as file_content:
            test_file_path = test_file.split(self.test_file_dir)[1]
            self.log.info('\n* FILE: {}'.format(test_file_path))
            test_file_name = test_file.split('\\')[-1]
            for e, line in enumerate(file_content):
                if line == '\n' or line.startswith('#'):
                    pass
                else:
                    line = line.strip('\n')
                    self.current_page_object = self.pages.get_current_page(self.portal)
                    self.commands.set_current_page_commands(self.current_page_object)
                    self.commands.set_visible_element_commands(self.portal, self.current_page_object)
                    self.pages.verify_page_has_loaded(self.current_page_object, self.portal)
                    # Run the commands, report any errors/exceptions
                    try:
                        if self.verbose:
                            print("{0}{1}".format("try: " if self.try_mode else '', line))
                        self.commands.execute_command(line, self)
                    except Exception:  # Accepts any Exception to prevent crashes and log useful info
                        if self.try_mode:
                            pass
                        else:
                            self.log.exception(
                                msg='    {0} {1}'.format(sys.exc_info()[0].__name__, sys.exc_info()[1]),
                                exc_info=False,
                                stack_info=False
                            )
                            self.log.error("    Line {0}: {1}".format(e+1, line))
                            self.test_results[self.current_assertion_level][self.current_browser][analysis_category][tool].setdefault(
                                test_file_name, 'FAIL: {0} -- {1}'.format(sys.exc_info()[0].__name__, sys.exc_info()[1])
                            )
                            screenshot_file_path = os.path.join(self.log_file_dir, test_file_name.split('.')[0] + '.png')
                            try:
                                os.remove(screenshot_file_path)
                            except FileNotFoundError:
                                pass
                            finally:
                                self.portal.driver.get_screenshot_as_file(screenshot_file_path)
                            break  # Stop iteration of test file
            else:
                self.log.info("* Pass")
                self.test_results[self.current_assertion_level][self.current_browser][analysis_category][tool].setdefault(
                    test_file_name, 'PASS'
                )

            # self.log.info("PASS")  # No exception was thrown, test passed
            self.portal.close_window()

    def set_log(self, log_file_dir):
        """
        Set up a new log file using the LogLady class.
        :param log_file_dir: (str) folder location of log file, from main.py.
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        log_file_name = 'UI {0} {1} {2}.log'.format(
            current_time, self.current_browser, self.current_assertion_level
        )
        log_file_path = os.path.join(log_file_dir, log_file_name)
        log = LogLady(log_file_path)
        log.create_log()
        print("Created log file: {}".format(log_file_path))
        self.log = log.get_logger()

    def set_parameters(self, parameters):
        """
        Sets the endpoint attr. to the endpoint provided in main.py.
        Populates the arg_commands dict with all extra commands.
        These commands are available at all times.
        Works great with usernames and passwords.
        :param parameters: dict provided via main.py.
        """
        self.endpoint = parameters['endpoint']
        if 'args' in parameters.keys():
            for e, a in enumerate(parameters['args']):
                exec('self.arg_commands.setdefault("arg_{}", a)'.format(e))

    def set_test_results(self, analysis_cat, tool):
        """
        Sets up a dictionary for reporting to Flask site once testing is complete.
        :param analysis_cat: category of analysis tool (standard, raster, geoanalytics)
        :param tool: name of analysis tool being tested
        :return:
        """
        self.test_results.setdefault(self.current_assertion_level, dict())
        self.test_results[self.current_assertion_level].setdefault(self.current_browser, dict())
        self.test_results[self.current_assertion_level][self.current_browser].setdefault(analysis_cat, dict())
        self.test_results[self.current_assertion_level][self.current_browser][analysis_cat].setdefault(tool, dict())

    @staticmethod
    def validate_assertion_levels(assertion_levels):
        """
        Validates the expected assertion levels.
        :return:
        """
        valid_assertions = ['sanity', 'release']
        invalid_assertions = list(filter(lambda a: a.lower() not in valid_assertions, assertion_levels))
        if not assertion_levels:
            m = "No assertion-type(s) specified in main.py.\n" \
                "Please update 'assertion_level' to include at least one of the following:\n" \
                "{0}".format(valid_assertions)
            sys.exit(m)
        elif invalid_assertions:
            m = "Error: Invalid assertion name{0} found in main.py:\n" \
                "{1}\n" \
                "'assertion_level' will only accept the following values:\n" \
                "{2}".format('s' if len(invalid_assertions) > 1 else '', invalid_assertions, valid_assertions)
            sys.exit(m)
        else:
            pass

    @staticmethod
    def validate_browsers(browsers_list):
        """
        Verify that the provided browsers are expected, returns list of lowercase
        strings if valid. Otherwise prints error message and quits the program.
        :param browsers_list: (list - strings) list of browser names from main.py
        :return browsers_list: converted to lower-case (if validation passes)
        """
        valid_browsers = ['firefox', 'chrome', 'internetexplorer', 'safari', 'edge']
        invalid_browsers = list(filter(lambda b: b.lower() not in valid_browsers, browsers_list))
        if not browsers_list:
            m = "No browsers specified for tests." \
                "Please update to include at least one of the following:\n" \
                "{0}".format(valid_browsers)
            sys.exit(m)
        elif invalid_browsers:
            m = "Error: Invalid browser name{0} found in main.py:\n" \
                "{1}\n" \
                "'browsers' will only accept the following names:\n" \
                "{2}".format('s' if len(invalid_browsers) > 1 else '', invalid_browsers, valid_browsers)
            sys.exit(m)
        else:
            pass

    @staticmethod
    def validate_parameters(parameters):
        """
        Verify that the expected data structures and keys are present
        in the parameters parameter from main.py. Quits program if error.
        :param parameters: (dict) contains endpoint, username, and password
        :return bool: True if no errors.
        """
        errors = list()
        if 'endpoint' not in parameters.keys():
            errors.append('* Key "endpoint" missing from parameter dictionary in main.py.')
        if len(parameters.keys()) == 2 and 'args' in parameters.keys():
            if not isinstance(parameters['args'], list):
                errors.append('* Value for Key "args" expected a list, found {0}.'.format(type(parameters['args'])))
        else:
            errors.append('* Invalid key found in parameters dictionary. Expected "endpoint" and "args" only.')
        if errors:
            print("ERROR{}:".format('s' if len(errors) > 1 else ''))
            for e in errors:
                print(e)
            return False
        else:
            return True

    @staticmethod
    def validate_log_file_path(log_file_dir):
        """
        Creates a file to which all the log-write commands will be written.
        :param log_file_dir: (str) path to the location of the log file.
        """
        if os.path.exists(log_file_dir):
            print("Log file path found: {0}".format(log_file_dir))
        else:
            m = "ERROR: Could not find the file path: {0}\n" \
                "Please create the directory or specify an existing one.".format(log_file_dir)
            sys.exit(m)

    @staticmethod
    def validate_test_file(test_file):
        """
        Checks file for known errors and prevents running/parsing broken test files.
        :param test_file: (str) path to file to be tested.
        :return: (bool, str) True and '' if no errors are found, False and error message otherwise.
        ToDo: Collect common errors after test-writing session on 6/14
        ToDo: Finish this
        """
        if True:
            return True, ''
        else:
            m = 'Test file is invalid for the following reason: ToDo'
            return False, m


class LogLady:
    """
    One day, the log will have something to say about this.
    """
    def __init__(self, file_path):
        """
        Handles settings for log files.
        The formatter is extremely useful since it can pre-append
        any string to the output, including timestamps, level-type, etc.
        Formatting attributes:
        https://docs.python.org/2/library/logging.html#logrecord-attributes
        :param file_path: (str) full path to the log file.
        """
        self.file_path = file_path
        self.formatter = logging.Formatter('%(message)s')
        self.logger = None
        self.level = logging.DEBUG

    def create_log(self):
        """
        Configures a log file using a unique ID (the file name) for DEBUG-level use.
        """
        log = logging.getLogger(self.file_path.split('.')[-1])
        log.setLevel(self.level)

        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)

        fh = logging.FileHandler(filename=self.file_path)
        fh.setFormatter(self.formatter)
        fh.setLevel(self.level)
        log.addHandler(fh)

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(self.formatter)
        sh.setLevel(self.level)
        log.addHandler(sh)

        self.logger = log

    def get_logger(self):
        return self.logger
