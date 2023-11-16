from Debug import Debug as DB

class EventListener:
    def __init__(self):
        self.listeners = []
    def __str__(self) -> str:
        return DB.str("Class","EventListener",kwargs=[self.listeners],desc=["listeners"])


    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def notify_all(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)