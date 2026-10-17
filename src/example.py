"""Small CLI used to demonstrate acceptance, packaging and releases."""

import argparse


def greet(name):
    clean = name.strip()
    if not clean:
        raise ValueError("A name is required")
    return f"Hello, {clean}!"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()
