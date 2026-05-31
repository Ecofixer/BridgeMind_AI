"""File I/O utilities."""

from pathlib import Path


def ensure_dir(path: Path | str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_text(path: Path | str, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)


def write_text(path: Path | str, content: str, encoding: str = "utf-8") -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    target.write_text(content, encoding=encoding)
    return target


def file_exists_and_nonempty(path: Path | str) -> bool:
    target = Path(path)
    return target.is_file() and target.stat().st_size > 0
