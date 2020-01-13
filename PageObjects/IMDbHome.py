class IMDbHome:
    """
    IMDb homepage; used in the Wiki's Page Object tutorial
    """
    def __init__(self):
        self.id = 'https://www.imdb.com/'
        self.wait_element = '//input[@id="navbar-query"]'
        self.wait_method = 'visible'

        self.page_elements = {
            'search-bar': '//input[@id="navbar-query"]',
            'search-button': '//button[@id="navbar-submit-button"]'
        }

        self.dynamic_elements = {

        }

        self.window_elements = {

        }

        self.frame_elements = {

        }
