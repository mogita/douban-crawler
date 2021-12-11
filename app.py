from importlib import import_module
import sys
import logging
import traceback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.root.setLevel(logging.INFO)


def main():
    sys.argv.pop(0)
    if len(sys.argv) < 1:
        raise ValueError("Too few arguments")

    action = sys.argv[0]
    rest_args = sys.argv[1:]

    try:
        task = import_module(".".join(["src", action]))
    except:
        traceback.print_exc()
        exit(1)

    if len(rest_args) > 0:
        task.main(rest_args)
    else:
        task.main()


if __name__ == "__main__":
    main()
