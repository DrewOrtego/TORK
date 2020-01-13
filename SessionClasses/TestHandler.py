import os


class TestHandler:
    def __init__(self, selected_test_files, test_file_dir, assertion_level, tasks):
        """
        Manages validation of test-file paths and reporting.
        :param selected_test_files: list of exclusive file names to be tested
        :param test_file_dir: root directory for the test files
        :param assertion_level: sanity or release-- each navigates to different files
        :param tasks: (dict) tool categories and names used to get their corresponding folder
        """
        self.selected_test_files = selected_test_files
        self.test_file_dir = test_file_dir
        self.assertion_level = assertion_level
        self.tasks = tasks

        self.invalid_files = None

        # self.invalid_files = self.get_invalid_files()
        # ToDo Check for invalid files. Removed for now due to bug.
        # ToDo Enforce unique file names amongst Tool Categories

    # def get_invalid_files(self):
    #     """
    #     Iterates through all the test files in a given path to verify that main.py
    #     has provided existing data paths.
    #     If selected_test_files is used, compare files names provided against
    #     all file names in test folders.
    #     If not, construct paths with the given parameters and only check for
    #     expected folder names. All the tests in those folders will be run.
    #     """
    #     invalid_paths = dict()
    #     if self.selected_test_files:
    #         all_files = [
    #             os.path.join(root, f) for root, dirs, files in
    #             os.walk(self.test_file_dir) for f in
    #             files if f.endswith('.txt')
    #         ]
    #         for test_file_path in self.selected_test_files:
    #             if test_file_path in all_files:
    #                 pass
    #             else:
    #                 invalid_paths.setdefault('InvalidPaths', list())
    #                 invalid_paths['InvalidPaths'].append(test_file_path)
    #         del all_files
    #     else:
    #         if self.tasks:
    #             for tool_category, tools in self.tasks.items():
    #                 if tools:
    #                     for tool in tools:
    #                         path = os.path.join(
    #                             self.test_file_dir, self.assertion_level, tool_category, tool
    #                         )
    #                         if not os.path.exists(path):
    #                             invalid_paths.setdefault(tool_category, list())
    #                             invalid_paths[tool_category].append(path)
    #                 else:
    #                     invalid_paths.setdefault(tool_category, 'No tool-name folders were specified.')
    #         else:
    #             invalid_paths.setdefault('Error', '"tasks" is empty in main.py, cannot load test files.')
    #     return invalid_paths

    def get_next_test_file(self):
        """
        Iterates over test-file dir. to find test files.
        Prevents need for saving all test-files in memory.
        :yield (str) path to current test file.
        """
        if self.selected_test_files:
            for root, dirs, files in os.walk(self.test_file_dir):
                for f in filter(lambda fi: fi.endswith('.txt'), files):
                    if f in self.selected_test_files:
                        yield os.path.join(root, f), root.split(os.sep)[-2], root.split(os.sep)[-1]
        elif self.tasks:
            for analysis_type, tools in self.tasks.items():
                if tools:
                    for tool in tools:
                        test_path = os.path.join(
                            self.test_file_dir, self.assertion_level, analysis_type, tool
                        )
                        if os.path.exists(test_path):
                            for root, dirs, files in os.walk(test_path):
                                for f in filter(lambda fi: fi.endswith('.txt'), files):
                                    yield os.path.join(root, f), analysis_type, tool
                        else:
                            print("WARNING! Test file directory does not exist: {0}".format(test_path))
                else:
                    test_path = os.path.join(
                        self.test_file_dir, self.assertion_level, analysis_type
                    )
                    if os.path.exists(test_path):
                        for root, dirs, files in os.walk(test_path):
                            for f in filter(lambda fi: fi.endswith('.txt'), files):
                                yield os.path.join(root, f), analysis_type, f
                    else:
                        print("WARNING! Test file directory does not exist: {0}".format(test_path))
        else:
            print("No tools specified for testing: please populate the 'tasks' dictionary in main.py.")
