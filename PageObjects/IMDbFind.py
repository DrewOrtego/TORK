class IMDbFind:
    """
    IMDb results page; used in the Wiki's Page Object tutorial
    """
    def __init__(self):
        self.id = 'https://www.imdb.com/find'
        self.wait_element = '//div[@class="recently-viewed"]'
        self.wait_method = 'visible'

        self.dynamic_elements = {

        }

        self.frame_elements = {

        }

        self.page_elements = {
            'result-titles': '(//div[@id="main"]//div[@class="findSection"])[1]'
        }

        self.window_elements = {

        }
