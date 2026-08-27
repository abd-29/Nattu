import hashlib
from pathlib import Path


def compute_file_hash(path: Path) -> str:
    """
    Compute the SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with path.open("rb") as file:

        while True:
            block = file.read(1024 * 1024)

            if not block:
                break

            sha256.update(block)

    return sha256.hexdigest()


if __name__ == "__main__":

    from config import DATA_DIR

    path = DATA_DIR / "raw" / "quality" / "QUA-INC-001_v3_2026.pdf"

    file_hash = compute_file_hash(path)

    print(path.name)
    print(file_hash)