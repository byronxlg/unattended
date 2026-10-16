"""Swap a fully validated directory in one filesystem operation."""
import ctypes
import os
from pathlib import Path
import shutil
import sys


def replace_directory(staged, destination):
    staged, destination = Path(staged), Path(destination)
    if destination.is_symlink():
        raise ValueError('UNSAFE_OUTPUT_PATH')
    if not destination.exists():
        os.rename(staged, destination)
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == 'darwin':
        result = libc.renamex_np(os.fsencode(staged), os.fsencode(destination), 2)
    elif sys.platform == 'linux':
        result = libc.renameat2(-100, os.fsencode(staged), -100, os.fsencode(destination), 2)
    else:
        raise OSError('ATOMIC_DIRECTORY_EXCHANGE_REQUIRED')
    if result:
        raise OSError(ctypes.get_errno(), 'atomic directory exchange failed')
    shutil.rmtree(staged)
