#!/usr/bin/env python
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    try:
        if sys.argv[1] == "test":
            if len(sys.argv) == 2:
                sys.argv.append("../..")
            elif len(sys.argv) == 3:
                sys.argv[2] = f"../../{sys.argv[2]}"
    except IndexError:
        pass

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
