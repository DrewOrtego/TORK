def lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property


class ControlBase(object):
    def __init__(self, element):
        self.element = element
        self.dijit_parent_element = self.get_dijit_parent(element)

    def get_dijit_parent_from_child(self, element):
        try:
            parent = element.find_element_by_xpath('..')
            if "dijit" not in parent.get_attribute("class").split(" "):
                parent = self.get_dijit_parent_from_child(parent)
            return parent
        except:
            raise Exception("Did not find the dijit parent element from dijit child control.")

    def get_dijit_parent(self, element):
        try:
            class_attrs = element.get_attribute("class").split(" ")
            if "dijit" in class_attrs:
                # If the control is already a dijit parent, directly return
                return element
            elif any("dijit" in x for x in class_attrs):
                # If control has dijit as part of the class attribute, then it has a dijit parent. 
                # Recursively seach all the way up to find the dijit parent.
                # This relies on the XPath for a control points to an element that has dijit as part of the class attribute. 
                # If someone uses a tr for XPath, it might not have this class attribute and this will not work.
                return self.get_dijit_parent_from_child(element)
            else:
                 # If control is not using a dijit template at all, then the dijit parent is None.
                return None
        except:
            return None
    
    @lazy_property
    def enabled(self):
        try:
            # If element has a dijit parent, then use the dijit parent to get the enabled status. 
            # Otherwise use the element itself to get the enabled status.
            element = self.element if self.dijit_parent_element is None else self.dijit_parent_element
            if element.is_enabled() and "Disabled" not in element.get_attribute("class"):
                return True
        except:
            raise Exception("Could not check enabled status for: {}".format(self.element.name))
        return False

    @lazy_property
    def visible(self):
        try:
            return self.element.is_displayed()
        except:
            raise Exception("Could not check visible status for: {}".format(self.element.name))

    @lazy_property
    def clickable(self):
        return self.enabled and self.visible

