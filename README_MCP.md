# Claude Code configuration

You configure it once (the exact location depends on the client/version), for example:

{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": [
        "/home/deb/projects/notes_app/mcp/mcp_server.py"
      ]
    }
  }
}

or on Windows

{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": [
        "C:\\Projects\\Notes\\mcp\\mcp_server.py"
      ]
    }
  }
}

Then Claude automatically sees tools like

notes.search
notes.list_sections
notes.get_note
notes.save_note