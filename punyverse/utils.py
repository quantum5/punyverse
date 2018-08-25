class cached_property(object):
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or func.__name__
        self.__doc__ = getattr(func, '__doc__')

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        result = instance.__dict__[self.name] = self.func(instance)
        return result

    def __set__(self, instance, value):
        if value is None:
            if self.name in instance.__dict__:
                del instance.__dict__[self.name]
        else:
            instance.__dict__[self.name] = value
