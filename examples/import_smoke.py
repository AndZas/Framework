"""Run after installing the package: python examples/import_smoke.py."""

import framework


def main() -> None:
    print(f"Imported {framework.__name__} successfully.")


if __name__ == "__main__":
    main()
