from pathlib import Path


def rm_tree(pth: Path) -> None:
    """https://stackoverflow.com/questions/50186904/pathlib-recursively-remove-directory
    Removes all content of a directory recursively but not the directory itself"""
    if not pth.exists():
        print(f"{pth} does not exist, creating it")

        pth.mkdir(parents=True)
        return

    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)

    # pth.rmdir()


def main(path: str | Path) -> None:
    if isinstance(path, str):
        path = Path(path)

    rm_tree(path)


if __name__ == "__main__":
    print("This script is not meant to be run directly.")
