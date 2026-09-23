import shutil
from pathlib import Path


def flatten_directory(target_dir: str | Path):
    target = Path(target_dir).resolve()

    # Iterate over all items in all subdirectories
    for item in list(target.rglob("*")):
        # Only process files that are inside subdirectories, not already in the target
        if item.is_file() and item.parent != target:
            dest = target / item.name

            # Handle duplicate filenames to prevent accidental overwrites
            counter = 1
            while dest.exists():
                dest = target / f"{item.stem}_{counter}{item.suffix}"
                counter += 1

            shutil.move(str(item), str(dest))
            print(f"Moved: {item} -> {dest}")



if __name__ == "__main__":
    # Replace with your target folder path
    flatten_directory(r"C:\Users\dolph\Downloads\Combined\Combined\Third_checked\P25_7.2slices")