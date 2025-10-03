#!/usr/bin/env python3
"""Validation script for the Streamlit demo app."""

import ast
import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} not found: {filepath}")
        return False


def check_python_syntax(filepath: str) -> bool:
    """Check Python file syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print(f"✅ Valid Python syntax: {filepath}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return False


def main():
    """Run validation checks."""
    print("=" * 60)
    print("MCP Streamlit Demo - Validation")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check required files
    print("📁 Checking required files...")
    files_to_check = [
        ("streamlit_demo.py", "Main Streamlit app"),
        ("requirements-streamlit.txt", "Streamlit requirements"),
        ("DEMO_README.md", "Demo README"),
        (".env.example", "Example environment file"),
        ("setup_streamlit_demo.sh", "Setup script"),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    print()
    
    # Check Python syntax
    print("🐍 Checking Python syntax...")
    if not check_python_syntax("streamlit_demo.py"):
        all_checks_passed = False
    
    print()
    
    # Check for database
    print("💾 Checking database...")
    if check_file_exists("simulation.db", "Simulation database"):
        size_mb = Path("simulation.db").stat().st_size / (1024 * 1024)
        print(f"   Database size: {size_mb:.2f} MB")
    else:
        print("   ⚠️  Warning: No simulation.db found (needed to run demo)")
    
    print()
    
    # Check environment
    print("🔧 Checking environment...")
    if check_file_exists(".env", "Environment file"):
        with open(".env", 'r', encoding='utf-8') as f:
            content = f.read()
            if "ANTHROPIC_API_KEY" in content:
                if "your_anthropic_api_key_here" in content:
                    print("   ⚠️  Warning: ANTHROPIC_API_KEY not set (using placeholder)")
                else:
                    print("   ✅ ANTHROPIC_API_KEY appears to be set")
    else:
        print("   ℹ️  No .env file (can copy from .env.example)")
    
    print()
    
    # Check MCP server structure
    print("🔍 Checking MCP server structure...")
    mcp_files = [
        "agentfarm_mcp/__init__.py",
        "agentfarm_mcp/server.py",
        "agentfarm_mcp/config.py",
    ]
    
    for filepath in mcp_files:
        if not check_file_exists(filepath, f"MCP file"):
            all_checks_passed = False
    
    print()
    
    # Summary
    print("=" * 60)
    if all_checks_passed:
        print("✅ All validation checks passed!")
        print()
        print("📝 Next steps to run the demo:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Install Streamlit deps: pip install -r requirements-streamlit.txt")
        print("   3. Set up .env with your ANTHROPIC_API_KEY")
        print("   4. Run: streamlit run streamlit_demo.py")
    else:
        print("❌ Some validation checks failed")
        print("   Please review the errors above")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
