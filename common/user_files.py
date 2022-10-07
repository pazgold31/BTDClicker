from pathlib import Path

import appdirs


def get_files_dir() -> Path:
    path = Path(appdirs.user_data_dir(roaming=True)) / "BTDClicker"
    if not path.exists():
        path.mkdir()
    return path


def get_knowledge_images_dir(subdirectory: str = "") -> Path:
    path = get_files_dir() / "KnowledgePictures" / subdirectory
    if not path.exists():
        path.mkdir(parents=True)
    return path
