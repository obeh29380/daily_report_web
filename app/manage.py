import argparse
from importlib import import_module


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("command")

    args = parser.parse_args()

    module = import_module(f"command.{args.command}")
    module.main()
