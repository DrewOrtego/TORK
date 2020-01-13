"""
Configuration for the Creating Page Objects and Commands, and Generating Test Report tutorial.

Manages configuration settings for automated sessions. Initiates a test session.

EXPECTED ARGUMENTS
Interactive Session: -i (optional params: <browser name> <portal url> <username> <password>)
Automated Session: -a (params are set below)

Parameter Details
    * = accepted options
    ! = note

1. assertion_level: (list - strings) level of test files to run.
    * 'sanity'
    * 'release'
2. verbose: (bool) amount of messaging to print to the console. True prints the most info, False prints the least.
3. log_file_dir: (string) path to the folder where you'd like to create log files.
4. test_file_dir: (string) path to the folder which contains the test files.
    ! This can be found here: https://devtopia.esri.com/andr7495/Portal-UI-Test-Files
5. parameters: (dictionary) contains the first URL a session will access, plus optional arguments.
    ! Each dictionary here is used to run an individual test session.
    ! The 'endpoint' key is required, and 'args' is optional.
    ! If you populate the 'args' value, each element in the list is available via commands 'arg_0', 'arg_1', etc. Use these in test files.
6. browsers: (list - strings) names of browsers to test. (Case-insensitive.)
    * 'FireFox'
    * 'Chrome'
7. selected_test_files: (list - strings) the only test files to run during the test session.
    ! If populated, these will be the ONLY test files used; the 'tasks' dictionary is completely ignored.
    ! The harness will only pick up files with the .txt file extensions.
    ! The .txt extension is not required in the file-name you provide to this list.
8. database: (string) path to the database location.
    * any object which is equivalent to False, or the path to create a new database, or path to an existing database.
    ! If a string is provided, it must be an existing path.
    ! The framework will not attempt to create or update any database whose path does not exist.
9. tasks: (dictionary) folder structure to follow when parsing for test files.
    * The minimum required options are the tool categories (Standard, Raster, GA).
    ! The list for each category is optional. If blank, all folders in the category will run. Otherwise, only those included will run.
    ! Note that selected_test_files will override these settings.
"""

import os
import sys

if sys.argv[1].lower() not in ['-a', '-i']:
    print("ERROR: Missing argument for Automated (-a) or Interactive (-i) Mode.")

elif sys.argv[1].lower() == '-i':
    from SessionClasses.InteractiveManager import InteractiveSession
    InteractiveSession()

elif sys.argv[1].lower() == '-a':
    from SessionClasses.AutomatedManager import AutomatedSession
    parameters = {
        'IMDb_Tutorial': {'endpoint': 'https://www.imdb.com/', 'args': []}
    }
    AutomatedSession(
        assertion_levels=['sanity'],
        verbose=False,
        log_file_dir=r'C:\UI-log',
        test_file_dir=os.path.join(os.getcwd(), os.pardir, 'Portal-UI-Test-Files'),
        parameters=parameters,
        browsers=['firefox'],
        selected_test_files=[

        ],
        database=r'C:\ui-databases\IMDbTest.db',
        tasks={
            'Tutorial': [
                'IMDb'
            ]
        }
    )
