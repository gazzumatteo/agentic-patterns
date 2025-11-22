"""
MCP (Model Context Protocol) Implementation - Basic Server
Article 2: Orchestration & Collaboration Patterns

MCP allows AI agents to connect to external data sources and tools through a standardized protocol.
This example demonstrates a basic MCP server that provides tools and resources to agents.

Key Concepts:
- MCP Server: Exposes tools and resources
- MCP Client: Agents connect to servers to access capabilities
- Protocol: Standardized communication between server and client

Use Cases:
- Connecting to databases
- Accessing file systems
- Integrating with APIs
- Sharing tools across multiple agents

Reference: https://modelcontextprotocol.io/
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


# ========================================
# MCP SERVER IMPLEMENTATION
# ========================================

@dataclass
class MCPTool:
    """Represents a tool exposed by the MCP server."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable


@dataclass
class MCPResource:
    """Represents a resource (data source) exposed by the MCP server."""
    uri: str
    name: str
    description: str
    mime_type: str
    handler: callable


class MCPServer:
    """
    Basic MCP Server implementation.

    Provides:
    - Tool registration and execution
    - Resource registration and access
    - Client connection management
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.clients: List[str] = []

    def register_tool(self, tool: MCPTool):
        """Register a tool with the server."""
        self.tools[tool.name] = tool
        print(f"✓ Registered tool: {tool.name}")

    def register_resource(self, resource: MCPResource):
        """Register a resource with the server."""
        self.resources[resource.uri] = resource
        print(f"✓ Registered resource: {resource.uri}")

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        tool = self.tools[tool_name]
        try:
            result = await tool.handler(**parameters)
            return {
                "success": True,
                "result": result,
                "tool": tool_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

    async def access_resource(self, uri: str) -> Dict[str, Any]:
        """Access a resource by URI."""
        if uri not in self.resources:
            return {"error": f"Resource '{uri}' not found"}

        resource = self.resources[uri]
        try:
            data = await resource.handler()
            return {
                "success": True,
                "uri": uri,
                "mime_type": resource.mime_type,
                "data": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "uri": uri
            }

    def connect_client(self, client_id: str):
        """Register a client connection."""
        self.clients.append(client_id)
        print(f"✓ Client connected: {client_id}")

    def get_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
                for tool in self.tools.values()
            ],
            "resources": [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mime_type": resource.mime_type
                }
                for resource in self.resources.values()
            ]
        }


# ========================================
# EXAMPLE: DATABASE MCP SERVER
# ========================================

# Mock database
DATABASE = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"}
    ],
    "products": [
        {"id": 101, "name": "Laptop", "price": 999.99, "stock": 50},
        {"id": 102, "name": "Mouse", "price": 29.99, "stock": 200},
        {"id": 103, "name": "Keyboard", "price": 79.99, "stock": 150}
    ]
}


# Tool handlers
async def query_database(table: str, filter_field: Optional[str] = None, filter_value: Optional[str] = None):
    """Query database table with optional filtering."""
    if table not in DATABASE:
        raise ValueError(f"Table '{table}' not found")

    data = DATABASE[table]

    if filter_field and filter_value:
        data = [row for row in data if str(row.get(filter_field)) == str(filter_value)]

    return {
        "table": table,
        "count": len(data),
        "rows": data
    }


async def insert_record(table: str, record: Dict[str, Any]):
    """Insert a record into database table."""
    if table not in DATABASE:
        raise ValueError(f"Table '{table}' not found")

    DATABASE[table].append(record)

    return {
        "table": table,
        "inserted": record,
        "new_count": len(DATABASE[table])
    }


async def get_table_schema(table: str):
    """Get schema for a database table."""
    schemas = {
        "users": {
            "fields": ["id", "name", "email", "role"],
            "types": {"id": "int", "name": "str", "email": "str", "role": "str"}
        },
        "products": {
            "fields": ["id", "name", "price", "stock"],
            "types": {"id": "int", "name": "str", "price": "float", "stock": "int"}
        }
    }

    if table not in schemas:
        raise ValueError(f"Schema for '{table}' not found")

    return schemas[table]


# Resource handlers
async def get_database_stats():
    """Get database statistics."""
    return {
        "tables": list(DATABASE.keys()),
        "total_records": sum(len(table) for table in DATABASE.values()),
        "timestamp": datetime.now().isoformat()
    }


async def get_all_tables():
    """Get list of all tables."""
    return {
        "tables": [
            {"name": name, "record_count": len(data)}
            for name, data in DATABASE.items()
        ]
    }


# ========================================
# SERVER SETUP
# ========================================

def create_database_mcp_server() -> MCPServer:
    """Create and configure a database MCP server."""

    server = MCPServer(name="database-server", version="1.0.0")

    # Register tools
    server.register_tool(MCPTool(
        name="query_database",
        description="Query a database table with optional filtering",
        parameters={
            "table": {"type": "string", "description": "Table name", "required": True},
            "filter_field": {"type": "string", "description": "Field to filter on", "required": False},
            "filter_value": {"type": "string", "description": "Value to filter for", "required": False}
        },
        handler=query_database
    ))

    server.register_tool(MCPTool(
        name="insert_record",
        description="Insert a new record into a database table",
        parameters={
            "table": {"type": "string", "description": "Table name", "required": True},
            "record": {"type": "object", "description": "Record data", "required": True}
        },
        handler=insert_record
    ))

    server.register_tool(MCPTool(
        name="get_table_schema",
        description="Get the schema for a database table",
        parameters={
            "table": {"type": "string", "description": "Table name", "required": True}
        },
        handler=get_table_schema
    ))

    # Register resources
    server.register_resource(MCPResource(
        uri="db://stats",
        name="Database Statistics",
        description="Overall database statistics",
        mime_type="application/json",
        handler=get_database_stats
    ))

    server.register_resource(MCPResource(
        uri="db://tables",
        name="Table List",
        description="List of all database tables",
        mime_type="application/json",
        handler=get_all_tables
    ))

    return server


# ========================================
# DEMO: AGENT USING MCP SERVER
# ========================================

class MCPClient:
    """Simple MCP client for agents to connect to servers."""

    def __init__(self, client_id: str, server: MCPServer):
        self.client_id = client_id
        self.server = server
        self.server.connect_client(client_id)

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]):
        """Call a tool on the server."""
        print(f"\n[{self.client_id}] Calling tool: {tool_name}")
        print(f"Parameters: {json.dumps(parameters, indent=2)}")

        result = await self.server.execute_tool(tool_name, parameters)

        print(f"Result: {json.dumps(result, indent=2)}")
        return result

    async def get_resource(self, uri: str):
        """Get a resource from the server."""
        print(f"\n[{self.client_id}] Accessing resource: {uri}")

        result = await self.server.access_resource(uri)

        print(f"Result: {json.dumps(result, indent=2)}")
        return result

    def get_capabilities(self):
        """Get server capabilities."""
        return self.server.get_capabilities()


async def demo():
    """Demonstrate MCP server and client."""

    print("="*80)
    print("MCP SERVER DEMO")
    print("="*80)

    # Create server
    print("\n1. Creating MCP Server...")
    server = create_database_mcp_server()

    # Show capabilities
    print("\n2. Server Capabilities:")
    capabilities = server.get_capabilities()
    print(json.dumps(capabilities, indent=2))

    # Create client (agent)
    print("\n3. Connecting Agent as MCP Client...")
    agent = MCPClient(client_id="agent-001", server=server)

    # Agent uses tools
    print("\n4. Agent Using MCP Tools:")

    # Query users
    await agent.call_tool("query_database", {"table": "users"})

    # Query specific user
    await agent.call_tool("query_database", {
        "table": "users",
        "filter_field": "role",
        "filter_value": "admin"
    })

    # Get schema
    await agent.call_tool("get_table_schema", {"table": "products"})

    # Insert record
    await agent.call_tool("insert_record", {
        "table": "users",
        "record": {"id": 4, "name": "Diana", "email": "diana@example.com", "role": "user"}
    })

    # Agent accesses resources
    print("\n5. Agent Accessing MCP Resources:")

    await agent.get_resource("db://stats")
    await agent.get_resource("db://tables")

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(demo())
