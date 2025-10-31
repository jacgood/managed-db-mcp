# MCP Server Installation Guide

## Quick Start

The MCP server is already configured for this project! Just follow these steps:

## Step 1: Ensure the Managed DB API is Running

Make sure the Managed DB API is accessible:

```bash
# From the managed-db root directory
docker compose up -d db-admin-api postgres

# Verify it's running
curl http://localhost:8080/api/health
```

Expected response:
```json
{"status":"ok","postgres":"ok","postgrest":"unknown"}
```

## Step 2: MCP Server is Already Configured!

This project includes a **`.mcp.json`** file in the root directory that automatically configures the MCP server for Claude Code.

The configuration uses **project scope**, which means:
- ✅ Only you can see it (local to your machine)
- ✅ Works for this project only
- ✅ Uses `${PWD}` to automatically find the correct paths
- ✅ No manual path configuration needed!

### What's in `.mcp.json`

```json
{
  "mcpServers": {
    "managed-db": {
      "command": "python3",
      "args": [
        "${PWD}/services/mcp-server/server.py"
      ],
      "env": {
        "MANAGED_DB_API_URL": "http://localhost:8080/api"
      }
    }
  }
}
```

## Step 3: Alternative - Add via CLI (Optional)

If you prefer using the CLI, you can also add the server using:

```bash
# From the managed-db directory
claude mcp add --transport stdio managed-db \
  --env MANAGED_DB_API_URL=http://localhost:8080/api \
  -- python3 services/mcp-server/server.py
```

## Step 4: Verify the Server is Loaded

Within Claude Code, type:

```
/mcp
```

You should see `managed-db` listed as an available server.

## Step 5: Install Python Dependencies

The MCP server requires Python 3.10+ and the `httpx` package:

```bash
pip3 install httpx
```

**Note about MCP SDK**: The server uses the MCP Python SDK which should be automatically available through Claude Code. If you're running the server standalone, you may need to install the SDK separately.

## Verification

Once configured, you can verify the server is working by asking Claude:

```
"List all my managed database projects"
```

Claude should use the `list_projects` tool from the MCP server.

## Troubleshooting

### MCP Server Not Loading

1. Check the path in the config is absolute and correct
2. Verify Python 3.10+ is available: `python3 --version`
3. Check the API is running: `curl http://localhost:8080/api/health`
4. Look at Claude's logs for error messages

### API Connection Errors

1. Ensure `MANAGED_DB_API_URL` points to the correct endpoint
2. Verify the API is accessible from your machine
3. Check firewall/network settings

### Permission Errors

Make sure the server script is executable:

```bash
chmod +x /path/to/managed-db/services/mcp-server/server.py
```

## Alternative: Using with uv

If you have [uv](https://github.com/astral-sh/uv) installed, you can use it for faster dependency management:

```json
{
  "mcpServers": {
    "managed-db": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/managed-db/services/mcp-server",
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

## Next Steps

Once installed, check out the [README](README.md) for available tools and example usage.
