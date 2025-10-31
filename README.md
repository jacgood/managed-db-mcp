# Managed DB MCP Server

An MCP (Model Context Protocol) server that provides tools for managing PostgreSQL databases through the Managed DB API.

## Overview

This MCP server exposes the Managed DB API as tools that can be used by Claude Code and other MCP-compatible clients. It allows you to:

- Create and manage isolated PostgreSQL database projects
- Execute migrations and create tables with RLS policies
- Backup and restore databases
- Manage API keys and authentication
- Monitor project health

## Installation

### Option 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer that can automatically manage dependencies:

```bash
# uv will automatically install dependencies when running the server
uv pip install -r requirements.txt
```

### Option 2: Using pip

1. Install the MCP Python SDK:
```bash
# The MCP SDK may need to be installed from source
pip install mcp httpx
```

2. Set the API base URL (optional):
```bash
export MANAGED_DB_API_URL=http://localhost:8080/api
```

**Note**: If you encounter issues installing the `mcp` package, you may need to install it from the official repository or wait for it to be published to PyPI. The server is ready to use once the MCP SDK is available.

## Usage with Claude Code

Add this MCP server to your Claude Code configuration:

### Using npx (Recommended)

Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "managed-db": {
      "command": "python",
      "args": ["/path/to/managed-db/services/mcp-server/server.py"],
      "env": {
        "MANAGED_DB_API_URL": "http://localhost:8080/api"
      }
    }
  }
}
```

### Using uv (Alternative)

```json
{
  "mcpServers": {
    "managed-db": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/managed-db/services/mcp-server",
        "run",
        "server.py"
      ],
      "env": {
        "MANAGED_DB_API_URL": "http://localhost:8080/api"
      }
    }
  }
}
```

## Available Tools

### Project Management

- **`create_project`** - Create a new managed database project
  - Creates isolated database with owner/service/anon roles
  - Deploys PostgREST container for instant REST API
  - Generates JWT secret and API keys

- **`list_projects`** - List all projects

- **`get_project`** - Get detailed project information including connection details

- **`delete_project`** - Delete a project (soft or hard delete)

- **`rotate_project_keys`** - Rotate JWT secret and API keys

- **`get_project_health`** - Check project database and PostgREST status

### Database Operations

- **`create_table`** - Create a table with columns, indexes, and RLS policies

- **`run_migration`** - Execute arbitrary SQL migrations

### Backup & Restore

- **`backup_project`** - Create a pg_dump backup

- **`restore_project`** - Restore from backup artifact

## Example Usage

Once configured, you can use these tools in Claude Code:

```
User: Create a new database project called "Analytics Dashboard"

Claude: [Uses create_project tool]
✅ Project created successfully!
ID: abc-123-def
Database: proj_analytics_dashboard
Connection URI: postgresql://proj_analytics_dashboard_owner:...@localhost:5432/proj_analytics_dashboard
REST API URL: https://db.example.com/p/abc-123-def/rest
```

```
User: Create a users table with email and created_at columns

Claude: [Uses create_table tool with the project ID]
✅ Table 'users' created successfully!
```

## Configuration

### Environment Variables

- `MANAGED_DB_API_URL` - Base URL for the Managed DB API (default: `http://localhost:8080/api`)

## Development

Run the server directly:

```bash
python server.py
```

The server communicates via stdin/stdout using the MCP protocol.

## Requirements

- Python 3.10+
- mcp >= 1.0.0
- httpx >= 0.26.0
- Running Managed DB API service

## Architecture

The MCP server acts as a bridge between Claude Code and the Managed DB API:

```
Claude Code <--> MCP Server <--> Managed DB API <--> PostgreSQL
```

Each MCP tool makes HTTP requests to the corresponding API endpoint and returns formatted responses.
