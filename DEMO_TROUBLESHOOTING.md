# 🔧 Streamlit Demo - Troubleshooting Guide

Comprehensive troubleshooting guide for the MCP Streamlit Demo application.

## 🚨 Common Issues & Solutions

### Installation & Setup Issues

#### Issue: "No module named 'streamlit'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**
```bash
# 1. Install Streamlit requirements
pip install -r requirements-streamlit.txt

# 2. Verify installation
pip list | grep streamlit

# 3. If still failing, install directly
pip install streamlit>=1.28.0 plotly>=5.17.0 anthropic>=0.21.0
```

#### Issue: "No module named 'anthropic'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Solutions:**
```bash
# Install Anthropic SDK
pip install anthropic>=0.21.0

# Verify
python3 -c "import anthropic; print(anthropic.__version__)"
```

#### Issue: "No module named 'agentfarm_mcp'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'agentfarm_mcp'
```

**Solutions:**
```bash
# 1. Install base requirements first
pip install -r requirements.txt

# 2. Install package in development mode
pip install -e .

# 3. Verify
python3 -c "from agentfarm_mcp import MCPConfig; print('✅ OK')"
```

### Configuration Issues

#### Issue: "ANTHROPIC_API_KEY environment variable not set!"

**Symptoms:**
- Red error message in Streamlit app
- App stops immediately

**Solutions:**

**Option 1: .env file**
```bash
# Create .env file
cp .env.example .env

# Edit and add your key
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-api03-...

# Restart app
streamlit run streamlit_demo.py
```

**Option 2: Environment variable**
```bash
# Set for current session
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Or run with variable
ANTHROPIC_API_KEY="sk-ant-api03-..." streamlit run streamlit_demo.py
```

**Option 3: System-wide (Linux/macOS)**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: "Database file not found"

**Symptoms:**
```
ValueError: Database file not found: simulation.db
```

**Solutions:**
```bash
# 1. Check if file exists
ls -lh simulation.db

# 2. If in different location, set DB_PATH
export DB_PATH=/path/to/simulation.db

# 3. Or add to .env
echo "DB_PATH=/path/to/simulation.db" >> .env

# 4. Verify database is readable
sqlite3 simulation.db "SELECT COUNT(*) FROM simulations;"
```

#### Issue: Invalid API Key

**Symptoms:**
- "Invalid API key" error
- Authentication failures

**Solutions:**
```bash
# 1. Verify key format (should start with sk-ant-api03-)
echo $ANTHROPIC_API_KEY

# 2. Get new key from Anthropic Console
# Visit: https://console.anthropic.com

# 3. Test key with curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"user","content":"test"}]}'
```

### Runtime Issues

#### Issue: Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
```bash
# 1. Check what's using port 8501
lsof -i :8501

# 2. Kill the process
kill -9 <PID>

# 3. Or use different port
streamlit run streamlit_demo.py --server.port 8502

# 4. Or specify in run script
streamlit run streamlit_demo.py --server.port 8503
```

#### Issue: App Freezes or Hangs

**Symptoms:**
- Spinner keeps spinning
- No response from Claude
- Browser becomes unresponsive

**Solutions:**

**Check 1: API Rate Limits**
```bash
# Claude may be rate-limited
# Wait a few minutes and try again

# Check API status
curl https://status.anthropic.com
```

**Check 2: Database Lock**
```bash
# Check for database locks
fuser simulation.db

# Close other connections to database
# Restart the app
```

**Check 3: Timeout Settings**
```python
# In streamlit_demo.py, increase timeout
# Around line 178 in chat_with_agent():
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    timeout=60.0,  # Add this line
    tools=tools,
    messages=messages,
)
```

#### Issue: Tool Execution Errors

**Symptoms:**
- "Error executing tool"
- Red error boxes in chat
- Tool calls fail

**Solutions:**

**Check 1: Database Connection**
```bash
# Test database access
python3 -c "
from agentfarm_mcp import MCPConfig, SimulationMCPServer
config = MCPConfig.from_db_path('simulation.db')
server = SimulationMCPServer(config)
print(server.health_check())
"
```

**Check 2: Specific Tool**
```python
# Test individual tool
from agentfarm_mcp import MCPConfig, SimulationMCPServer

config = MCPConfig.from_db_path("simulation.db")
server = SimulationMCPServer(config)

# Try the failing tool
tool = server.get_tool("list_simulations")
result = tool(limit=5)
print(result)
```

**Check 3: Clear Cache**
```python
# Add cache clearing to app
# In sidebar, add button:
if st.button("Clear Server Cache"):
    st.session_state.mcp_server.clear_cache()
    st.success("Cache cleared!")
```

### Visualization Issues

#### Issue: Charts Not Displaying

**Symptoms:**
- Blank space where chart should be
- "Error rendering plot" message

**Solutions:**
```bash
# 1. Verify Plotly version
pip show plotly

# 2. Reinstall if needed
pip install --upgrade plotly>=5.17.0

# 3. Clear browser cache
# Ctrl+Shift+R (hard refresh)

# 4. Try different browser
```

#### Issue: Tables Not Showing

**Symptoms:**
- No data table visible
- Empty dataframe

**Solutions:**
```python
# Check data structure
# In streamlit_demo.py, add debug logging:

if "agents" in result.get("data", {}):
    df = visualize_agent_data(result.get("data", {}))
    if df is not None and not df.empty:
        print(f"DEBUG: Table has {len(df)} rows")  # Add this
        st.dataframe(df, use_container_width=True)
    else:
        print(f"DEBUG: Empty or None dataframe")  # Add this
```

### Performance Issues

#### Issue: Slow Response Times

**Symptoms:**
- Long wait times for responses
- Timeout errors
- Poor user experience

**Solutions:**

**Optimize 1: Enable Caching**
```bash
# In .env, ensure caching is enabled
CACHE_ENABLED=true
CACHE_MAX_SIZE=100
CACHE_TTL_SECONDS=300
```

**Optimize 2: Limit Results**
```python
# When testing, use smaller limits
# Example queries with limits:
"List first 10 simulations"  # Instead of all
"Show 5 agents"  # Instead of 100
```

**Optimize 3: Database Optimization**
```bash
# Optimize database
sqlite3 simulation.db "VACUUM;"
sqlite3 simulation.db "ANALYZE;"
```

#### Issue: High Memory Usage

**Symptoms:**
- App becomes slow over time
- Memory errors
- System lag

**Solutions:**

**Solution 1: Clear Session State**
```python
# Add to sidebar in streamlit_demo.py:
if st.button("Reset Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

**Solution 2: Limit Message History**
```python
# In streamlit_demo.py, limit messages:
MAX_MESSAGES = 50

if len(st.session_state.messages) > MAX_MESSAGES:
    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
```

### UI/UX Issues

#### Issue: Sidebar Not Showing

**Symptoms:**
- Sidebar collapsed or hidden
- Can't see server status

**Solutions:**
```python
# In streamlit_demo.py, ensure:
st.set_page_config(
    page_title="MCP Simulation Server Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",  # This line
)
```

#### Issue: CSS Not Applied

**Symptoms:**
- Styling looks wrong
- Layout issues

**Solutions:**
```bash
# 1. Hard refresh browser
# Ctrl+Shift+R or Cmd+Shift+R

# 2. Clear Streamlit cache
streamlit cache clear

# 3. Restart app with --server.runOnSave
streamlit run streamlit_demo.py --server.runOnSave=true
```

### Integration Issues

#### Issue: Claude Not Responding

**Symptoms:**
- No response from Claude
- Blank assistant messages

**Solutions:**

**Check 1: API Status**
```bash
# Check Anthropic status
curl -I https://api.anthropic.com/v1/messages

# Should return 405 (method not allowed is expected for GET)
```

**Check 2: Request Format**
```python
# Verify message format
messages = [
    {"role": "user", "content": "test"}
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=messages
)
print(response.content)
```

**Check 3: Tool Schema**
```python
# Test tool schema generation
tools = get_tool_definitions()
print(f"Generated {len(tools)} tool definitions")
print(json.dumps(tools[0], indent=2))  # Check first tool
```

#### Issue: Tool Calls Not Working

**Symptoms:**
- Claude responds but doesn't call tools
- No tool execution happening

**Solutions:**

**Debug 1: Check Tool Definitions**
```python
# In streamlit_demo.py, add debug output:
tools = get_tool_definitions()
print(f"DEBUG: {len(tools)} tools available")
for tool in tools[:3]:  # First 3 tools
    print(f"  - {tool['name']}: {tool['description'][:50]}...")
```

**Debug 2: Check Response**
```python
# In chat_with_agent(), add logging:
print(f"DEBUG: Stop reason: {response.stop_reason}")
print(f"DEBUG: Content blocks: {len(response.content)}")
for block in response.content:
    print(f"  - Type: {block.type}")
```

**Debug 3: Verify Model Version**
```python
# Ensure using correct model
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # Check this
    max_tokens=4096,
    tools=tools,
    messages=messages,
)
```

## 🔍 Debugging Tools

### Enable Debug Mode

```python
# Add to top of streamlit_demo.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set via environment
export STREAMLIT_LOGGER_LEVEL=debug
```

### Streamlit Debug Commands

```bash
# Show config
streamlit config show

# Show cache info
streamlit cache clear

# Run with debug flag
streamlit run streamlit_demo.py --logger.level=debug
```

### Validation Script

```bash
# Run comprehensive validation
python3 validate_demo.py

# Check specific components
python3 -c "
from agentfarm_mcp import MCPConfig, SimulationMCPServer
import anthropic
import streamlit
import plotly

print('✅ All imports successful')
print(f'Streamlit: {streamlit.__version__}')
print(f'Plotly: {plotly.__version__}')
print(f'Anthropic: {anthropic.__version__}')
"
```

## 📊 Health Checks

### Quick Health Check

```bash
# Run health check
python3 -c "
from agentfarm_mcp import MCPConfig, SimulationMCPServer
config = MCPConfig.from_db_path('simulation.db')
server = SimulationMCPServer(config)
import json
print(json.dumps(server.health_check(), indent=2))
"
```

### Full System Check

```bash
# 1. Python version
python3 --version  # Should be 3.8+

# 2. Dependencies
pip check

# 3. Database
ls -lh simulation.db
sqlite3 simulation.db "SELECT COUNT(*) FROM simulations;"

# 4. Environment
env | grep -E "ANTHROPIC|DB_PATH"

# 5. Port availability
lsof -i :8501 || echo "Port 8501 available"
```

## 🆘 Getting Help

### Self-Help Resources

1. **Run validation**: `python3 validate_demo.py`
2. **Check logs**: Look in terminal for error messages
3. **Test components**: Use test suite
4. **Read docs**: Check DEMO_QUICKSTART.md and STREAMLIT_DEMO_README.md

### Collect Debug Information

```bash
# Create debug report
cat > debug_report.txt << 'EOF'
=== Environment ===
$(python3 --version)
$(pip list | grep -E "streamlit|anthropic|plotly|fastmcp|sqlalchemy|pydantic")

=== Files ===
$(ls -lh streamlit_demo.py simulation.db .env 2>&1)

=== Health Check ===
$(python3 -c "from agentfarm_mcp import MCPConfig, SimulationMCPServer; config = MCPConfig.from_db_path('simulation.db'); server = SimulationMCPServer(config); import json; print(json.dumps(server.health_check(), indent=2))" 2>&1)

=== Validation ===
$(python3 validate_demo.py 2>&1)
EOF

cat debug_report.txt
```

### Contact Support

Include this information when asking for help:
- Python version
- Operating system
- Error messages (full stack trace)
- Steps to reproduce
- Debug report output

## ✅ Prevention Checklist

Avoid issues by following these steps:

- [ ] Always use virtual environment
- [ ] Install all requirements before running
- [ ] Verify .env file is configured
- [ ] Test with validation script first
- [ ] Check database exists and is readable
- [ ] Use correct Python version (3.8+)
- [ ] Keep dependencies updated
- [ ] Clear cache when switching versions
- [ ] Read error messages carefully
- [ ] Test tools individually before using in app

## 📚 Related Documentation

- **[DEMO_QUICKSTART.md](DEMO_QUICKSTART.md)** - Setup guide
- **[DEMO_TESTING.md](DEMO_TESTING.md)** - Testing guide
- **[STREAMLIT_DEMO_README.md](STREAMLIT_DEMO_README.md)** - Full documentation
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - MCP server troubleshooting

---

**Remember**: Most issues are configuration or environment related. Always start with `python3 validate_demo.py` and check the basics first! 🔧
