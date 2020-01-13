import copy
import inspect
import os
import sys
import traceback

from selenium.common.exceptions import *

from .Exceptions.CommandExceptions import *


class CommandHandler:
    """
    Handles commands management for all things commands-related. Use this
    to update and get available commands.
    """
    def __init__(self):
        # static commands; these remain the same throughout testing
        self.session_arguments = dict()
        self.assertion_commands = dict()
        self.general_commands = dict()
        self.macro_commands = dict()
        self.portal_commands = dict()

        # dynamic commands; these updates based on the current page
        self.current_page_commands = dict()
        self.windowed_element_commands = dict()

        # Consolidation of each command-classes function_args attribute
        self.function_args = dict()

    def execute_command(self, user_input, session):
        """
        Error-check and run the user's input. All of the functions raise Exceptions
        when an issue is found with the input, thus any broken dependencies between
        variables and functions are conveniently unreachable.
        :param user_input: commands to be executed
        :param session: session for accessing both session and page-related attributes
        """
        user_input = [word for word in user_input.split(" ")]
        user_input = list(filter(lambda i: i, user_input))  # Remove space characters
        if user_input:
            parsed = self.parse_input(user_input)
            tokens = self.tokenize_commands(parsed, session.portal.driver.test)
            valid_tokens = self.validate_tokens(tokens)
            self.run_command(valid_tokens, session)
        else:
            raise NoCommandsFound("I beg your pardon?")

    @staticmethod
    def get_windowed_element_commands(path):
        """
        Joins all args together to form the path to the .py file containing
        the dynamic commands. Imports the module containing the commands, and
        searches for the single dict inside that module.
        More info here:
        https://devtopia.esri.com/andr7495/Portal-UI-Harness/wiki/Writing-XPath-for-Analysis-Tools#requirements
        :param path: complete dir. hierarchy to the file with the visible element-command pairs.
        """
        error_dict = dict()  # Save some memory by returning this for any error

        # Build path to module
        additional_cmd_dir = os.path.join(os.sep.join(os.getcwd().split(os.sep)), 'Commands')
        dir_path = os.path.join(additional_cmd_dir, os.sep.join(path.split('\\')[:-1]))
        sys.path.insert(0, dir_path)

        # Attempt to import the module
        module_name = path.split('\\')[-1]
        module_name = ''.join(module_name.split(' '))
        module_name = ''.join(module_name.split('-'))
        try:
            exec('import {0}'.format(module_name))
        except ModuleNotFoundError:
            m = "WARNING: Could not find the commands for the \"{0}\" module in the {1} directory." \
                " Compare the dynamic_element dict and the folder/file names for discrepancies."
            print(m.format(module_name, dir_path))
            return error_dict
        except SyntaxError:
            m = "WARNING: A syntax error occurred while trying to import \"{0}\"." \
                " Verify that the module's name is import-legal."
            print(m.format(module_name))
            return error_dict

        # Get all non-magic attributes of the module
        all_attributes = eval('dir({})'.format(module_name))
        non_magic_attribute_names = list(
            filter(
                lambda a: not a.startswith('__') and not a.endswith('__'),
                all_attributes
            )
        )
        g = globals()
        l = locals()
        all_types = [eval('type({}.{})'.format(module_name, a), g, l) for a in non_magic_attribute_names]
        num_dict = sum(list(map(lambda t: isinstance(t, dict), all_types)))

        # Check for unexpected attributes or unexpected type
        if num_dict > 1:
            print("ERROR: Multiple attributes found in {0}. Refactor to a single dictionary.\n".format(module_name))
            return error_dict
        else:
            obj = eval('{0}.{1}'.format(module_name, non_magic_attribute_names[0]))
            if not isinstance(obj, dict):
                print("ERROR: Non-dict attribute returned from the {0} module.".format(module_name),
                      "Please refactor to a dictionary.\n")
                return error_dict
            else:
                return obj

    def tokenize_commands(self, parsed_input, temp_vars):
        """
        Recognizes command-types and associates input with those types.
        This is used to ensure that expected input-patterns are used.
        Inform the user of any invalid commands, and detect comments.
        :param parsed_input: (List - Strings): user input from the commands prompt.
        :return recognized_input (list - dicts) or bool: recognized_input if
            the all input is valid, False otherwise.
        """
        def generate_default_tokens(tokens):
            """
            Creates a Token for any default arguments NOT provided by the user.
            Makes validation easier when multiple lines are consolidated to a single line.
            :param tokens: list of tokenized input.
            :return lex: returns modified list of tokenized input.
            """
            default_types = {
                'int': 'INTEGER',
                'page': 'PAGE_ELEMENT',
                'arg': 'ARG_CMD',
                'arb': 'ARBITRARY_CMD'
            }
            if len(tokens) != 1 + len(tokens[0].args) + len(tokens[0].default_args):
                for e, token in enumerate(tokens):
                    if token.type in ['ASSERTION_CMD', 'GENERAL_CMD', 'PORTAL_CMD']:
                        if token.default_args:
                            for _e, (darg_name, darg_value) in enumerate(token.default_args.items()):
                                try:
                                    if tokens[e + len(token.args) + len(token.default_args)].type != 'ARG_CMD':
                                        tokens.insert(tokens.index(token) + len(token.args) + 1, Token(darg_value, 'ARG_CMD'))
                                except IndexError:
                                    tokens.append(Token(darg_value, default_types[darg_name.split('_')[1]]))
            return tokens

        def report_unrecognized_input(unrecognized_commands):
            """
            Prints out all unrecognized commands obtained during lexerization.
            :param unrecognized_commands:
            :return:
            """
            bad_commands = ["* {}".format(c) for c in unrecognized_commands]
            plural = 's' if len(unrecognized_commands) > 1 else ''
            raise UnrecognizedCommandException("Please review the command{0} for errors:\n{1}".format(plural, '\n'.join(bad_commands)))

        command_functions = {
            'ARG_CMD': {v: None for _, values in self.function_args.items() for v in values},
            'ASSERTION_CMD': self.assertion_commands,
            'GENERAL_CMD': self.general_commands,
            'PAGE_ELEMENT': self.current_page_commands,
            'PORTAL_CMD': self.portal_commands,
            'WINDOWED_ELEMENT': self.windowed_element_commands,
        }

        tokens, unrecognized_input = list(), list()
        for cmd in parsed_input:
            if isinstance(cmd, int):
                tokens.append(Token(cmd, 'INTEGER'))
            elif cmd.startswith('#'):
                break  # Ignore anything following the comment character ("#")
            elif cmd.startswith('"') and cmd.endswith('"'):
                tokens.append(Token(cmd[1:-1], 'ARBITRARY_CMD'))
            elif cmd in self.session_arguments.keys():
                tokens.append(Token(self.session_arguments[cmd], 'SESSION_ARG'))
            elif cmd in temp_vars.keys():
                tokens.append(Token(temp_vars[cmd], 'ARBITRARY_CMD'))
            else:
                for command_type, commands in command_functions.items():
                    if cmd.lower() in commands.keys():
                        tokens.append(
                            Token(cmd.lower(), command_type, commands[cmd.lower()])
                        )
                        break
                else:
                    unrecognized_input.append(cmd)

        if unrecognized_input:
            report_unrecognized_input(unrecognized_input)
            return False
        elif tokens:
            tokens = generate_default_tokens(tokens)
            return tokens
        elif not(tokens and unrecognized_input):
            return False
        else:
            return False  # Shouldn't ever be hit

    def run_command(self, valid_lex, session):
        """
        Fire off functions associated with the validated commands.
        """
        def get_token_values(tokens):
            return [t.name for t in tokens]

        cmd_map = {
            'ASSERTION_CMD': self.assertion_commands,
            'GENERAL_CMD': self.general_commands,
            'MACRO_CMD': self.macro_commands,
            'PORTAL_CMD': self.portal_commands
        }
        for command_group in valid_lex:

            # Log commands to a save file
            if session.__class__.__name__ == 'InteractiveSession':
                if session.save_enabled:
                    complete_command = ' '.join([tkn.name for tkn in command_group])
                    with open(session.save_file_path, 'a') as f:
                        f.write(complete_command)
                        f.write('\n')

            if command_group[0].type == 'GENERAL_CMD':
                token_values = get_token_values(command_group[1:])
                cmd_map[command_group[0].type][command_group[0].name](session, *token_values)
            elif command_group[0].type == 'PORTAL_CMD':
                cmd_map[command_group[0].type][command_group[0].name](session.portal.driver, session.current_page_object, *command_group[1:])
            elif command_group[0].type == 'MACRO_CMD':
                if command_group[1].name == '-h':
                    # [print(help_text) for help_text in command_group[0].help]
                    pass
                else:
                    cmd_map[command_group[0].type][command_group[0].name](session.portal, command_group[0].argument_type, *command_group[1:])
            elif command_group[0].type == 'ASSERTION_CMD':
                cmd_map[command_group[0].type][command_group[0].name](session.portal.driver, session.current_page_object, *command_group[1:])

    def set_current_page_commands(self, current_page_object):
        """
        Iterates through the current page's dict of commands to determine whether
        each element is currently visible or not. Invisible elements are visible
        once their containing window or drop-down menu has been opened.
        """
        self.current_page_commands = dict()
        for cmd, xpath in current_page_object.page_elements.items():
            self.current_page_commands[cmd] = xpath

        for window, elms in current_page_object.window_elements.items():
            for cmd, xpath in elms.items():
                self.current_page_commands[cmd] = xpath

    def set_static_commands(self, session=None):
        """
        Iterates through the Commands directory to import each module, and then
        each class from each module. Each non-special function found in the
        class is a key for it's function value in the commands dict.
        This prepares "static" commands: those that are always available, and
        will only need to be run once at the beginning of a session.
        :param session: Automated Session object
        """
        command_dicts = {
            'GeneralCommands': self.general_commands,
            'PortalCommands': self.portal_commands,
            'MacroCommands': self.macro_commands,
            'AssertionCommands': self.assertion_commands,
            'ArgumentCommands': self.session_arguments
        }
        root_dir = '\\'.join(os.path.realpath(__file__).split('\\')[:-2])
        cmds_dir = os.path.join(root_dir, 'Commands')
        for root, dirs, files in os.walk(cmds_dir):
            modules = [f[:-3] for f in files if f.endswith('py') and not f.startswith('__')]
            break  # Limit the walk to the root dir. and no sub-folders

        for module in modules:
            exec('import Commands.{0}'.format(module))
            classes = {
                c[0]: c[1] for c in inspect.getmembers(
                    eval('Commands.{0}'.format(module)), inspect.isclass
                ) if c[0] == module
            }
            for class_name, class_object in classes.items():
                functions = {
                    f[0]: f[1] for f in inspect.getmembers(
                        class_object, inspect.isfunction
                    ) if not (f[0].startswith('_') or f[0].endswith('_'))
                }
                for func_name, func_object in functions.items():
                    command_dicts[module].setdefault(func_name, func_object)
            self.function_args.update(eval('Commands.{0}.{0}.function_args'.format(module)))

        if hasattr(session, 'arg_commands'):
            self.session_arguments = session.arg_commands

    def set_visible_element_commands(self, portal, current_page_object):
        """
        Checks the current page for any commands which are unique to it or to any
        window/frame elements within it.
        :param portal: Portal object containing the web driver.
        :param current_page_object: Page object containing page-specific info.
        """
        self.windowed_element_commands = dict()  # Clear out any commands from the last call
        # Note that this happens before checking the attr. This ensures that we can switch
        # to a page which does not have this attr. without the previous attr. carrying over.

        if current_page_object.dynamic_elements:
            portal.driver.implicitly_wait(0)
            for directory, xpath_expression in current_page_object.dynamic_elements.items():

                # Handle multiple XPath expressions
                if isinstance(xpath_expression, list):
                    results = list()
                    try:
                        for exp in xpath_expression:
                            results.append(portal.driver.find_element_by_xpath(exp))
                    except NoSuchElementException:
                        pass  # We expect to hit this frequently while browsing the Viewer page.
                    except Exception:
                        traceback.print_exc()  # DBug: not sure what to expect from this until it is thoroughly tested
                    else:
                        if len(results) == len(xpath_expression):
                            text_results = [r.text for r in results]
                            path = os.path.join(current_page_object.__class__.__name__, directory.format(*text_results))
                            self.windowed_element_commands.update(self.get_windowed_element_commands(path))
                        else:
                            print("Unexpected number of elements found.")

                # Handle single XPath expressions
                elif isinstance(xpath_expression, str):
                    try:
                        result = portal.driver.find_element_by_xpath(xpath_expression)
                    except NoSuchElementException:
                        pass  # We expect to hit this frequently while browsing the Viewer page.
                    except Exception:
                        traceback.print_exc()  # DBug: not sure what to expect from this until it is thoroughly tested
                    else:
                        path = os.path.join(current_page_object.id, result.text)
                        self.windowed_element_commands.update(self.get_windowed_element_commands(path))
            portal.driver.implicitly_wait(portal.implicit_wait_amt)

    @staticmethod
    def parse_input(user_input):
        """
        Groups space-delimited input into separate commands.
        After removing spaces in execute_command(), arbitrary commands need to be
        rebuilt. This function will merge commands together into one command using
        quotation marks.
        Furthermore, integer-type input needs to be detected, so an attempt to
        convert all integers from str to int is made.
        :param user_input: (list - str) list of commands from the prompt
        :return: (list - str) parsed string-input with merged arbitrary commands.
        """
        parsed_input = list()
        substring_start = int()
        parse_substring = False

        # Gather arbitrary commands and all others
        for e, c in enumerate(user_input):
            if not parse_substring and c.startswith("'"):
                raise IllegalCharacterException("Double quotes only please, no single quotes allowed.")
            if parse_substring:
                if '"' in c:
                    substring = ' '.join(user_input[substring_start:e+1])
                    parsed_input.append(substring)
                    parse_substring = False
                else:
                    pass
            elif '"' in c:
                if c.count('"') % 2 == 0:
                    parsed_input.append(c)
                else:
                    parse_substring = True
                    substring_start = e
            else:
                parsed_input.append(c)

        # Convert all integer-str's to int and replace in output
        for e, token in enumerate(parsed_input):
            try:
                int_token = int(token)
            except ValueError:
                pass
            else:
                parsed_input[e] = int_token

        if parse_substring:
            raise InvalidPattern("Could not find matching double-quote for arbitrary command.")
        return parsed_input

    @staticmethod
    def validate_tokens(tokens_org):
        """
        Detects valid commands patterns before attempting to execute any found
        commands. If any sub-commands are incorrect, no commands are run,
        regardless of whether preceding sub-commands are valid. This helps
        reinforce user intent and maintain user orientation.
        :param tokens_org: lexerized user-input.
        :return list(tuples): validated tokens used to execute commands.
        """
        def validate_pattern(function, args, kwargs):
            """
            Compares the types of tokens (found in lex_values[1:]) to the types of arguments
            expected by the function (found in lex_values[0]).
            Expected Types: arb, int, page, and the prefix: default
            :param function: The function called by the user.
            :param args: Any required arguments provided by the user.
            :param kwargs: Any optional arguments provided by the user.
            :return: bool; True if the input types match the expected-argument types.
            """
            type_matches = {
                'ARBITRARY_CMD': 'arb',
                'ARG_CMD': 'arg',
                'SESSION_ARG': 'arb',
                'INTEGER': 'int',
                'PAGE_ELEMENT': 'page',
                'WINDOWED_ELEMENT': 'page',
                'GENERAL_CMD': None,
                'PORTAL_CMD': None,
                'ASSERTION_CMD': None
            }
            if not function.args and not function.kwargs:
                return True
            else:
                mismatch = dict()

                # Compare the required-argument requirements to the user's input
                expected_arg_pattern = [name.split('_')[0] for name in function.args]
                args_matchup = {z[0]: z[1].type for z in list(zip(expected_arg_pattern, args))}
                if not args_matchup:
                    raise MissingExpectedArgument('could not find expected argument for "{}"'.format(function.name))
                for expected, actual in args_matchup.items():
                    if expected == type_matches[actual]:
                        pass
                    else:
                        mismatch[expected] = actual

                # Compare the optional-argument requirements to the user's input
                expected_kwarg_pattern = [name.split('_')[1] for name in function.default_args]
                kwargs_matchup = {z[0]: z[1].type for z in list(zip(expected_kwarg_pattern, kwargs))}
                for expected, actual in kwargs_matchup.items():
                    if expected == type_matches[actual]:
                        pass
                    else:
                        mismatch[expected] = actual

                # Report input-pattern errors or return to continue parsing more commands
                if mismatch:
                    print("Invalid argument{1} found for {0} command:".format(function.name, 's' if len(mismatch) > 1 else ''))
                    for exp, act in mismatch.items():
                        print('  * Expected type {0}, found {1}'.format(exp, act))
                    raise InvalidPattern()
                else:
                    return True

        tokens = copy.copy(tokens_org)
        cmd_patterns = list()
        while tokens:
            if tokens[0].type not in ['ASSERTION_CMD', 'GENERAL_CMD', 'PORTAL_CMD']:
                raise InvalidPattern("{0} command found. Expected Assertion, General, or Portal command.".format(tokens[0].type))
            else:
                if tokens[0].args or tokens[0].default_args:
                    len_args = len(tokens[0].args)  # Get number of expected args
                    len_dargs = len(tokens[0].default_args)  # Get number of expected default_args

                    if validate_pattern(tokens[0], tokens[1:len_args+1], tokens[len_args+1:]):
                        cmd_patterns.append(tuple(tokens[:len_args + len_dargs + 1]))  # If valid, create tuple with function and all args
                        for i in range(len_args + len_dargs + 1):
                            try:
                                tokens.pop()  # Remove processed commands and move onto remaining commands
                            except IndexError:
                                raise MissingExpectedArgument('could not find expected argument for that command')
                else:
                    cmd_patterns.append((tokens[0],))
                    tokens.pop()
        else:
            return cmd_patterns


class Token:
    def __init__(self, name, token_type, func=None):
        """
        Class used to "tokenize" a command during parsing.
        This enables command validation later on.
        """
        self.args = list()
        self.default_args = dict()
        self.func = func
        self.kwargs = list()
        self.name = name
        self.type = token_type
        self.unpack_args = None
        self.unpack_kwargs = None

        if token_type in ['ASSERTION_CMD', 'GENERAL_CMD', 'PORTAL_CMD']:
            self.set_arg_attributes()

    def __repr__(self):
        """
        Makes Token-objects more readable while debugging.
        :return:
        """
        return '{0}: {1}'.format(self.type, self.name)

    def set_arg_attributes(self):
        """
        Sets argument-related attributes of a Token object.
        Note that the inspect module has no way to build an association between
        default arguments and their values, so we have to improvise a bit by
        assuming the reversed "args" and "defaults" properties can be zipped.
        """
        arg_spec = inspect.getfullargspec(self.func)

        self.args = [a for a in arg_spec.args if not a.startswith('default') and not a.startswith('_')]
        self.unpack_args = arg_spec.varargs
        self.unpack_kwargs = arg_spec.varkw

        if arg_spec.defaults:
            zipped = zip(reversed(arg_spec.args), reversed(arg_spec.defaults))
            self.default_args = {e[0]: e[1] for e in list(zipped)}
