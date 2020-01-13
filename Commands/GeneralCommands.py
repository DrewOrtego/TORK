import os
import sys
import time

sys.path.append([os.sep.join(os.getcwd().split(os.sep)[:-1]), 'Stuff'])


class GeneralCommands:
    """
    Abstract class containing functions for running harness-centric commands.
    """
    function_args = {
        'help': ['all', 'assertion', 'browser', 'general', 'page', 'window'],
    }

    @staticmethod
    def end_save(_session):
        """
        Ends a save session, if active.
        :param _session: Current session and its available commands.
        """
        if _session.save_enabled:
            _session.save_enabled = False
            _session.save_file_path = None
            _session.prompt = _session.prompt.replace('*', '')
            print('Save session ended.')
        else:
            print('A save session is not currently enabled.')

    @staticmethod
    def help(_session, default_arg_type='all'):
        """
        See InteractiveSession.InteractiveSession.help() function.
        :param _session: Current session and its available commands.
        :param default_arg_type: Indicates which commands to display (options found in function_args).
        """
        def print_each(iterable, space=''):
            for i in iterable:
                print("{0}{1}".format(space, i))

        if default_arg_type not in ['browser', 'general', 'assertion', 'page', 'window', 'all']:
            print("Did not recognize argument {0}. Printing all available commands...".format(default_arg_type))
            default_arg_type = 'all'

        if default_arg_type in ['page', 'all']:
            print("\nPage Commands:")
            print_each(sorted(list(_session.current_page_object.page_elements.keys())), '    ')
            if _session.current_page_object.window_elements:
                print("\nContained Elements:")
                for win_elm, elms in _session.current_page_object.window_elements.items():
                    print("*{0}{1}:".format('  ', win_elm))
                    print_each(sorted(list(elms.keys())), '    ')
            if _session.commands.windowed_element_commands:
                print("\nWindow Commands:")
                print_each(sorted(list(_session.commands.windowed_element_commands.keys())), '    ')

        if default_arg_type in ['window']:
            if _session.commands.windowed_element_commands:
                print("\nWindow Commands:")
                print_each(sorted(list(_session.commands.windowed_element_commands.keys())), '    ')
            else:
                print("\nNo windowed commands found. Check 'page' for other options.")

        if default_arg_type in ['general', 'all']:
            print("\nGeneral Commands:")
            print_each(sorted(list(_session.commands.general_commands.keys())), '    ')

        if default_arg_type in ['browser', 'all']:
            print("\nBrowser Commands:")
            print_each(sorted(list(_session.commands.portal_commands.keys())), '    ')

        if default_arg_type in ['assertion', 'all']:
            print("\nAssertion Commands:")
            print_each(sorted(list(_session.commands.assertion_commands.keys())), '    ')

        print("\n")

    @staticmethod
    def pause(_session):
        """
        Stops until the user preses the ENTER key (making this funciton platform-agnostic).
        Useful in automated mode as a way of pausing a test, interacting with the browser,
        and then starting the test again.
        :param _session: test session object.
        """
        input("Press ENTER to continue...")

    @staticmethod
    def prompt(_session, arb_text):
        """
        Allows user to change the prompt character from the default.
        :param _session: Current session and its available commands.
        :param arb_text: token object containing the text to use as the new prompt.
        """
        _session.prompt = '{0} '.format(arb_text.name.strip('"'))

    @staticmethod
    def save(_session, arb_file_name):
        """
        Enables the save session after verifying file i/o. This begins saving
        interactively-entered commands into  the specified file. Makes automated
        testing easier, assuming the commands are valid.
        :param _session: Current session and its available commands.
        :param arb_file_name: contains name of the file which the commands will written to.
        :return bool, str: True indicates the file was created, otherwise False. The str
            contains the full path to the save file so that subsequent commands can be written
            to it.
        """

        def check_extension(filename):
            """
            If not already provided, append the .txt file extension
            :param filename: user-provided filename or path
            :return: modified filename
            """
            if not filename.endswith('.txt'):
                return '{}.txt'.format(filename)
            else:
                return filename

        def get_full_path(full_filename):
            """
            Verify whether the user provided a full file path or not
            :param full_filename: file or full file path with .txt ext.
            :return: The full file path if the directory exists, otherwise False.
            """
            if len(full_filename.split(os.sep)) > 1:
                # Prevents someone from writing to a specified directory
                print("Invalid file name! Do not use separators in the file name.")
                return False
            else:
                dir_path = os.path.join(
                    os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]),
                    'SavedSessions'
                )
                full_file_path = os.sep.join([dir_path, full_filename])
                if os.path.exists(full_file_path):
                    print("File already exists: {}".format(full_file_path))
                    return False
                else:
                    return full_file_path

        if _session.save_enabled:
            print('A save session is already enabled.')
        else:
            file_name = arb_file_name
            filename_with_ext = check_extension(file_name)
            full_path = get_full_path(filename_with_ext)
            if full_path:
                with open(full_path, 'a') as f:
                    f.close()
                print("Created file {0}".format(full_path))
                _session.save_enabled, _session.save_file_path, _session.prompt = True, full_path, '*{}'.format(_session.prompt)
            else:
                _session.save_enabled, _session.save_file_path = False, ''

    @staticmethod
    def sleep(_, int_time):
        """
        Tells the program to wait for n-number of seconds. Literally sleeps.
        :param int_time: amount of seconds to sleep.
        """
        try:
            time.sleep(int_time)
        except Exception as err:
            print(err)

    @staticmethod
    def try_start(_session):
        """
        Starts "try mode" which ignores exceptions.
        This allows for portal-unique commands to coexist with non-unique commands.
        E.g. A test file can include the "extra" workflow needed for AGOL, and
        then turn off "try mode" for commands that it shares with Portal.
        :param _session: Session object.
        """
        if _session.try_mode:
            print("Try mode is already active. To disable, use: try_stop.")
        else:
            _session.try_mode = True

    @staticmethod
    def try_stop(_session):
        """
        Disables "try mode" after try_start has been run.
        :param _session: Session object.
        """
        if not _session.try_mode:
            print("Try mode is already inactive. To enable, use: try_start.")
        else:
            _session.try_mode = False

    @staticmethod
    def quit(_):
        """
        Exits the program. Same as "exit".
        """
        sys.exit()

    @staticmethod
    def xyzzy(_):
        print('A hollow voice says, "Quit playing around, this isn\'t a game!"')
