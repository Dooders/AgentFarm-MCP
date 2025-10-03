#!/usr/bin/env python3
"""Streamlit demo app for the MCP Simulation Server.

This app provides a chat interface to interact with the MCP server using an LLM agent
that can call the 25 available simulation analysis tools.
"""

import json
import os
from typing import Any, Dict, List, Optional

import anthropic
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from agentfarm_mcp import MCPConfig, SimulationMCPServer

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MCP Simulation Server Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .tool-result {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "mcp_server" not in st.session_state:
    # Initialize MCP server
    db_path = os.getenv("DB_PATH", "simulation.db")
    config = MCPConfig.from_db_path(db_path)
    st.session_state.mcp_server = SimulationMCPServer(config)

if "anthropic_client" not in st.session_state:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY environment variable not set!")
        st.stop()
    st.session_state.anthropic_client = anthropic.Anthropic(api_key=api_key)


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get tool definitions in Anthropic format."""
    server = st.session_state.mcp_server
    tools = []
    
    for tool_name in server.list_tools():
        tool = server.get_tool(tool_name)
        schema = tool.parameters_schema.model_json_schema()
        
        # Convert Pydantic schema to Anthropic format
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Build input schema
        input_schema = {
            "type": "object",
            "properties": {},
            "required": required,
        }
        
        for prop_name, prop_info in properties.items():
            input_schema["properties"][prop_name] = {
                "type": prop_info.get("type", "string"),
                "description": prop_info.get("description", ""),
            }
            
            # Add constraints if present
            if "minimum" in prop_info:
                input_schema["properties"][prop_name]["minimum"] = prop_info["minimum"]
            if "maximum" in prop_info:
                input_schema["properties"][prop_name]["maximum"] = prop_info["maximum"]
            if "enum" in prop_info:
                input_schema["properties"][prop_name]["enum"] = prop_info["enum"]
            if "default" in prop_info:
                input_schema["properties"][prop_name]["default"] = prop_info["default"]
        
        tools.append({
            "name": tool_name,
            "description": tool.description.strip(),
            "input_schema": input_schema,
        })
    
    return tools


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP tool and return the result."""
    server = st.session_state.mcp_server
    tool = server.get_tool(tool_name)
    
    try:
        result = tool(**tool_input)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "metadata": {"execution_time_ms": 0},
        }


def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """Format tool result for display."""
    if not result.get("success"):
        return f"❌ Error: {result.get('error', 'Unknown error')}"
    
    data = result.get("data", {})
    exec_time = result.get("metadata", {}).get("execution_time_ms", 0)
    
    # Format based on tool type
    formatted = f"**Tool:** `{tool_name}` (⚡ {exec_time:.1f}ms)\n\n"
    
    # Add data summary
    if isinstance(data, dict):
        # Check for common data patterns
        if "agents" in data:
            formatted += f"📊 Found {len(data['agents'])} agents\n"
        elif "simulations" in data:
            formatted += f"📊 Found {len(data['simulations'])} simulations\n"
        elif "population_summary" in data:
            summary = data["population_summary"]
            formatted += "📈 Population Analysis:\n"
            formatted += f"- Growth Rate: {summary.get('total_growth_rate_percent', 0):.1f}%\n"
            formatted += f"- Peak: {summary.get('peak_population', 0)} agents\n"
        elif "summary" in data:
            formatted += f"📊 Summary: {json.dumps(data['summary'], indent=2)}\n"
    
    return formatted


def visualize_population_data(data: Dict[str, Any]) -> Optional[go.Figure]:
    """Create population dynamics visualization."""
    if "time_series" not in data:
        return None
    
    time_series = data["time_series"]
    if not time_series:
        return None
    
    df = pd.DataFrame(time_series)
    
    fig = go.Figure()
    
    # Add total agents line
    fig.add_trace(
        go.Scatter(
            x=df["step_number"],
            y=df["total_agents"],
            mode="lines+markers",
            name="Total Agents",
            line=dict(color="#1f77b4", width=2),
        )
    )
    
    # Add births and deaths
    fig.add_trace(
        go.Scatter(
            x=df["step_number"],
            y=df["births"],
            mode="lines",
            name="Births",
            line=dict(color="#2ca02c", width=1, dash="dot"),
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["step_number"],
            y=df["deaths"],
            mode="lines",
            name="Deaths",
            line=dict(color="#d62728", width=1, dash="dot"),
        )
    )
    
    fig.update_layout(
        title="Population Dynamics Over Time",
        xaxis_title="Step Number",
        yaxis_title="Count",
        hovermode="x unified",
        template="plotly_white",
        height=400,
    )
    
    return fig


def visualize_agent_data(data: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """Create agent data table."""
    if "agents" not in data:
        return None
    
    agents = data["agents"]
    if not agents:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(agents)
    
    # Select key columns
    columns = ["agent_id", "agent_type", "generation", "birth_time", "death_time"]
    available_cols = [col for col in columns if col in df.columns]
    
    return df[available_cols] if available_cols else df


def render_tool_results(tool_results: List[Dict[str, Any]]) -> None:
    """Render tool results with visualizations and data display."""
    if not tool_results:
        return
    
    for tool_result in tool_results:
        with st.expander(f"🔧 Tool: {tool_result['name']}", expanded=False):
            st.json(tool_result["input"], expanded=False)
            
            result = tool_result["result"]
            if result.get("success"):
                st.success(f"✅ Success ({result['metadata']['execution_time_ms']:.1f}ms)")
                
                # Visualizations
                if tool_result["name"] == "analyze_population_dynamics":
                    fig = visualize_population_data(result.get("data", {}))
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                if "agents" in result.get("data", {}):
                    df = visualize_agent_data(result.get("data", {}))
                    if df is not None and not df.empty:
                        st.dataframe(df, use_container_width=True)
                
                # JSON data
                st.json(result.get("data", {}), expanded=False)
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")


def display_chat_message(message: Dict[str, Any]) -> None:
    """Display a single chat message with optional tool results."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display tool results if present
        if "tool_results" in message:
            render_tool_results(message["tool_results"])


def display_and_process_message(role: str, content: str, tool_results: Optional[List[Dict[str, Any]]] = None) -> None:
    """Display a message in the chat interface and optionally add to history."""
    with st.chat_message(role):
        st.markdown(content)
        
        # Display tool results if present
        if tool_results:
            render_tool_results(tool_results)


def add_message_to_history(role: str, content: str, tool_results: Optional[List[Dict[str, Any]]] = None) -> None:
    """Add a message to chat history with consistent structure."""
    message = {"role": role, "content": content}
    if tool_results is not None:
        message["tool_results"] = tool_results
    st.session_state.messages.append(message)


def handle_user_query(user_input: str) -> None:
    """Unified handler for all user queries (example queries and new input)."""
    # Display user message immediately
    display_and_process_message("user", user_input)
    
    # Get AI response (this will add user message to history internally)
    with st.spinner("Thinking..."):
        response_text, tool_results = chat_with_agent(user_input)
    
    # Display assistant response and add both messages to history
    display_and_process_message("assistant", response_text, tool_results)
    add_message_to_history("user", user_input)
    add_message_to_history("assistant", response_text, tool_results)
    
    st.rerun()


def chat_with_agent(user_message: str) -> tuple[str, List[Dict[str, Any]]]:
    """Send message to LLM agent and get response with tool calls."""
    client = st.session_state.anthropic_client
    tools = get_tool_definitions()
    
    # Build messages including history
    messages = []
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    tool_results = []
    response_text = ""
    
    # Agentic loop - allow multiple tool calls
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )
        
        # Check if we're done
        if response.stop_reason == "end_turn":
            # Extract text response
            for block in response.content:
                if hasattr(block, "text"):
                    response_text += block.text
            break
        
        # Process tool calls
        if response.stop_reason == "tool_use":
            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})
            
            # Execute each tool
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
            tool_results_content = []
            
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input
                tool_use_id = tool_block.id
                
                # Execute tool
                result = execute_tool(tool_name, tool_input)
                
                # Store result for display
                tool_results.append({
                    "name": tool_name,
                    "input": tool_input,
                    "result": result,
                })
                
                # Format for Claude
                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result),
                })
            
            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results_content})
        else:
            # Unexpected stop reason
            break
    
    # Handle cases where we don't get a proper response
    if not response_text.strip():
        if tool_results:
            # We have tool results but no explanation - provide a summary
            response_text = f"I've analyzed your request using {len(tool_results)} tool(s). Here's what I found:\n\n"
            for i, tool_result in enumerate(tool_results, 1):
                tool_name = tool_result['name']
                result = tool_result['result']
                if result.get('success'):
                    response_text += f"{i}. **{tool_name}**: Successfully executed and returned data.\n"
                else:
                    response_text += f"{i}. **{tool_name}**: Failed with error: {result.get('error', 'Unknown error')}\n"
            response_text += "\nPlease check the tool results below for detailed information."
        elif iteration >= max_iterations:
            # Hit max iterations without completion
            response_text = f"I apologize, but I reached the maximum number of processing steps ({max_iterations}) while trying to answer your question. This might indicate a complex query that requires more analysis or there may be an issue with the available tools.\n\nPlease try:\n- Breaking down your question into smaller parts\n- Being more specific about what you're looking for\n- Checking if the simulation data is available"
        else:
            # No tool results and didn't hit max iterations - unexpected case
            response_text = "I apologize, but I encountered an issue while processing your request. Please try rephrasing your question or check if the simulation data is available."
    
    return response_text, tool_results


# Sidebar
with st.sidebar:
    st.title("🤖 MCP Server Demo")

    # Precompute server health once for all tabs
    server = st.session_state.mcp_server
    health = server.health_check()

    # Persist current tab selection across reruns using a simple radio (hidden)
    if "sidebar_active_tab" not in st.session_state:
        st.session_state.sidebar_active_tab = "Tools"

    tabs = ["Tools", "Data", "Settings"]
    # Render tabs and keep track of active tab index by name
    tools_tab, data_tab, settings_tab = st.tabs(tabs)

    with tools_tab:
        st.subheader("💡 Example Queries")
        with st.form(key="example_queries_form", clear_on_submit=False):
            with st.expander("Examples", expanded=st.session_state.get("exp_examples", False)):
                example_queries = [
                    "List all available simulations",
                    "What's the population growth rate in the latest simulation?",
                    "Show me the top 5 agents that survived the longest",
                    "Analyze population dynamics and show a chart",
                    "What were the critical events in the simulation?",
                    "Compare survival rates by generation",
                ]
                selected_query = st.selectbox(
                    "Choose an example",
                    example_queries,
                    index=None,
                    placeholder="Select an example query",
                    key="selected_example_query",
                )
            submitted = st.form_submit_button("Run Example", use_container_width=True)
            if submitted and selected_query:
                st.session_state.example_query = selected_query

        with st.expander("Tool Categories", expanded=st.session_state.get("exp_tool_categories", False)):
            st.markdown("**Available Tools:** 25")
            st.markdown("- Metadata: 4")
            st.markdown("- Query: 6")
            st.markdown("- Analysis: 7")
            st.markdown("- Comparison: 4")
            st.markdown("- Advanced: 2")
            st.markdown("- Health: 2")

    with data_tab:
        st.subheader("Server & Data")
        status_color = "🟢" if health["status"] == "healthy" else "🔴"
        st.write(f"{status_color} {health['status'].upper()}")

        db_status = health["components"].get("database", "unknown")
        st.write(f"**Database:** {db_status}")

        cache_info = health["components"].get("cache", {})
        if isinstance(cache_info, dict):
            st.write(f"**Cache:** Enabled ({cache_info.get('size', 0)} entries)")
            st.write(f"**Hit Rate:** {cache_info.get('hit_rate', 0):.1%}")

        tools_info = health["components"].get("tools", {})
        st.write(f"**Tools Registered:** {tools_info.get('registered', 0)}/{tools_info.get('expected', 25)}")

    with settings_tab:
        st.subheader("Actions")
        with st.form(key="actions_form"):
            clear = st.form_submit_button("🗑️ Clear Chat", use_container_width=True)
            if clear:
                st.session_state.messages = []
                st.rerun()

        with st.expander("Preferences", expanded=False):
            st.checkbox("Expand 'Examples' by default", key="exp_examples")
            st.checkbox("Expand 'Tool Categories' by default", key="exp_tool_categories")


# Main content
st.title("🤖 MCP Simulation Server - Chat Demo")
st.markdown("Ask questions about your simulation data using natural language!")

# Display chat messages
for message in st.session_state.messages:
    display_chat_message(message)

# Handle example query
if hasattr(st.session_state, "example_query"):
    user_input = st.session_state.example_query
    del st.session_state.example_query
    handle_user_query(user_input)

# Chat input
if user_input := st.chat_input("Ask about your simulation data..."):
    handle_user_query(user_input)
