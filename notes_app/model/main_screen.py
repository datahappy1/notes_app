class MainScreenModel:
    def __init__(self):
        self._c = 0
        self._d = 0
        self._sum = 0
        self._observers = []

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        self._c = value
        self._sum = self._c + self._d
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.model_is_changed()
