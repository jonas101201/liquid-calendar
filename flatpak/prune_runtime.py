"""Keep the BaseApp runtime bindings used by the calendar, without build tools."""
from pathlib import Path
import shutil
import sys

KEEP={'QtCore','QtGui','QtWidgets','QtQml','QtQuick','QtQuickControls2','QtQuickWidgets','QtNetwork','QtDBus','QtOpenGL','QtSvg','QtTest'}
def remove(path):
    if path.is_symlink() or path.is_file():path.unlink()
    elif path.is_dir():shutil.rmtree(path)
def prune(prefix):
    prefix=Path(prefix)
    for path in (prefix/'lib').glob('libLLVM*'):remove(path)
    for path in (prefix/'lib').glob('libclang*'):remove(path)
    for site in (prefix/'lib').glob('python*/site-packages'):
        for pattern in ['numpy*','OpenGL','pyopengl*','build','build-*.dist-info','packaging','packaging-*.dist-info','pyproject_hooks*','distro*','shiboken6_generator*','patchelf*']:
            for path in site.glob(pattern):remove(path)
        pyside=site/'PySide6'
        for path in pyside.glob('Qt*.abi3.so'):
            if path.name.split('.')[0] not in KEEP:remove(path)
        for pattern in ['*.pyi','include','typesystems','glue','scripts','doc','Qt','__pycache__']:
            for path in pyside.glob(pattern):remove(path)
    for path in prefix.rglob('__pycache__'):remove(path)
    for path in prefix.glob('cleanup-BaseApp*.sh'):remove(path)
    remove(prefix/'share/metainfo/io.qt.PySide.BaseApp.metainfo.xml')
if __name__=='__main__':prune(sys.argv[1])
