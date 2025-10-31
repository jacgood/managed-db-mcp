#!/usr/bin/env python3
"""
MCP Server for Managed DB API

Provides tools for managing PostgreSQL databases through the Managed DB API.
"""

import asyncio
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# API configuration
API_BASE_URL = os.getenv("MANAGED_DB_API_URL", "http://localhost:8080/api")

app = Server("managed-db")


def create_http_client() -> httpx.AsyncClient:
    """Create configured HTTP client for API requests."""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=30.0,
        headers={"Content-Type": "application/json"}
    )


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for Managed DB API."""
    return [
        Tool(
            name="create_project",
            description="Create a new managed database project with isolated database, roles, and auto-generated REST API",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Human-readable project name (e.g., 'My Analytics DB')"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["db", "schema"],
                        "description": "Isolation mode: 'db' creates separate database, 'schema' creates schema in shared database",
                        "default": "db"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional project description"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_projects",
            description="List all managed database projects",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_project",
            description="Get detailed information about a specific project including connection details and API keys",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="delete_project",
            description="Delete a project (soft delete by default, use hard=true to permanently remove database)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project to delete"
                    },
                    "hard": {
                        "type": "boolean",
                        "description": "If true, permanently deletes database and PostgREST container. If false, marks as deleted but keeps data.",
                        "default": False
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="rotate_project_keys",
            description="Rotate JWT secret and API keys (anon_key, service_key) for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="create_table",
            description="Create a table in a project database with columns, indexes, and optional RLS policies",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project"
                    },
                    "name": {
                        "type": "string",
                        "description": "Table name"
                    },
                    "columns": {
                        "type": "array",
                        "description": "Table columns",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "data_type": {"type": "string", "description": "PostgreSQL data type (e.g., 'text', 'integer', 'timestamptz')"},
                                "nullable": {"type": "boolean", "default": True},
                                "default": {"type": "string", "description": "Default value expression"}
                            },
                            "required": ["name", "data_type"]
                        }
                    },
                    "indexes": {
                        "type": "array",
                        "description": "Optional indexes",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "columns": {"type": "array", "items": {"type": "string"}},
                                "unique": {"type": "boolean", "default": False}
                            },
                            "required": ["name", "columns"]
                        }
                    },
                    "rls_policies": {
                        "type": "array",
                        "description": "Optional Row Level Security policies",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "command": {"type": "string", "enum": ["SELECT", "INSERT", "UPDATE", "DELETE", "ALL"]},
                                "expression": {"type": "string", "description": "SQL expression that returns boolean"},
                                "with_check": {"type": "string", "description": "Optional WITH CHECK expression for INSERT/UPDATE"}
                            },
                            "required": ["name", "command", "expression"]
                        }
                    }
                },
                "required": ["project_id", "name", "columns"]
            }
        ),
        Tool(
            name="run_migration",
            description="Execute arbitrary SQL migration on a project database",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project"
                    },
                    "sql": {
                        "type": "string",
                        "description": "SQL statements to execute"
                    },
                    "statement_timeout_ms": {
                        "type": "integer",
                        "description": "Statement timeout in milliseconds",
                        "default": 30000
                    }
                },
                "required": ["project_id", "sql"]
            }
        ),
        Tool(
            name="backup_project",
            description="Create a pg_dump backup of a project database",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project to backup"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="restore_project",
            description="Restore a project database from a backup artifact",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project to restore"
                    },
                    "artifact_path": {
                        "type": "string",
                        "description": "Path to backup artifact file"
                    }
                },
                "required": ["project_id", "artifact_path"]
            }
        ),
        Tool(
            name="get_project_health",
            description="Check health status of a specific project's database and PostgREST API",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "UUID of the project"
                    }
                },
                "required": ["project_id"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute MCP tool by calling the Managed DB API."""

    async with create_http_client() as client:
        try:
            if name == "create_project":
                response = await client.post("/projects", json={
                    "name": arguments["name"],
                    "mode": arguments.get("mode", "db"),
                    "description": arguments.get("description")
                })
                response.raise_for_status()
                data = response.json()
                return [TextContent(
                    type="text",
                    text=f"✅ Project created successfully!\n\n"
                         f"ID: {data['id']}\n"
                         f"Name: {data['name']}\n"
                         f"Slug: {data['slug']}\n"
                         f"Mode: {data['mode']}\n"
                         f"Database: {data['db_name']}\n"
                         f"Connection URI: {data['connection_uri']}\n"
                         f"REST API URL: {data['rest_base_url']}\n"
                         f"Docs URL: {data['docs_url']}\n"
                         f"Anonymous API Key: {data['anon_key']}\n"
                         f"Service API Key: {data['service_key']}\n"
                         f"Created: {data['created_at']}"
                )]

            elif name == "list_projects":
                response = await client.get("/projects")
                response.raise_for_status()
                data = response.json()
                projects = data.get("projects", [])

                if not projects:
                    return [TextContent(type="text", text="No projects found.")]

                output = f"Found {len(projects)} project(s):\n\n"
                for p in projects:
                    output += f"• {p['name']} ({p['slug']})\n"
                    output += f"  ID: {p['id']}\n"
                    output += f"  Mode: {p['mode']}\n"
                    output += f"  Database: {p['db_name']}\n"
                    output += f"  REST API: {p['rest_base_url']}\n"
                    output += f"  Created: {p['created_at']}\n\n"

                return [TextContent(type="text", text=output)]

            elif name == "get_project":
                project_id = arguments["project_id"]
                response = await client.get(f"/projects/{project_id}")
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"Project Details:\n\n"
                         f"ID: {data['id']}\n"
                         f"Name: {data['name']}\n"
                         f"Slug: {data['slug']}\n"
                         f"Mode: {data['mode']}\n"
                         f"Database: {data['db_name']}\n"
                         f"Schema: {data.get('schema_name', 'N/A')}\n"
                         f"Connection URI: {data['connection_uri']}\n"
                         f"REST API URL: {data['rest_base_url']}\n"
                         f"Docs URL: {data['docs_url']}\n"
                         f"Anonymous Key: {data.get('anon_key', 'N/A')}\n"
                         f"Service Key: {data.get('service_key', 'N/A')}\n"
                         f"Created: {data['created_at']}\n"
                         f"Updated: {data['updated_at']}\n"
                         f"Deleted: {data.get('deleted_at', 'N/A')}"
                )]

            elif name == "delete_project":
                project_id = arguments["project_id"]
                hard = arguments.get("hard", False)
                response = await client.delete(f"/projects/{project_id}", params={"hard": hard})
                response.raise_for_status()

                delete_type = "permanently deleted" if hard else "soft deleted (marked for deletion)"
                return [TextContent(
                    type="text",
                    text=f"✅ Project {project_id} has been {delete_type}."
                )]

            elif name == "rotate_project_keys":
                project_id = arguments["project_id"]
                response = await client.post(f"/projects/{project_id}/rotate-keys")
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"✅ Keys rotated successfully!\n\n"
                         f"Project ID: {data['id']}\n"
                         f"New Anonymous Key: {data['anon_key']}\n"
                         f"New Service Key: {data['service_key']}\n"
                         f"New JWT Secret: {data['jwt_secret']}\n"
                         f"Rotated At: {data['rotated_at']}"
                )]

            elif name == "create_table":
                project_id = arguments["project_id"]
                table_data = {
                    "name": arguments["name"],
                    "columns": arguments["columns"]
                }
                if "indexes" in arguments:
                    table_data["indexes"] = arguments["indexes"]
                if "rls_policies" in arguments:
                    table_data["rls_policies"] = arguments["rls_policies"]

                response = await client.post(f"/projects/{project_id}/tables", json=table_data)
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"✅ Table '{arguments['name']}' created successfully!\n\n{data}"
                )]

            elif name == "run_migration":
                project_id = arguments["project_id"]
                migration_data = {
                    "sql": arguments["sql"],
                    "statement_timeout_ms": arguments.get("statement_timeout_ms", 30000)
                }

                response = await client.post(f"/projects/{project_id}/migrations", json=migration_data)
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"✅ Migration executed successfully!\n\n{data}"
                )]

            elif name == "backup_project":
                project_id = arguments["project_id"]
                response = await client.post(f"/projects/{project_id}/backup")
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"✅ Backup created successfully!\n\n"
                         f"Artifact Path: {data['artifact_path']}\n"
                         f"Started At: {data['started_at']}\n"
                         f"Completed At: {data.get('completed_at', 'In progress...')}"
                )]

            elif name == "restore_project":
                project_id = arguments["project_id"]
                restore_data = {"artifact_path": arguments["artifact_path"]}

                response = await client.post(f"/projects/{project_id}/restore", json=restore_data)
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"✅ Restore initiated successfully!\n\n{data}"
                )]

            elif name == "get_project_health":
                project_id = arguments["project_id"]
                response = await client.get(f"/projects/{project_id}/health")
                response.raise_for_status()
                data = response.json()

                return [TextContent(
                    type="text",
                    text=f"Project Health Status:\n\n{data}"
                )]

            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(error_data))
            except Exception:
                error_detail = e.response.text or str(e)

            return [TextContent(
                type="text",
                text=f"❌ API Error ({e.response.status_code}): {error_detail}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
