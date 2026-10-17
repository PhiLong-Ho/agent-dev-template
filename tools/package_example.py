"""Package only the reference source; replace for your project stack."""

import argparse
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        args.output / f"example-{args.version}.zip", "x", zipfile.ZIP_DEFLATED
    ) as bundle:
        for path in sorted(Path("src").glob("*.py")):
            bundle.write(path, path.as_posix())


if __name__ == "__main__":
    main()
