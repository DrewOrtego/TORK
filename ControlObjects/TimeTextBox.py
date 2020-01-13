from ControlObjects.ControlBase import ControlBase

class TimeTextBox(ControlBase):
    def __init__(self, element):
        ControlBase.__init__(self, element)

    @property
    def Items(self, element):
        '''Should return items of timetextbox dropdown box
        
        Arguments:
            element {} -- element
        '''
        pass