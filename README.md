# Notes

A lightweight desktop notes application built with **Python 3.11** and
**KivyMD**.

Notes are stored in a plain text file and organized into sections. The
application provides a graphical editor, full-text search, Markdown
preview, automatic saving, drawing support, and an **MCP server** that
allows AI assistants and other MCP clients to work with the notes
programmatically.

![Notes
application](https://github.com/datahappy1/notes_app/blob/main/notes_app_recording.gif)

## Features

-   Section-based notes organization
    -   Create sections
    -   Rename sections
    -   Delete sections with confirmation
    -   Quickly filter sections from the navigation drawer
-   Plain-text file storage
-   Storage file can be located anywhere on the local filesystem
-   Compatible with synchronized folders such as Dropbox
-   Full-text search
    -   Search current section
    -   Search all sections
    -   Case-sensitive search
    -   Full-word search
-   Markdown preview
-   Automatic saving while typing
-   Customizable fonts, font sizes, background colors, and foreground
    colors
-   Drawing pad
    -   Multiple pen colors
    -   Undo
    -   Clear
    -   PNG export
-   External file-change detection and best-effort merging
-   MCP server for accessing and modifying notes through AI assistants

## Architecture

The application follows an **MVC architecture with an observer
notification pattern**.

``` text
                         ┌──────────────────┐
                         │    Notes View    │
                         │     KivyMD       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Notes Controller │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Notes Service  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             ┌──────────────┐           ┌──────────────┐
             │ Notes / File │           │    Search    │
             │    domain    │           │    service   │
             └──────┬───────┘           └──────────────┘
                    │
                    ▼
             ┌──────────────┐
             │ Plain text   │
             │  notes file  │
             └──────────────┘
```

The GUI and MCP server use the same `NotesService` layer rather than
implementing separate note-management logic. This keeps the MCP
interface thin and avoids introducing a separate database or persistence
layer.

## MCP Server

The project includes an **MCP (Model Context Protocol) server** that
exposes notes functionality to AI assistants and other MCP-compatible
clients.

The MCP layer acts as an adapter between the MCP protocol and the
existing `NotesService`.

### Why MCP?

The MCP server provides an AI assistant with a structured interface to
the Notes application instead of giving it direct access to the notes
file.

``` text
┌──────────────────┐
│   MCP Client     │
│ Claude / etc.    │
└────────┬─────────┘
         │
         │ MCP / stdio
         ▼
┌──────────────────┐
│  mcp_server.py   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   NotesService   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Notes text file  │
└──────────────────┘
```

### MCP capabilities

The MCP server exposes operations for working with notes and sections,
including:

-   Search notes
-   List sections
-   Read a note or section
-   Create notes
-   Save or update notes
-   Rename sections
-   Delete sections

### MCP transport

The server is designed to run as a local MCP process using **stdio**.

This means:

-   No HTTP server is required
-   No port needs to be opened
-   No network service is required
-   The MCP client starts the server process and communicates over
    stdin/stdout

For this local application, stdio keeps the architecture simple and
avoids introducing an unnecessary network service.

### Installing MCP dependencies

Install the MCP Python SDK with:

``` bash
pip install "mcp[cli]"
```

If the project requirements already contain the MCP dependency,
installing the project's normal dependencies is sufficient.

### Running the MCP server

From the project root:

``` bash
python mcp_server.py
```

The server communicates through stdio.

The server can also use the standard FastMCP direct-execution pattern:

``` python
if __name__ == "__main__":
    mcp.run()
```

### Testing the MCP server

The MCP SDK provides an MCP Inspector for development and debugging.

For a FastMCP server:

``` bash
uv run mcp dev mcp_server.py
```

This allows the available MCP tools to be inspected and invoked
interactively.

If using pip/virtualenv rather than `uv`, the equivalent MCP CLI can be
used from the project's virtual environment.

### Connecting an MCP client

An MCP client launches the server as a subprocess and communicates
through stdio.

A typical client configuration conceptually looks like:

``` json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": [
        "C:\\path\\to\\notes_app\\mcp_server.py"
      ]
    }
  }
}
```

The exact configuration format depends on the MCP client.

The important point is that the server does not need to listen on a port
when using stdio.

## Notes File Format

Notes are stored in a plain text file.

Sections are separated using the application's configured section
separator.

Example:

``` text
<section=first>
Your first section.

Here you can write your notes.

<section=second>
Another section of yours.
```

The notes file remains human-readable and can be edited outside the
application if necessary.

## Application Data

The application generates several files when first run.

### `file_metadata.json`

Stores metadata about the current notes file:

``` json
{
    "_file_path": {
        "value": "some/path/to/my_first_file.txt"
    },
    "_file_size": {
        "value": 42
    },
    "_last_updated_on": {
        "value": 1654674166
    }
}
```

The metadata allows the application to detect changes made to the notes
file by another application instance.

### `my_first_file.txt`

The actual notes file:

``` text
<section=first>
Your first section.

<section=second>
Another section.
```

### `settings.json`

Stores UI preferences such as font and colors:

``` json
{
    "font_name": {
        "value": "RobotoMono-Regular"
    },
    "font_size": {
        "value": "14.0"
    },
    "background_color": {
        "value": "black"
    },
    "foreground_color": {
        "value": "green"
    }
}
```

## Synchronizing Notes Between Devices

Because notes are stored in a normal text file, synchronization can be
handled by an external file synchronization service.

For example:

1.  Put the notes file inside a synchronized Dropbox folder.
2.  Open the Notes application.
3.  Select **Choose storage file**.
4.  Select the synchronized notes file.

The application uses the file metadata and `difflib`-based merging to
provide best-effort handling when the same notes file is modified
externally.

## Development

### Requirements

-   Python 3.11
-   Kivy
-   KivyMD
-   Pytest
-   MCP Python SDK

A `requirements.txt` file is provided with the project.

Pipenv can also be used for local development.

### Running the Application

Create a virtual environment:

``` bash
python -m venv venv
```

Activate it on Windows:

``` bat
venv\Scripts\activate
```

Install dependencies:

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run:

``` bash
python notes_app/main.py
```

### Running Tests

The project uses **Pytest**.

From the project root:

``` bash
pytest
```

The test suite covers application services, domain logic, and view
behavior.

## Building the Application

### Windows

Build from a Windows environment.

Create a virtual environment:

``` bat
python -m venv venv_notes_app
venv_notes_app\Scripts\activate.bat
```

Install build dependencies:

``` bat
python -m pip install --upgrade pip wheel setuptools

python -m pip install ^
    kivy ^
    docutils ^
    pygments ^
    pypiwin32 ^
    kivy.deps.sdl2 ^
    kivy.deps.glew ^
    kivy.deps.gstreamer ^
    kivy.deps.angle

python -m pip install PyInstaller
```

Generate the PyInstaller specification:

``` bat
cd ..
PyInstaller --name notes notes_app/main.py
```

Rename the generated spec file:

``` bat
ren notes.spec notes_win.spec
```

The KivyMD KV file must be included in the PyInstaller `datas` section:

``` python
datas=[
    ("notes_app\\view\\notes_view.kv", "notes_app\\view\\"),
]
```

Build:

``` bat
pyinstaller c:\notes_app\notes_app\notes_win.spec
```

### Linux

Create and activate a virtual environment:

``` bash
python -m venv venv_notes_app
source venv_notes_app/bin/activate
```

Install build dependencies:

``` bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install PyInstaller
```

Rename the generated spec file:

``` bash
mv notes.spec notes_linux.spec
```

Add the KV file to the `datas` section:

``` python
datas=[
    ("notes_app/view/notes_view.kv", "notes_app/view/"),
]
```

Build:

``` bash
pyinstaller notes_linux.spec
```

## Project Structure

The project is organized around a small MVC-style application with
services separated from the UI.

``` text
notes_app/
│
├── main.py
│
├── controller/
│   └── ...
│
├── model/
│   └── ...
│
├── services/
│   ├── notes_service.py
│   ├── drawing_service.py
│   └── search_service.py
│
├── view/
│   ├── notes_view.py
│   ├── notes_view.kv
│   ├── drawing_canvas.py
│   ├── drawing_window.py
│   └── markdown_renderer.py
│
├── observer/
│   └── ...
│
└── utils/
    └── ...

mcp_server.py
```

The MCP server sits outside the Kivy UI layer and uses `NotesService`
directly.

This is intentional: MCP provides programmatic access to application
capabilities without depending on the graphical interface.

## Version History

  -----------------------------------------------------------------------
         Version              Date       Description
  ---------------------- --------------- --------------------------------
          1.0.0            29/07/2026    Python 3.11 upgrade, MCP server,
                                         Markdown support, Drawpad

          0.1.2            10/10/2022    Minor bug fixes

          0.1.1            12/07/2022    Removed item drawer menu
                                         highlight, improved diff
                                         feature, bug fixes

          0.1.0            19/06/2022    Initial release
  -----------------------------------------------------------------------

## Useful Links

### Project

-   [Notes application
    repository](https://github.com/datahappy1/notes_app)

### Kivy / KivyMD

-   [KivyMD
    documentation](https://kivymd.readthedocs.io/en/latest/components/)
-   [Kivy MVC
    template](https://github.com/HeaTTheatR/Kivy_MVC_Template/tree/main)

### MCP

-   [MCP Python SDK
    documentation](https://py.sdk.modelcontextprotocol.io/)
-   [MCP Python SDK server
    documentation](https://py.sdk.modelcontextprotocol.io/server/)
-   [MCP Python SDK getting
    started](https://py.sdk.modelcontextprotocol.io/get-started/)

### Packaging

-   [PyInstaller](https://pyinstaller.org/en/stable/when-things-go-wrong.html)
