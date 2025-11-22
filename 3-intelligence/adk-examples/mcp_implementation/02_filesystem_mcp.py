"""
MCP Implementation - File System Server
Article 2: Orchestration & Collaboration Patterns

This example shows an MCP server that provides file system access to agents.
Agents can read files, list directories, search content, and access file metadata.

Use Cases:
- Code analysis across multiple files
- Documentation generation
- File organization and management
- Content extraction and processing

Business Value:
- Agents can work with local files securely
- Standardized file access across different agent frameworks
- Easy to add new file operations as tools
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


# ========================================
# MOCK FILE SYSTEM (for demo purposes)
# ========================================

MOCK_FILESYSTEM = {
    "/project/README.md": {
        "content": "# My Project\n\nThis is a sample project for demonstrating MCP file access.",
        "size": 67,
        "modified": "2024-11-18T10:00:00"
    },
    "/project/src/main.py": {
        "content": "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()",
        "size": 75,
        "modified": "2024-11-18T11:30:00"
    },
    "/project/src/utils.py": {
        "content": "def helper():\n    return 42\n\ndef formatter(text):\n    return text.upper()",
        "size": 63,
        "modified": "2024-11-18T09:15:00"
    },
    "/project/docs/guide.md": {
        "content": "# User Guide\n\n## Installation\n\nRun `pip install myproject`",
        "size": 58,
        "modified": "2024-11-17T14:20:00"
    },
    "/project/.gitignore": {
        "content": "*.pyc\n__pycache__/\n.env\nvenv/",
        "size": 34,
        "modified": "2024-11-16T08:00:00"
    }
}


# ========================================
# MCP SERVER FOR FILE SYSTEM
# ========================================

from dataclasses import dataclass


@dataclass
class MCPTool:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable


@dataclass
class MCPResource:
    uri: str
    name: str
    description: str
    mime_type: str
    handler: callable


class FileSystemMCPServer:
    """MCP Server for file system operations."""

    def __init__(self, name: str = "filesystem-server", base_path: str = "/project"):
        self.name = name
        self.version = "1.0.0"
        self.base_path = base_path
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register file system tools."""

        async def read_file(path: str) -> Dict[str, Any]:
            """Read file contents."""
            full_path = path if path.startswith(self.base_path) else f"{self.base_path}{path}"

            if full_path not in MOCK_FILESYSTEM:
                raise FileNotFoundError(f"File not found: {path}")

            file_data = MOCK_FILESYSTEM[full_path]
            return {
                "path": path,
                "content": file_data["content"],
                "size": file_data["size"],
                "encoding": "utf-8"
            }

        async def list_directory(path: str = "/", pattern: Optional[str] = None) -> Dict[str, Any]:
            """List files in a directory."""
            search_path = path if path.startswith(self.base_path) else f"{self.base_path}{path}"

            files = []
            for file_path in MOCK_FILESYSTEM.keys():
                if file_path.startswith(search_path):
                    relative = file_path[len(search_path):].lstrip('/')
                    if '/' not in relative or relative.split('/')[0]:  # Only direct children
                        if not pattern or pattern in file_path:
                            file_data = MOCK_FILESYSTEM[file_path]
                            files.append({
                                "name": os.path.basename(file_path),
                                "path": file_path,
                                "size": file_data["size"],
                                "modified": file_data["modified"],
                                "type": "file" if '.' in os.path.basename(file_path) else "directory"
                            })

            return {
                "path": path,
                "count": len(files),
                "files": files
            }

        async def search_content(query: str, path: str = "/") -> Dict[str, Any]:
            """Search for content in files."""
            search_path = path if path.startswith(self.base_path) else f"{self.base_path}{path}"

            matches = []
            for file_path, file_data in MOCK_FILESYSTEM.items():
                if file_path.startswith(search_path) and query.lower() in file_data["content"].lower():
                    # Find line numbers
                    lines = file_data["content"].split('\n')
                    matching_lines = [
                        (i+1, line) for i, line in enumerate(lines)
                        if query.lower() in line.lower()
                    ]

                    matches.append({
                        "file": file_path,
                        "match_count": len(matching_lines),
                        "matches": [
                            {"line": line_num, "content": content}
                            for line_num, content in matching_lines
                        ]
                    })

            return {
                "query": query,
                "files_searched": len([f for f in MOCK_FILESYSTEM.keys() if f.startswith(search_path)]),
                "files_with_matches": len(matches),
                "results": matches
            }

        async def get_file_metadata(path: str) -> Dict[str, Any]:
            """Get file metadata."""
            full_path = path if path.startswith(self.base_path) else f"{self.base_path}{path}"

            if full_path not in MOCK_FILESYSTEM:
                raise FileNotFoundError(f"File not found: {path}")

            file_data = MOCK_FILESYSTEM[full_path]
            return {
                "path": path,
                "size": file_data["size"],
                "modified": file_data["modified"],
                "extension": os.path.splitext(path)[1],
                "name": os.path.basename(path)
            }

        # Register tools
        self.tools["read_file"] = MCPTool(
            name="read_file",
            description="Read the contents of a file",
            parameters={
                "path": {"type": "string", "description": "File path relative to base", "required": True}
            },
            handler=read_file
        )

        self.tools["list_directory"] = MCPTool(
            name="list_directory",
            description="List files and directories",
            parameters={
                "path": {"type": "string", "description": "Directory path", "required": False},
                "pattern": {"type": "string", "description": "Filter pattern", "required": False}
            },
            handler=list_directory
        )

        self.tools["search_content"] = MCPTool(
            name="search_content",
            description="Search for text content in files",
            parameters={
                "query": {"type": "string", "description": "Search query", "required": True},
                "path": {"type": "string", "description": "Path to search in", "required": False}
            },
            handler=search_content
        )

        self.tools["get_file_metadata"] = MCPTool(
            name="get_file_metadata",
            description="Get metadata for a file",
            parameters={
                "path": {"type": "string", "description": "File path", "required": True}
            },
            handler=get_file_metadata
        )

    def _register_resources(self):
        """Register file system resources."""

        async def get_project_structure():
            """Get project structure."""
            structure = {}
            for file_path in MOCK_FILESYSTEM.keys():
                parts = file_path.split('/')
                current = structure
                for part in parts[1:-1]:  # Skip first empty and last (filename)
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = "file"

            return {"structure": structure, "total_files": len(MOCK_FILESYSTEM)}

        async def get_file_statistics():
            """Get file statistics."""
            total_size = sum(f["size"] for f in MOCK_FILESYSTEM.values())
            extensions = {}
            for path in MOCK_FILESYSTEM.keys():
                ext = os.path.splitext(path)[1] or "no extension"
                extensions[ext] = extensions.get(ext, 0) + 1

            return {
                "total_files": len(MOCK_FILESYSTEM),
                "total_size": total_size,
                "extensions": extensions,
                "timestamp": datetime.now().isoformat()
            }

        self.resources["fs://structure"] = MCPResource(
            uri="fs://structure",
            name="Project Structure",
            description="Hierarchical project structure",
            mime_type="application/json",
            handler=get_project_structure
        )

        self.resources["fs://stats"] = MCPResource(
            uri="fs://stats",
            name="File Statistics",
            description="Overall file statistics",
            mime_type="application/json",
            handler=get_file_statistics
        )

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        tool = self.tools[tool_name]
        try:
            result = await tool.handler(**parameters)
            return {"success": True, "result": result, "tool": tool_name}
        except Exception as e:
            return {"success": False, "error": str(e), "tool": tool_name}

    async def access_resource(self, uri: str) -> Dict[str, Any]:
        """Access a resource."""
        if uri not in self.resources:
            return {"error": f"Resource '{uri}' not found"}

        resource = self.resources[uri]
        try:
            data = await resource.handler()
            return {"success": True, "uri": uri, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e), "uri": uri}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "tools": [
                {"name": t.name, "description": t.description, "parameters": t.parameters}
                for t in self.tools.values()
            ],
            "resources": [
                {"uri": r.uri, "name": r.name, "description": r.description}
                for r in self.resources.values()
            ]
        }


# ========================================
# DEMO
# ========================================

async def demo():
    """Demonstrate file system MCP server."""

    print("="*80)
    print("FILE SYSTEM MCP SERVER DEMO")
    print("="*80)

    # Create server
    print("\n1. Creating File System MCP Server...")
    server = FileSystemMCPServer()

    # Show capabilities
    print("\n2. Server Capabilities:")
    capabilities = server.get_capabilities()
    print(f"Tools: {len(capabilities['tools'])}")
    for tool in capabilities['tools']:
        print(f"  - {tool['name']}: {tool['description']}")
    print(f"Resources: {len(capabilities['resources'])}")
    for resource in capabilities['resources']:
        print(f"  - {resource['uri']}: {resource['name']}")

    # Use tools
    print("\n3. Using File System Tools:")

    # List directory
    print("\n--- List root directory ---")
    result = await server.execute_tool("list_directory", {"path": "/"})
    print(json.dumps(result, indent=2))

    # Read file
    print("\n--- Read README.md ---")
    result = await server.execute_tool("read_file", {"path": "/README.md"})
    if result["success"]:
        print(f"Content:\n{result['result']['content']}")

    # Search content
    print("\n--- Search for 'def' ---")
    result = await server.execute_tool("search_content", {"query": "def", "path": "/src"})
    print(json.dumps(result, indent=2))

    # Get metadata
    print("\n--- Get file metadata ---")
    result = await server.execute_tool("get_file_metadata", {"path": "/src/main.py"})
    print(json.dumps(result, indent=2))

    # Access resources
    print("\n4. Accessing Resources:")

    print("\n--- Project structure ---")
    result = await server.access_resource("fs://structure")
    print(json.dumps(result, indent=2))

    print("\n--- File statistics ---")
    result = await server.access_resource("fs://stats")
    print(json.dumps(result, indent=2))

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(demo())
