# -*- mode: python -*-
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks
from kivymd.icon_definitions import md_icons


# From http://bitstream.io/packaging-and-distributing-a-kivy-application-on-linux.html
def filter_binaries(all_binaries):
    '''Exclude binaries provided by system packages, and rely on .deb dependencies
    to ensure these binaries are available on the target machine.


    We need to remove OpenGL-related libraries so we can distribute the executable
    to other linux machines that might have different graphics hardware. If you
    bundle system libraries, your application might crash when run on a different
    machine with the following error during kivy startup:


    Fatal Python Error: (pygame parachute) Segmentation Fault


    If we strip all libraries, then PIL might not be able to find the correct _imaging
    module, even if the `python-image` package has been installed on the system. The
    easy way to fix this is to not filter binaries from the python-imaging package.


    We will strip out all binaries, except libpython2.7, which is required for the
    pyinstaller-frozen executable to work, and any of the python-* packages.
    '''


    print('Excluding system libraries')
    import subprocess
    excluded_pkgs  = set()
    excluded_files = set()
    whitelist_prefixes = ('libpython3.8', 'python-', 'python3-')
    binaries = []


    for b in all_binaries:
        try:
            output = subprocess.check_output(['dpkg', '-S', b[1]], stderr=open('/dev/null'))
            p, path = output.split(':', 2)
            if not p.startswith(whitelist_prefixes):
                excluded_pkgs.add(p)
                excluded_files.add(b[0])
                print(' excluding {f} from package {p}'.format(f=b[0], p=p))
        except Exception:
            pass


    print('Your exe will depend on the following packages:')
    print(excluded_pkgs)


    inc_libs = set(['libpython3.8.so.1.0'])
    binaries = [x for x in all_binaries if x[0] not in excluded_files]
    return binaries


block_cipher = None


a = Analysis(['notes_app/main.py'],
             pathex=['notes_app'],
             #binaries=[],
             datas=[("notes_app/view/notes_view.kv", "notes_app/view/")],
             #hiddenimports=[],
             #hookspath=[],
             hookspath=hookspath(),
             #runtime_hooks=[],
             runtime_hooks=runtime_hooks(),
             #excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             **get_deps_minimal(video=None)
             )


pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)


binaries = filter_binaries(a.binaries)


exe = EXE(pyz,
          Tree('notes_app'),
          a.scripts,
          binaries,
          a.zipfiles,
          a.datas,
          name='notes',
          debug=False,
          strip=None,
          upx=True,
          console=True )
