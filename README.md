# notes_app
Notes application written in Python 3.8 & KivyMD

![](https://github.com/datahappy1/notes_app/blob/main/notes_app_recording.gif)

## application description
- OS independent
- Notes can be grouped in separate sections, these sections can be added, renamed or removed
- Notes storage file can be placed anywhere on the local drive but can also be placed in a DropBox shared folder for example to synchronize notes across devices
- Full-text or word-based search capability across the current section or all sections
- Customizable fonts and colors, settings can be persisted
- Notes text is auto-saved while typing

## version history
| version | date | description |
| :---: | :---: | :---: |
| 0.1.2 | 10/10/2022 | minor bugfixes |
| 0.1.1  | 12/7/2022  | removing item drawer menu highlight, improving diff feature, bugfixes |
| 0.1.0  | 19/6/2022  | initial release |

## FAQ
- I need to synchronize my notes file across devices, how do I achieve that?
  - Copy the notes file to the synchronized folder of your choice
  - Click the file icon menu in the app, press `choose storage file`, locate the file in the synchronized folder and you're set  

### information for developers
The application design is based on the MVC architecture with the observer notification pattern. 
The notes are stored in a defined text file where the notes sections are separated by the defined section separator pattern.  

The model in the MVC is responsible for storing the metadata of this text file only. 
When the notes text file content significantly changes or when a different text file
for storage is chosen, the view is notified through it's registered observer and displays a info message on the UI.

The app uses `difflib` library to do the best effort to reasonably "version-control" notes in case the storage file was modified from another instance of the app that is using the same
text file for notes storage. *This can happen when using a shared DropBox folder for example.*

When running the app for the first time, these needed files get auto-generated:
- `file_metadata.json` - stores the notes text file metadata like it's file path, size and last updated epoch timestamp
```json
{
    "_file_path": {"value": "some/path/to/my_first_file.txt"}, 
    "_file_size": {"value": 42}, 
    "_last_updated_on": {"value": 1654674166}
}
```
- `my_first_file.txt` - this is the notes text file itself
```text
<section=first>  Your first section. 
Here you can write your notes.
<section=second>  Another section of yours.
```
- `settings.json` - stores settings like fonts, colors for the UI
```json
{
    "font_name": {"value": "RobotoMono-Regular"}, 
    "font_size": {"value": "14.0"}, 
    "background_color": {"value": "black"}, 
    "foreground_color": {"value": "green"}
}
```

When running the app locally, Pipenv is recommended but general requirements.txt file is also attached.

- generating dependencies graph using Pydeps
```language="sh"
cd notes_app
pip3 install pydeps
pydeps notes_app --max-bacon 2 --cluster --rmprefix notes_app. --exclude-exact notes_app.utils notes_app.view notes_app.model notes_app.controller notes_app.observer
```
![](https://github.com/datahappy1/notes_app/blob/main/notes_app.svg)

- running unit tests using Pytest
```language="sh
cd notes_app
pytest
```

### building the application
#### Windows app build from Windows environment:
- prerequisites example:

```language="sh"
virtualenv venv_notes_app
venv_notes_app\Scripts\activate.bat
(venv_notes_app) python -m pip install --upgrade pip wheel setuptools
(venv_notes_app) python -m pip install kivy docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer kivy.deps.angle
(venv_notes_app) python -m pip install PyInstaller
(venv_notes_app) cd ..
(venv_notes_app) PyInstaller --name notes notes_app/main.py
ren "notes.spec" "notes_win.spec"
change in the spec file the line datas=[], to datas=[("notes_app\\view\\notes_view.kv", "notes_app\\view\\")],
```

- build command example:
```language="sh"
(venv_notes_app) PyInstaller c:\notes_app\notes_app\notes_win.spec
```

#### Linux app build from Linux environment:
- prerequisites example:

```language="sh"
virtualenv venv_notes_app
source bin/activate
(venv_notes_app) python -m pip install --upgrade pip wheel setuptools
(venv_notes_app) python -m pip install PyInstaller
mv notes.spec notes_linux.spec
change in the spec file the line datas=[], to datas=[("notes_app/view/notes_view.kv", "notes_app/view/")],
```

- build command example:
```language="sh"
(venv_notes_app) pyinstaller notes_linux.spec
```

## useful links
- app development 
  - https://kivymd.readthedocs.io/en/latest/components/
  - https://www.tutorialspoint.com/design_pattern/mvc_pattern.htm
  - https://github.com/HeaTTheatR/Kivy_MVC_Template/tree/main
  - https://github.com/thebjorn/pydeps
  - https://github.com/kivymd/KivyMD/blob/master/kivymd/icon_definitions.py
  
- building the app
  - https://pyinstaller.org/en/stable/when-things-go-wrong.html
  - https://dev.to/ngonidzashe/using-pyinstaller-to-package-kivy-and-kivymd-desktop-apps-2fmj
  - https://github.com/devgiordane/kivy-md-build
