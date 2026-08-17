# Notes App

A lightweight desktop notes application built with **Python 3.11** and **KivyMD**.

![Notes application](https://github.com/datahappy1/notes_app/blob/main/notes_app_recording.gif)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Storage](#storage)
- [Search](#search)
- [Markdown Support](#markdown-support)
  - [Markdown Syntax](#markdown-syntax)
  - [Supported Markdown Commands](#supported-markdown-commands)
- [Drawing Pad](#drawing-pad)
- [Synchronization](#synchronization)
- [MCP Server](#mcp-server)
- [Development](#development)
  - [Requirements](#requirements)
  - [Running the Application](#running-the-application)
  - [Running Tests](#running-tests)
- [Building the Application](#building-the-application)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [Project Structure](#project-structure)
- [Version History](#version-history)
- [Useful Links](#useful-links)

---

## Features

- Organize notes into separate sections
- Add, rename, and delete sections
- Quickly filter sections in the navigation drawer
- Store notes in a plain text file
- Choose any local file as the notes storage
- Search notes within the current section or across all sections
- Case-sensitive and full-word search options
- Markdown preview
- Automatic saving while typing
- Configurable fonts, font sizes, foreground colors, and background colors
- Drawing pad associated with note sections
- Multiple drawing pen colors
- Drawing undo and clear functionality
- Detect changes made to the notes file outside the application
- Best-effort handling of concurrent modifications
- MCP server for integration with compatible AI clients

---

## Architecture

The application follows an **MVC architecture combined with an observer notification pattern**.

The main components are separated into:

```text
View
 │
 ▼
Controller
 │
 ▼
Services
 │
 ├── Notes / File handling
 ├── Search
 └── Drawing
```

The view is responsible for the user interface, while application logic is implemented in the controller, services, and model layers.

The MCP server uses the same application services as the graphical application rather than implementing a separate notes-management layer.

---

## Storage

Notes are stored in a plain text file.

Sections are separated using the application's section separator.

Example:

```text
<section=first>
Your first section.

Here you can write your notes.

<drawing>
{
    "version": 1,
    "strokes": [...]
}
</drawing>

<section=second>
Another section of yours.
```

The notes file remains human-readable and can also be edited using an external text editor.

### Application Metadata

The application creates supporting files when required.

#### `file_metadata.json`

Stores metadata about the currently selected notes file:

```json
{
    "_file_path": {"value": "some/path/to/my_first_file.txt"},
    "_file_size": {"value": 42},
    "_last_updated_on": {"value": 1654674166}
}
```

#### `settings.json`

Stores application settings such as fonts and colors:

```json
{
    "font_name": {"value": "RobotoMono-Regular"},
    "font_size": {"value": "14.0"},
    "background_color": {"value": "black"},
    "foreground_color": {"value": "green"}
}
```

---

## Search

The application provides note searching with several options:

- Search the current section
- Search all sections
- Case-sensitive search
- Full-word search
- Real-time filtering of sections in the navigation drawer

The section filter is intended to make navigation practical when a large number of sections are present.

---

## Markdown Support

The application supports a small subset of Markdown syntax through a custom renderer.

Markdown is rendered into KivyMD widgets rather than being processed by a full Markdown parser.

### Supported Markdown Syntax

| Syntax | Example | Result |
|---|---|---|
| Heading 1 | `# Heading` | Large heading |
| Heading 2 | `## Heading` | Medium heading |
| Heading 3 | `### Heading` | Small heading |
| Bold | `**text**` | **Bold text** |
| Italic | `*text*` | *Italic text* |
| Bullet | `- item` | • item |
| Indented bullet | `-- item` | Indented bullet |
| Quote | `> text` | Quote displayed in a card |
| Horizontal separator | `---` | Horizontal separator |
| URL | `https://example.com` | Clickable, underlined URL |
| Code block | See below | Monospace code block |

### Headings

Three heading levels are supported:

```text
# Heading 1
## Heading 2
### Heading 3
```

### Text Formatting

Bold and italic text are supported:

```text
**bold text**
*italic text*
```

The renderer converts these into Kivy markup internally.

### Lists

Simple bullet items are supported:

```text
- First item
- Second item
- Third item
```

An indented bullet can be created using two hyphens:

```text
- Main item
-- Indented item
-- Another indented item
- Another main item
```

The indented form is rendered visually as an indented `-` item. It is not a general-purpose nested Markdown list implementation.

### Quotes

Lines beginning with `>` are rendered as a separate card:

```text
> This is a quote
```

### Horizontal Separator

A line beginning with `---` is rendered as a horizontal separator:

```text
---
```

### URLs

URLs beginning with `http://` or `https://` are automatically detected:

```text
Visit https://example.com for more information.
```

The URL is rendered as a clickable, underlined link. Clicking it opens the URL using the system web browser.

### Code Blocks

Fenced code blocks are supported using triple backticks:
````
```python
def hello():
    print("Hello")
```
````

The content between the opening and closing triple backticks is rendered in a monospace font (`RobotoMono-Regular`) inside a card.

The language identifier after the opening backticks is **not interpreted** for syntax highlighting. 

---

## Drawing Pad

Each note section can have an associated drawing.

The drawing pad supports:

- Pencil drawing
- Multiple pen colors
- Selection of the active pen
- Undo
- Clear
- Save without closing the drawing window
- Closing the drawing window without saving

Drawings are stored as json-serialized strokes in the note text file and are placed in the associated notes section.

---

## Synchronization

The notes file can be stored in a directory managed by an external synchronization service such as Dropbox.

For example:

1. Place the notes file inside a synchronized folder.
2. Open the application.
3. Open the storage menu.
4. Select **Choose storage file**.
5. Select the synchronized notes file.

The application stores metadata about the notes file and uses `difflib` to provide best-effort handling when the file has been modified by another instance or outside the application.

This allows the same notes file to be shared between multiple devices, subject to the limitations of file-based synchronization.

---

## MCP Server

The project includes a small **Model Context Protocol (MCP) server** that exposes the notes application services to compatible AI clients.

The server uses the existing `NotesService`, so AI clients can interact with the same notes storage and section structure used by the desktop application.

Available operations include:

```text
notes.search
notes.list_sections
notes.get_note
notes.save_note
notes.list_markdown_commands
```

The server can be run independently:

```bash
python mcp_server.py
```

An MCP-compatible client can then be configured to start the server.

Example configuration:

```json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": [
        "/path/to/notes_app/mcp_server.py"
      ]
    }
  }
}
```

On Windows:

```json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": [
        "C:\\Projects\\Notes\\mcp_server.py"
      ]
    }
  }
}
```

---

## Development

### Requirements

The application is developed and tested with:

- Python 3.11
- Kivy
- KivyMD
- Pytest
- MCP Python SDK

A `requirements.txt` file is included in the project.

Pipenv can also be used for local development.

### Running the Application

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bat
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the application:

```bash
python notes_app/main.py
```

### Running Tests

The project uses **Pytest**.

From the project root:

```bash
pytest
```

---

## Building the Application

PyInstaller is used to package the application as a standalone desktop application.

Build the application on the same operating system for which it is intended.

### Windows

Create a virtual environment:

```bat
python -m venv venv_notes_app
venv_notes_app\Scripts\activate.bat
```

Install the required packages:

```bat
python -m pip install --upgrade pip wheel setuptools
python -m pip install kivy docutils pygments pypiwin32
python -m pip install kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer kivy.deps.angle
python -m pip install PyInstaller
```

Generate the PyInstaller specification:

```bat
PyInstaller --name notes notes_app/main.py
```

Rename the specification:

```bat
ren notes.spec notes_win.spec
```

The KivyMD KV file must be included in the `datas` section:

```python
datas=[
    ("notes_app\\view\\notes_view.kv", "notes_app\\view\\"),
]
```

Build:

```bat
PyInstaller notes_win.spec
```

The packaged application will be created under:

```text
dist/
```

### Linux

Create a virtual environment:

```bash
python3.11 -m venv venv_notes_app
source venv_notes_app/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt
python -m pip install PyInstaller
```

Generate the specification:

```bash
PyInstaller --name notes notes_app/main.py
```

Rename it:

```bash
mv notes.spec notes_linux.spec
```

Include the KV file:

```python
datas=[
    ("notes_app/view/notes_view.kv", "notes_app/view/"),
]
```

Build:

```bash
pyinstaller notes_linux.spec
```

### macOS

Build the macOS application **on macOS** rather than attempting to cross-build it from Windows.

Create a Python 3.11 environment:

```bash
python3.11 -m venv venv_notes_app
source venv_notes_app/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt
python -m pip install PyInstaller
```

Test the application before packaging:

```bash
python notes_app/main.py
```

Generate the PyInstaller specification:

```bash
PyInstaller --name Notes notes_app/main.py
```

Include the KV file:

```python
datas=[
    ("notes_app/view/notes_view.kv", "notes_app/view/"),
]
```

Build:

```bash
PyInstaller Notes.spec
```

The resulting application should be available as:

```text
dist/
└── Notes.app
```

Launch it with:

```bash
open dist/Notes.app
```

For macOS builds, dependencies such as Kivy's SDL2/GStreamer stack may require additional PyInstaller configuration depending on the Python, Kivy, Homebrew, and PyInstaller versions being used.

---

## Project Structure

The project is organized around the MVC architecture and separates UI, application logic, and services.

![Notes architecture](https://github.com/datahappy1/notes_app/blob/main/notes_app_architecture.png)

---

## Version History

| Version | Date | Description |
|:---:|:---:|---|
| **1.0.0** | 29/07/2026 | Python 3.11 upgrade, MCP server, Markdown support, Drawpad |
| 0.1.2 | 10/10/2022 | Minor bug fixes |
| 0.1.1 | 12/07/2022 | Removed item drawer menu highlight, improved diff feature, bug fixes |
| 0.1.0 | 19/06/2022 | Initial release |

---

## Useful Links

- [KivyMD documentation](https://kivymd.readthedocs.io/en/latest/components/)
- [Kivy MVC Template](https://github.com/HeaTTheatR/Kivy_MVC_Template/tree/master)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [PyInstaller documentation](https://pyinstaller.org/en/stable/)