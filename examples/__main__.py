import sys

from wexample_helpers.classes.example.executor import Executor

if __name__ == "__main__":
    Executor(
        entrypoint_path=__file__,
        filters=sys.argv[1:],
    ).execute()
