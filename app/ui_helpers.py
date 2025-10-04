"""Pure UI helper functions for the Streamlit demo.

These functions are intentionally side-effect free so they can be unit tested
without importing Streamlit or the full app module.
"""
from typing import Dict, List


def get_sidebar_tab_labels() -> List[str]:
    """Return the ordered labels for the left sidebar tabs."""
    return ["Tools", "Data", "Settings"]


def get_example_queries() -> List[str]:
    """Return curated example queries shown in the sidebar."""
    return [
        "List all available simulations",
        "What's the population growth rate in the latest simulation?",
        "Show me the top 5 agents that survived the longest",
        "Analyze population dynamics and show a chart",
        "What were the critical events in the simulation?",
        "Compare survival rates by generation",
    ]


def get_tool_category_counts() -> Dict[str, int]:
    """Return counts of tools by category used for sidebar summary."""
    return {
        "Metadata": 4,
        "Query": 6,
        "Analysis": 7,
        "Comparison": 4,
        "Advanced": 2,
        "Health": 2,
    }


def get_total_tool_count() -> int:
    """Return total number of available tools."""
    return sum(get_tool_category_counts().values())


def get_log_levels() -> List[str]:
    """Return ordered log levels including 'All'."""
    return ["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
