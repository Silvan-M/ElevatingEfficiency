import sys
import time

class ProgressBar:
    def __init__(self, total, prefix="", size=60, out=sys.stdout):
        self.total = total
        self.prefix = prefix
        self.size = size
        self.out = out
        self.start_time = time.time()
        self.current_count = 0

    def update(self):
        self.current_count += 1
        x = int(self.size * self.current_count / self.total)
        remaining = ((time.time() - self.start_time) / self.current_count) * (self.total - self.current_count)

        mins, sec = divmod(remaining, 60)
        time_str = f"{int(mins):02}:{sec:05.2f}"

        print(
            f"{self.prefix}[{'█' * x}{'.' * (self.size - x)}] {self.current_count}/{self.total} Est wait {time_str}",
            end='\r', file=self.out, flush=True
        )

        return self.current_count


