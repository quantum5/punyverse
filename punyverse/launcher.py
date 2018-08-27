import os
import shutil
import sys


def main():
    if os.name != 'nt':
        print('Not on Windows. Nothing to do.')
        return

    source_dir = os.path.dirname(__file__)
    dest_dir = os.path.join(sys.prefix, 'Scripts')

    launcher_exe = os.path.join(source_dir, 'launcher.exe')
    launcherw_exe = os.path.join(source_dir, 'launcherw.exe')
    punyverse_exe = os.path.join(dest_dir, 'punyverse.exe')
    punyversew_exe = os.path.join(dest_dir, 'punyversew.exe')
    assert os.path.isfile(launcher_exe)
    assert os.path.isfile(launcherw_exe)
    assert os.path.isfile(punyverse_exe)
    assert os.path.isfile(punyversew_exe)

    def copy(src, dst):
        print('Copying %s to %s...' % (src, dst))
        shutil.copy(src, dst)
    copy(launcher_exe, punyverse_exe)
    copy(launcherw_exe, punyversew_exe)


if __name__ == '__main__':
    main()
