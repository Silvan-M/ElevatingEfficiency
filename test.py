import sys
import time

def print_progress_bar(current, max_value, bar_length=50):
    progress = current / max_value
    block = int(round(bar_length * progress))
    progress_bar = "[" + "=" * block + " " * (bar_length - block) + "]"
    sys.stdout.write("\rProgress: [{}] {:.2%}".format(progress_bar, progress))
    sys.stdout.flush()

def main(max_value):
    for i in range(max_value + 1):
        print_progress_bar(i, max_value)
        time.sleep(0.1)  # Simulate some work being done


