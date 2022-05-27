# notes_app
notes app written in Python 3.8 + KivyMD

## description

### feature highlights

### development patterns
- generating dependencies graph
```language="sh"
pydeps notes_app --max-bacon 2 --exclude kivy
```

### building app
#### Windows app build from Windows environment:
- prerequisites example:

```language="sh"
virtualenv venv_notes_app
venv_notes_app\Scripts\activate.bat
(venv_notes_app) python -m pip install --upgrade pip wheel setuptools
(venv_notes_app) python -m pip install kivy docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer kivy.deps.angle
(venv_notes_app) python -m pip install PyInstaller
(venv_notes_app) PyInstaller --name notes notes_app/main.py
```

- build command example:
```language="sh"
(venv_notes_app) PyInstaller c:\notes_app\notes_app\notes.spec
```

## useful links
- development 
  - https://kivymd.readthedocs.io/en/latest/components/
  - https://www.tutorialspoint.com/design_pattern/mvc_pattern.htm
  - https://github.com/HeaTTheatR/Kivy_MVC_Template/tree/main
  - https://github.com/thebjorn/pydeps
  
- app building
  - https://dev.to/ngonidzashe/using-pyinstaller-to-package-kivy-and-kivymd-desktop-apps-2fmj
  - https://github.com/devgiordane/kivy-md-build
