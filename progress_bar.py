import sys
import time


class ProgressBar:
    """
    A simple progress bar

    :param total: The total amount of steps
    :type total: int
    :param prefix: The prefix to display
    :type prefix: str
    :param size: The size of the progress bar
    :type size: int
    :param out: The output stream
    :type out: file
    """

    def __init__(self, total, prefix="", size=60, out=sys.stdout):
        self.total = total
        self.prefix = prefix
        self.size = size
        self.out = out
        self.start_time = time.time()
        self.current_count = 0

    def show(self):
        """
        Shows the progress bar

        :return: The current count
        """
        self.start_time = time.time()
        self.update(start=True)

    def update(self, start=False):
        """
        Displays or updates a console progress bar.

        :param start: Whether this is the first time the progress bar is being displayed
        """
        if not start:
            self.current_count += 1

        x = int(self.size * self.current_count / self.total)
        remaining = ((time.time() - self.start_time) / max(1,
                                                           self.current_count)) * (self.total - self.current_count)

        mins, sec = divmod(remaining, 60)
        time_str = f"{int(mins):02}:{sec:05.2f}"
        end = "\n" if self.current_count == self.total else "\r"

        print(
            f"{self.prefix}[{'█' * x}{'.' * (self.size - x)}] {self.current_count}/{self.total} Est wait {time_str}",
            end=end,
            file=self.out,
            flush=True)

        return self.current_count
