from importlib import import_module
from os import environ as env
from dotenv import load_dotenv
import sys
import logging
import traceback

load_dotenv()
debug_mode = True if env.get("DEBUG") == "yes" else False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.root.setLevel(logging.DEBUG if debug_mode else logging.INFO)


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
