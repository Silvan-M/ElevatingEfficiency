from debug import Debug as DB


class Delegate:
    """
    Handles the delegation of events to listeners

    :param listeners: The listeners to add
    :type listeners: list
    """


    def __init__(self):
        self.listeners = []

    def __str__(self) -> str:
        return DB.str(
            "Class",
            "Delegate",
            kwargs=[
                self.listeners],
            desc=["listeners"])

    def add_listener(self, listener):
        """
        Add a listener to the delegate

        :param listener: The listener to add
        :type listener: function
        """
        self.listeners.append(listener)

    def remove_listener(self, listener):
        """
        Remove a listener from the delegate
        
        :param listener: The listener to remove
        :type listener: function
        """
        self.listeners.remove(listener)

    def notify_all(self, *args, **kwargs):
        """
        Notify all listeners of the delegate

        :param args: The arguments to pass to the listeners
        :type args: list
        :param kwargs: The keyword arguments to pass to the listeners
        :type kwargs: dict        
        """
        for listener in self.listeners:
            listener(*args, **kwargs)
