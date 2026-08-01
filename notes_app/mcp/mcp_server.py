"""
Minimal MCP server for the Notes application.

Exposes NotesService methods to Claude Code, Codex, etc.

Run:
    python mcp_server.py
"""
import json

from fastmcp import FastMCP

from notes_app.defaults import Defaults
from notes_app.domain.file import File
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


file_path = _get_file_path(filename=defaults.DEFAULT_MODEL_STORE_FILE_NAME)

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

    return {"success": True}


@mcp.tool()
def delete_note(section: str):
    """
    Deletes a section.
    """

    notes.delete_section_by_name(section)

    return {"success": True}


# ---------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
