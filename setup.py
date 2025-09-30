from setuptools import setup, find_packages

setup(
    name="mcp-simulation-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-server=mcp.cli:main",
        ],
    },
)