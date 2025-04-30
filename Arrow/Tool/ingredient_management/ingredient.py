
class Ingredient:
    """
    a template base class
    """
    def init(self):
        raise NotImplementedError

    def body(self):
        raise NotImplementedError

    def final(self):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__  # Return the name of the class


