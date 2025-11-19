#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autor: Sandor Miguel Cruz Jiménez
"""

from pathlib import Path
import tempfile
import os
import shutil
from typing import Union, IO, Any, Optional

PathLike = Union[str, Path]


# -------------------
# Utilidades internas
# -------------------

def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _fsync_file(fobj: IO[Any]) -> None:
    try:
        fobj.flush()
    except Exception:
        pass
    try:
        os.fsync(fobj.fileno())
    except Exception:
        pass


def _fsync_folder(folder: Path) -> None:
    try:
        fd = os.open(str(folder), os.O_RDONLY)
    except Exception:
        return
    try:
        os.fsync(fd)
    except Exception:
        pass
    finally:
        try:
            os.close(fd)
        except Exception:
            pass


def _replace_atomic(src: Path, dst: Path, fsync_dir: bool) -> None:
    try:
        if src.resolve() == dst.resolve():
            return
    except Exception:
        pass

    try:
        os.replace(str(src), str(dst))  # Para Windows/Linux
    except Exception:
        shutil.move(str(src), str(dst))  # fallback

    if fsync_dir:
        _fsync_folder(dst.parent)


# -------------------------
# API pública
# -------------------------

def write_atomic(
    path: PathLike,
    data: Union[str, bytes],
    fsync: bool = True,
    encoding: str = "utf-8",
) -> None:
    """
    Si `data` es str, se codifica automáticamente a UTF-8 (o la codificación dada).
    """
    path = Path(path)
    
    if isinstance(data, str):
        data = data.encode(encoding)

    _ensure_parent(path)

    fd = None
    tmpp = None
    try:
        fd, tmpp = tempfile.mkstemp(dir=str(path.parent))
        with os.fdopen(fd, "wb") as f:
            fd = None
            f.write(data)
            if fsync:
                _fsync_file(f)

        _replace_atomic(Path(tmpp), path, fsync_dir=fsync)
        tmpp = None

    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass

        if tmpp is not None:
            try:
                os.unlink(tmpp)
            except Exception:
                pass


def write_text_atomic(
    path: PathLike,
    text: str,
    encoding: str = "utf-8",
    fsync: bool = True
) -> None:
    """
    Convenience wrapper para escribir texto directamente.
    """
    write_atomic(path, text.encode(encoding), fsync=fsync)


def write_from_file(
    path: PathLike,
    source: PathLike,
    fsync: bool = True,
    chunk_size: int = 1 << 20,
) -> None:
    """
    Copia el contenido de un archivo a otro 
    Útil para ficheros grandes (usa chunks).
    """
    path = Path(path)
    _ensure_parent(path)

    fd = None
    tmpp = None
    try:
        fd, tmpp = tempfile.mkstemp(dir=str(path.parent))
        with os.fdopen(fd, "wb") as out_f:
            fd = None
            with open(str(source), "rb") as in_f:
                while True:
                    chunk = in_f.read(chunk_size)
                    if not chunk:
                        break
                    out_f.write(chunk)
            if fsync:
                _fsync_file(out_f)

        _replace_atomic(Path(tmpp), path, fsync_dir=fsync)
        tmpp = None

    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass
        if tmpp is not None:
            try:
                os.unlink(tmpp)
            except Exception:
                pass


def remove_safe(path: PathLike) -> None:
    try:
        os.unlink(str(path))
    except FileNotFoundError:
        pass
    except IsADirectoryError:
        try:
            os.rmdir(str(path))
        except Exception:
            pass
    except Exception:
        pass


# -------------------------
# Writer incremental
# -------------------------

class SimpleWriter:
    """
    Context manager para escritura incremental
    Escribe en un temporal y reemplaza al cerrar si no hubo errores.
    """

    def __init__(self, path: PathLike, mode: str = "wb", fsync: bool = True):
        self.path = Path(path)
        self.mode = mode
        self.fsync = fsync
        self._tmpp: Optional[str] = None
        self._fd: Optional[int] = None
        self._file: Optional[IO[Any]] = None

    def __enter__(self) -> IO[Any]:
        _ensure_parent(self.path)
        self._fd, self._tmpp = tempfile.mkstemp(dir=str(self.path.parent))
        self._file = os.fdopen(self._fd, self.mode)
        self._fd = None
        return self._file

    def __exit__(self, exc_type, exc, tb) -> Optional[bool]:
        try:
            if self._file is not None:
                try:
                    # fsync en modos write/append
                    if self.fsync and any(m in self.mode for m in "wax"):
                        _fsync_file(self._file)
                    self._file.close()
                except Exception:
                    pass

            if exc_type is None and self._tmpp is not None:
                _replace_atomic(Path(self._tmpp), self.path, fsync_dir=self.fsync)
                self._tmpp = None

        finally:
            if self._tmpp is not None:
                try:
                    os.unlink(self._tmpp)
                except Exception:
                    pass

        return False  # No suprimir excepciones
