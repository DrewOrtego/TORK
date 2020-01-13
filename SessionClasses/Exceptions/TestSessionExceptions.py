class UnknownPageError(Exception):
    def __init__(self, current_url):
        """
        Raised when a session cannot recognize the current url
        """
        m = 'Couldn\'t locate any PageObject abbreviation in the url "{0}";' \
            ' The page is unrecognized by the test session.'.format(current_url)
        print(m)


class UnknownPageObjectWaitMethod(Exception):
    def __init__(self, page_object_name, key):
        """
        Raised when a PageObject's wait_method attr. is unrecognized
        :param key:
        """
        m = 'Unrecognized wait-method "{0}" found in PageObject "{1}"'.format(
            key, page_object_name
        )
        print(m)
