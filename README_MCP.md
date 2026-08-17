# Claude Code Configuration

Configure the Notes MCP server once in Claude Code. The exact configuration location depends on the Claude Code version and client setup.

## Linux / macOS

```json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": [
        "/home/deb/projects/notes_app/mcp_server.py"
      ]
    }
  }
}
```

## Windows

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

Once configured, Claude Code can automatically discover and use the Notes MCP tools, such as:

* `notes.search`
* `notes.list_sections`
* `notes.get_note`
* `notes.save_note`

The MCP server runs locally and communicates with Claude Code through **stdio**, so no HTTP server or open network port is required.
