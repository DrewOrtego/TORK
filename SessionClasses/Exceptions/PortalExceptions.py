class ElementNotFoundException(Exception):
    def __init__(self, item_name):
        m = 'Item {0} not found'.format(item_name)
        print(m)


class InvalidBrowserNameException(Exception):
    def __init__(self):
        m = "Invalid browser name provided, please choose a valid browser"
        print(m)


class InvalidPasswordException(Exception):
    def __init__(self):
        m = "Invalid password provided, please enter a password without spaces"
        print(m)


class InvalidURLException(Exception):
    def __init__(self):
        m = "Invalid URL format provided, please include a valid URL"
        print(m)


class InvalidUsernameException(Exception):
    def __init__(self):
        m = "Invalid username provided, please enter a username with no spaces"
        print(m)


class ItemNotFoundException(Exception):
    def __init__(self, item_name, drop_down_name):
        m = 'Item "{0}" not found in menu "{1}"'.format(item_name, drop_down_name)
        print(m)


class SearchResultException(Exception):
    def __init__(self, m):
        pass


class UnrecognizedBrowserException(Exception):
    def __init__(self, browser_name):
        m = 'Unexpected browser found: {0}'.format(browser_name)
        print(m)
