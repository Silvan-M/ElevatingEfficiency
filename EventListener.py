class EventListener:
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def notify_all(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)