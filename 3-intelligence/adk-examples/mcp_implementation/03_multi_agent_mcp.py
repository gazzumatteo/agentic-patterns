"""
MCP Implementation - Multi-Agent Collaboration via MCP
Article 2: Orchestration & Collaboration Patterns

This example demonstrates multiple agents connecting to MCP servers
and collaborating on a complex task using shared tools and resources.

Scenario: Code Review System
- Analyzer Agent: Analyzes code quality using file system MCP
- Security Agent: Checks for security issues
- Documentation Agent: Verifies documentation completeness
- Coordinator Agent: Orchestrates the review process

Business Value:
- Agents can share capabilities through MCP
- Standardized protocol for agent-tool communication
- Easy to add new agents without changing existing ones
"""

import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime


# ========================================
# MOCK CODE REPOSITORY
# ========================================

CODE_REPOSITORY = {
    "/app/auth.py": {
        "content": """import hashlib

def hash_password(password):
    # SECURITY ISSUE: Using MD5 (weak)
    return hashlib.md5(password.encode()).hexdigest()

def login(username, password):
    # TODO: Add rate limiting
    hashed = hash_password(password)
    # Check against database
    return True
""",
        "size": 250,
        "language": "python"
    },
    "/app/api.py": {
        "content": """from flask import Flask, request

app = Flask(__name__)

@app.route('/user/<id>')
def get_user(id):
    # SECURITY ISSUE: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {id}"
    # Execute query...
    return {"user": "data"}
""",
        "size": 200,
        "language": "python"
    },
    "/app/utils.py": {
        "content": """def calculate_total(items):
    '''Calculate total price of items.

    Args:
        items: List of items with price field

    Returns:
        float: Total price
    '''
    return sum(item['price'] for item in items)

def format_date(date):
    # Missing docstring
    return date.strftime('%Y-%m-%d')
""",
        "size": 250,
        "language": "python"
    },
    "/README.md": {
        "content": """# My App

A sample application.

## Installation

pip install -r requirements.txt
""",
        "size": 80,
        "language": "markdown"
    }
}


# ========================================
# MCP SERVER FOR CODE ANALYSIS
# ========================================

class CodeAnalysisMCPServer:
    """MCP Server providing code analysis tools."""

    def __init__(self):
        self.name = "code-analysis-server"
        self.version = "1.0.0"

    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read a code file."""
        if path not in CODE_REPOSITORY:
            raise FileNotFoundError(f"File not found: {path}")

        return {
            "path": path,
            "content": CODE_REPOSITORY[path]["content"],
            "language": CODE_REPOSITORY[path]["language"]
        }

    async def list_files(self, extension: str = None) -> Dict[str, Any]:
        """List all code files."""
        files = []
        for path, data in CODE_REPOSITORY.items():
            if extension is None or path.endswith(extension):
                files.append({
                    "path": path,
                    "size": data["size"],
                    "language": data["language"]
                })

        return {"files": files, "count": len(files)}

    async def check_security(self, code: str) -> Dict[str, Any]:
        """Check code for security issues."""
        issues = []

        # Check for common security issues
        if "md5" in code.lower() or "hashlib.md5" in code:
            issues.append({
                "severity": "high",
                "type": "weak_crypto",
                "message": "Using MD5 for hashing (weak algorithm)"
            })

        if "f\"SELECT" in code or 'f"SELECT' in code:
            issues.append({
                "severity": "critical",
                "type": "sql_injection",
                "message": "Potential SQL injection vulnerability (string interpolation in query)"
            })

        if "eval(" in code or "exec(" in code:
            issues.append({
                "severity": "critical",
                "type": "code_injection",
                "message": "Use of eval/exec (code injection risk)"
            })

        return {
            "issues_found": len(issues),
            "issues": issues,
            "severity_counts": {
                "critical": len([i for i in issues if i["severity"] == "critical"]),
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"])
            }
        }

    async def check_documentation(self, code: str) -> Dict[str, Any]:
        """Check if functions have docstrings."""
        missing_docs = []

        lines = code.split('\n')
        in_function = False
        function_name = None

        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                in_function = True
                function_name = line.strip().split('(')[0].replace('def ', '')
                # Check next line for docstring
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if not next_line.startswith('"""') and not next_line.startswith("'''"):
                        missing_docs.append({
                            "function": function_name,
                            "line": i + 1,
                            "message": f"Function '{function_name}' missing docstring"
                        })

        return {
            "missing_docstrings": len(missing_docs),
            "details": missing_docs
        }

    async def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze code complexity (simplified)."""
        lines = code.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

        functions = len([l for l in lines if 'def ' in l])
        classes = len([l for l in lines if 'class ' in l])
        comments = len([l for l in lines if l.strip().startswith('#')])

        return {
            "total_lines": len(lines),
            "code_lines": len(code_lines),
            "functions": functions,
            "classes": classes,
            "comments": comments,
            "comment_ratio": comments / len(code_lines) if code_lines else 0
        }


# ========================================
# AGENTS
# ========================================

class CodeReviewAgent:
    """Base class for code review agents."""

    def __init__(self, name: str, server: CodeAnalysisMCPServer):
        self.name = name
        self.server = server

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """Override in subclasses."""
        raise NotImplementedError


class SecurityAgent(CodeReviewAgent):
    """Agent that checks for security issues."""

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        print(f"\n[{self.name}] Analyzing security: {file_path}")

        # Read file
        file_data = await self.server.read_file(file_path)
        code = file_data["content"]

        # Check security
        security_result = await self.server.check_security(code)

        print(f"[{self.name}] Found {security_result['issues_found']} security issues")

        return {
            "agent": self.name,
            "file": file_path,
            "security_score": 100 - (security_result['issues_found'] * 20),
            "issues": security_result["issues"],
            "recommendation": "Fix security issues before deployment" if security_result['issues_found'] > 0 else "No security issues found"
        }


class DocumentationAgent(CodeReviewAgent):
    """Agent that verifies documentation."""

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        print(f"\n[{self.name}] Checking documentation: {file_path}")

        # Read file
        file_data = await self.server.read_file(file_path)
        code = file_data["content"]

        # Check documentation
        doc_result = await self.server.check_documentation(code)

        print(f"[{self.name}] {doc_result['missing_docstrings']} functions missing docstrings")

        return {
            "agent": self.name,
            "file": file_path,
            "documentation_score": 100 - (doc_result['missing_docstrings'] * 25),
            "missing_docs": doc_result["details"],
            "recommendation": "Add docstrings to all functions" if doc_result['missing_docstrings'] > 0 else "Documentation complete"
        }


class QualityAgent(CodeReviewAgent):
    """Agent that analyzes code quality."""

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        print(f"\n[{self.name}] Analyzing code quality: {file_path}")

        # Read file
        file_data = await self.server.read_file(file_path)
        code = file_data["content"]

        # Analyze complexity
        complexity = await self.server.analyze_complexity(code)

        # Calculate quality score
        quality_score = 70  # Base score
        if complexity["comment_ratio"] > 0.1:
            quality_score += 15
        if complexity["functions"] > 0:
            quality_score += 15

        print(f"[{self.name}] Quality score: {quality_score}/100")

        return {
            "agent": self.name,
            "file": file_path,
            "quality_score": quality_score,
            "complexity": complexity,
            "recommendation": "Good code structure" if quality_score >= 80 else "Consider refactoring"
        }


class CoordinatorAgent:
    """Coordinates the code review process."""

    def __init__(self, server: CodeAnalysisMCPServer):
        self.server = server
        self.security_agent = SecurityAgent("SecurityAgent", server)
        self.doc_agent = DocumentationAgent("DocAgent", server)
        self.quality_agent = QualityAgent("QualityAgent", server)

    async def review_repository(self) -> Dict[str, Any]:
        """Coordinate full repository review."""

        print("="*80)
        print("CODE REVIEW COORDINATOR")
        print("="*80)

        # Get Python files
        print("\n1. Discovering Python files...")
        files_result = await self.server.list_files(extension=".py")
        python_files = [f["path"] for f in files_result["files"]]

        print(f"Found {len(python_files)} Python files")

        # Review each file
        reviews = []

        for file_path in python_files:
            print(f"\n2. Reviewing: {file_path}")
            print("-" * 80)

            # Run all agents in parallel
            security_result, doc_result, quality_result = await asyncio.gather(
                self.security_agent.analyze(file_path),
                self.doc_agent.analyze(file_path),
                self.quality_agent.analyze(file_path)
            )

            # Aggregate results
            overall_score = (
                security_result["security_score"] * 0.4 +
                doc_result["documentation_score"] * 0.3 +
                quality_result["quality_score"] * 0.3
            )

            reviews.append({
                "file": file_path,
                "overall_score": round(overall_score, 1),
                "security": security_result,
                "documentation": doc_result,
                "quality": quality_result,
                "status": "PASS" if overall_score >= 80 else "NEEDS_WORK"
            })

        # Summary
        print("\n" + "="*80)
        print("REVIEW SUMMARY")
        print("="*80)

        avg_score = sum(r["overall_score"] for r in reviews) / len(reviews)
        passing = sum(1 for r in reviews if r["status"] == "PASS")

        print(f"Files Reviewed: {len(reviews)}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Passing: {passing}/{len(reviews)}")
        print(f"Status: {'✓ APPROVED' if passing == len(reviews) else '⚠ NEEDS REVISION'}")

        print("\nFile Details:")
        for review in reviews:
            print(f"\n{review['file']}:")
            print(f"  Overall: {review['overall_score']}/100 [{review['status']}]")
            print(f"  Security: {review['security']['security_score']}/100")
            print(f"  Documentation: {review['documentation']['documentation_score']}/100")
            print(f"  Quality: {review['quality']['quality_score']}/100")

        return {
            "reviews": reviews,
            "summary": {
                "total_files": len(reviews),
                "average_score": avg_score,
                "passing": passing,
                "status": "APPROVED" if passing == len(reviews) else "NEEDS_REVISION"
            }
        }


# ========================================
# DEMO
# ========================================

async def main():
    """Demonstrate multi-agent collaboration via MCP."""

    # Create MCP server
    server = CodeAnalysisMCPServer()

    # Create coordinator
    coordinator = CoordinatorAgent(server)

    # Run review
    result = await coordinator.review_repository()

    # Show final report
    print("\n" + "="*80)
    print("FINAL REPORT")
    print("="*80)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
