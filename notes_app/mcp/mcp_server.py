"""
Minimal MCP server for the Notes application.

Exposes NotesService methods to Claude Code, Codex, etc.

Run:
    python mcp_server.py
"""

import json
import os

from fastmcp import FastMCP

from notes_app.defaults import Defaults
from notes_app.domain.notes_file import File
from notes_app.services.notes_service import NotesService

# ---------------------------------------------------------------------
# Bootstrap application
# ---------------------------------------------------------------------

defaults = Defaults()


# we need to load the file path to the currently used file in the notes app
def _get_file_path(filename):
    with open(file=filename, mode="r", encoding="utf-8") as f:
        content = json.load(f)
    return content.get("_file_path").get("value")


# NOTES_FILE takes precedence, letting the server target a specific notes file
# independently of whatever the GUI app currently has open. When it is unset we
# fall back to the file path recorded in the model store, then to the default.
file_path = os.environ.get("NOTES_FILE") or _get_file_path(
    filename=defaults.DEFAULT_MODEL_STORE_FILE_NAME
)

file = File(
    file_path=file_path or defaults.DEFAULT_NOTES_FILE_NAME,
    defaults=defaults,
)

notes = NotesService(
    file=file,
    defaults=defaults,
)

# ---------------------------------------------------------------------
# MCP
# ---------------------------------------------------------------------

mcp = FastMCP("Notes")


@mcp.tool
def list_markdown_commands() -> list[dict[str, str]]:
    """Return the Markdown syntax supported by the Notes application."""
    return [
        {
            "syntax": "# Heading",
            "description": "Heading level 1",
        },
        {
            "syntax": "## Heading",
            "description": "Heading level 2",
        },
        {
            "syntax": "### Heading",
            "description": "Heading level 3",
        },
        {
            "syntax": "**text**",
            "description": "Bold text",
        },
        {
            "syntax": "*text*",
            "description": "Italic text",
        },
        {
            "syntax": "- item",
            "description": "Bullet item",
        },
        {
            "syntax": "-- item",
            "description": "Indented bullet item",
        },
        {
            "syntax": "> text",
            "description": "Quote",
        },
        {
            "syntax": "---",
            "description": "Horizontal separator",
        },
        {
            "syntax": "https://example.com",
            "description": "Clickable URL",
        },
        {
            "syntax": "```",
            "description": "Fenced code block",
        },
    ]


@mcp.tool()
def search_notes(query: str):
    """
    Search all notes.
    """

    return [
        r.to_dict()
        for r in notes.search_all_sections_simple(
            query=query,
        )
    ]


@mcp.tool()
def list_sections():
    """
    List all note sections.
    """

    return notes.list_sections()


@mcp.tool()
def get_note(section: str):
    """
    Returns the contents of a section.
    """

    return {
        "section": section,
        "content": notes.get_section_by_name(section),
    }


@mcp.tool()
def save_note(section: str, content: str):
    """
    Overwrites a section.
    """

    notes.save_section_by_name(
        section_name=section,
        text=content,
    )
    notes.file.save_file_data()
    notes.file.reload()

    return {"success": True}


@mcp.tool()
def create_note(section: str, content: str = ""):
    """
    Creates a new section.
    """

    notes.create_section_by_name(
        section_name=section,
        text=content,
    )
    notes.file.save_file_data()
    notes.file.reload()

    return {"success": True}


@mcp.tool()
def rename_note(old_name: str, new_name: str):
    """
    Renames a section.
    """

    notes.rename_section_by_name(
        old_section_name=old_name,
        new_section_name=new_name,
    )
    notes.file.save_file_data()
    notes.file.reload()

    return {"success": True}


@mcp.tool()
def delete_note(section: str):
    """
    Deletes a section.
    """

    notes.delete_section_by_name(section)
    notes.file.save_file_data()
    notes.file.reload()

    return {"success": True}


# ---------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
