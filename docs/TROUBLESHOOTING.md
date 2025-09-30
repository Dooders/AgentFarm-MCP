# Troubleshooting Guide

Common issues and solutions for the MCP Simulation Analysis Server.

---

## 🔧 Installation Issues

### Issue: `ModuleNotFoundError: No module named 'mcp'`

**Cause:** Package not installed.

**Solution:**
```bash
cd /workspace/mcp
pip install -e .
```

### Issue: `externally-managed-environment` error

**Cause:** System Python is protected.

**Solution:**
```bash
# Use --break-system-packages (development environment)
pip install -e . --break-system-packages

# Or create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Issue: `ModuleNotFoundError: No module named 'fastmcp'`

**Cause:** Dependencies not installed.

**Solution:**
```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Issues

### Issue: `Database file not found: /path/to/db.sqlite`

**Cause:** Invalid or incorrect database path.

**Solution:**
1. Check the path is correct:
```bash
ls -la /path/to/simulation.db
```

2. Use absolute path:
```bash
python3 -m mcp --db-path /workspace/simulation.db
```

3. Check file permissions:
```bash
chmod 644 /path/to/simulation.db
```

### Issue: `no such table: simulations`

**Cause:** Database doesn't have the expected schema.

**Solution:**
1. Verify database schema:
```python
import sqlite3
conn = sqlite3.connect('/path/to/db.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
```

2. Ensure you're using the correct database file.

### Issue: `database is locked`

**Cause:** Another process is writing to the database.

**Solution:**
1. Close other connections to the database
2. Use read-only mode (default):
```python
config = MCPConfig.from_db_path(db_path)  # read_only=True by default
```

---

## ⚡ Performance Issues

### Issue: Queries taking too long (>1 second)

**Diagnosis:**
```python
result = tool(simulation_id="sim_001")
print(f"Execution time: {result['metadata']['execution_time_ms']}ms")
print(f"From cache: {result['metadata']['from_cache']}")
```

**Solutions:**

1. **Enable caching** (if disabled):
```python
config = MCPConfig.from_db_path(
    db_path,
    cache={"enabled": True, "max_size": 200}
)
```

2. **Use smaller limits:**
```python
# Instead of
tool(simulation_id="sim_001", limit=10000)

# Use
tool(simulation_id="sim_001", limit=100)
```

3. **Use step ranges:**
```python
# Instead of querying all steps
tool(simulation_id="sim_001")

# Query specific range
tool(simulation_id="sim_001", start_step=0, end_step=100)
```

4. **Check database indexes:**
```sql
-- In SQLite
SELECT name FROM sqlite_master WHERE type='index';
```

### Issue: Low cache hit rate

**Diagnosis:**
```python
stats = server.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
```

**Solutions:**

1. **Increase cache size:**
```python
config = MCPConfig.from_db_path(
    db_path,
    cache={"max_size": 500}  # Larger cache
)
```

2. **Increase TTL:**
```python
config = MCPConfig.from_db_path(
    db_path,
    cache={"ttl_seconds": 600}  # 10 minutes
)
```

3. **Use consistent parameters** (cache keys are parameter-based)

---

## 💾 Memory Issues

### Issue: High memory usage

**Diagnosis:**
```bash
# Monitor memory while running
ps aux | grep python
```

**Solutions:**

1. **Reduce cache size:**
```python
config = MCPConfig.from_db_path(
    db_path,
    cache={"enabled": True, "max_size": 50}
)
```

2. **Use smaller result sets:**
```python
# Use pagination instead of large queries
tool(simulation_id="sim_001", limit=100, offset=0)
```

3. **Clear cache periodically:**
```python
server.clear_cache()
```

---

## 🐛 Query Issues

### Issue: No results returned

**Diagnosis:**
```python
result = tool(simulation_id="sim_001", agent_type="BaseAgent")
print(f"Total: {result['data']['total_count']}")
print(f"Returned: {result['data']['returned_count']}")
```

**Solutions:**

1. **Check filters:**
```python
# Remove filters to see all data
result = tool(simulation_id="sim_001")  # No filters
```

2. **Check simulation exists:**
```python
list_tool = server.get_tool("list_simulations")
sims = list_tool()
print([s['simulation_id'] for s in sims['data']['simulations']])
```

3. **Check step range:**
```python
# Make sure range is valid
metrics = server.get_tool("get_simulation_metrics")
result = metrics(simulation_id="sim_001", limit=1)
print(f"Steps available: {result['data']['total_count']}")
```

### Issue: Validation errors

```
ValidationError: limit must be >= 1
```

**Cause:** Invalid parameters.

**Solution:**
Check parameter constraints in API_REFERENCE.md:
- `limit`: 1-1000 for most tools
- `offset`: >= 0
- `step` values: >= 0
- `simulation_ids`: 2-10 for comparisons

---

## 🔍 Tool-Specific Issues

### `compare_simulations`: "List should have at least 2 items"

**Cause:** Need at least 2 simulations to compare.

**Solution:**
```python
# Make sure you have 2+ simulation IDs
tool(simulation_ids=["sim_001", "sim_002"])
```

### `analyze_agent_performance`: "Agent not found"

**Cause:** Invalid agent ID.

**Solution:**
```python
# First, get valid agent IDs
agents_tool = server.get_tool("query_agents")
agents = agents_tool(simulation_id="sim_001", limit=10)

# Use a valid agent ID
agent_id = agents['data']['agents'][0]['agent_id']
perf_tool(simulation_id="sim_001", agent_id=agent_id)
```

### `identify_critical_events`: No events detected

**Cause:** Threshold too high.

**Solution:**
```python
# Lower the threshold
tool(simulation_id="sim_001", threshold_percent=5.0)  # More sensitive
```

---

## 🧪 Testing Issues

### Issue: Tests fail with "database not found"

**Cause:** Test fixtures not created.

**Solution:**
Tests use temporary databases created by pytest fixtures. Make sure pytest is installed:
```bash
pip install pytest pytest-cov
```

### Issue: Import errors in tests

**Cause:** Package not installed in development mode.

**Solution:**
```bash
cd /workspace/mcp
pip install -e .
```

---

## 🔌 Integration Issues

### Issue: Claude Desktop can't connect

**Diagnosis:**
1. Check server starts manually:
```bash
python3 -m mcp --db-path /path/to/db.sqlite
```

2. Check output for errors

**Solutions:**

1. **Use absolute paths** in Claude Desktop config:
```json
{
  "mcpServers": {
    "simulation-analysis": {
      "command": "python3",
      "args": ["-m", "mcp", "--db-path", "/absolute/path/to/simulation.db"]
    }
  }
}
```

2. **Check Python is in PATH:**
```bash
which python3
```

3. **Test with --list-tools first:**
```bash
python3 -m mcp --db-path /path/to/db.sqlite --list-tools
```

### Issue: Tools not appearing in LLM

**Cause:** Server not starting properly.

**Solution:**
Check Claude Desktop logs:
- macOS: `~/Library/Logs/Claude/`
- Look for MCP server errors

---

## 📊 Data Issues

### Issue: "No data found for specified range"

**Cause:** Step range doesn't contain data.

**Solution:**
```python
# First check available steps
metrics_tool = server.get_tool("get_simulation_metrics")
result = metrics_tool(simulation_id="sim_001", limit=1)

if result["data"]["metrics"]:
    first_step = result["data"]["metrics"][0]["step_number"]
    
    # Query last steps
    result = metrics_tool(simulation_id="sim_001")
    last_step = result["data"]["metrics"][-1]["step_number"]
    
    print(f"Steps available: {first_step} to {last_step}")
```

### Issue: Unexpected `None` values in results

**Cause:** Data not recorded for that field.

**Solution:**
This is normal - not all fields are populated for all records. Check for None:
```python
for agent in result['data']['agents']:
    if agent['death_time'] is not None:
        print(f"Agent died at step {agent['death_time']}")
    else:
        print("Agent is alive")
```

---

## 🛡️ Security Issues

### Issue: "Read-only mode not enforced"

**Diagnosis:**
```python
print(f"Read-only: {server.config.database.read_only}")
```

**Solution:**
Currently using application-level read-only (no write operations in tools). For database-level enforcement, file permissions can be used:
```bash
chmod 444 /path/to/simulation.db
```

---

## 🔄 Cache Issues

### Issue: Getting stale data

**Cause:** Cache TTL too long.

**Solution:**
```python
# Reduce TTL
config = MCPConfig.from_db_path(
    db_path,
    cache={"ttl_seconds": 60}  # 1 minute instead of 5
)

# Or disable cache
config = MCPConfig.from_db_path(
    db_path,
    cache={"enabled": False}
)

# Or clear cache manually
server.clear_cache()
```

### Issue: Cache not working

**Diagnosis:**
```python
stats = server.get_cache_stats()
print(f"Enabled: {stats['enabled']}")
print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
```

**Solution:**
Make sure cache is enabled:
```python
config = MCPConfig.from_db_path(
    db_path,
    cache={"enabled": True}
)
```

---

## 📝 Logging Issues

### Issue: Too much log output

**Solution:**
```bash
# Reduce log level
python3 -m mcp --db-path /path/to/db.sqlite --log-level WARNING
```

Or in code:
```python
config = MCPConfig.from_db_path(
    db_path,
    server={"log_level": "WARNING"}
)
```

### Issue: Need more debugging info

**Solution:**
```bash
# Enable debug logging
python3 -m mcp --db-path /path/to/db.sqlite --log-level DEBUG
```

---

## 🆘 Getting Help

### Before Asking for Help

1. **Check the documentation:**
   - README.md
   - QUICK_START.md
   - API_REFERENCE.md (this file)
   - STATUS.md

2. **Run the tests:**
```bash
python3 -m pytest tests/ -v
```

3. **Try the demos:**
```bash
python3 demo_all_tools.py
```

4. **Check server starts:**
```bash
python3 -m mcp --db-path /workspace/simulation.db --list-tools
```

### Debug Checklist

- [ ] Package installed (`pip install -e .`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database file exists and is readable
- [ ] Using absolute paths
- [ ] Tried with `--log-level DEBUG`
- [ ] Checked logs for error messages
- [ ] Verified simulation ID exists
- [ ] Tested with demo scripts

---

## 🔬 Advanced Debugging

### Enable SQL logging

```python
# In database_service.py, change echo=False to echo=True
engine = create_engine(..., echo=True)
```

This will print all SQL queries.

### Check cache keys

```python
# See what's being cached
stats = server.get_cache_stats()
print(f"Cache size: {stats['size']}")

# Clear and test
server.clear_cache()
result = tool(...)  # Should be slow
result = tool(...)  # Should be fast (cached)
```

### Inspect tool schemas

```python
tool = server.get_tool("query_agents")
schema = tool.get_schema()
print(schema)  # See parameter requirements
```

---

## 💡 Best Practices

### 1. Always Check Success

```python
result = tool(...)

if result["success"]:
    # Process data
    data = result["data"]
else:
    # Handle error
    error = result["error"]
    print(f"Error: {error['message']}")
```

### 2. Use Appropriate Tools

- **Browsing:** Use `list_*` tools
- **Details:** Use `get_*` tools
- **Analysis:** Use `analyze_*` tools
- **Comparison:** Use `compare_*` tools

### 3. Start Simple

```python
# Start with simple queries
tool(simulation_id="sim_001", limit=10)

# Then add filters as needed
tool(simulation_id="sim_001", agent_type="BaseAgent", limit=10)
```

### 4. Monitor Performance

```python
# Check execution times
print(f"Time: {result['metadata']['execution_time_ms']}ms")

# Check cache effectiveness
stats = server.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
```

---

## 📊 Common Error Messages

### "Simulation not found: sim_XYZ"

- Simulation doesn't exist in database
- Check spelling of simulation_id
- Use `list_simulations` to see available IDs

### "ValidationError: limit must be >= 1"

- Parameter out of range
- Check API_REFERENCE.md for valid ranges
- Most limits: 1-1000

### "Query execution failed"

- Database error occurred
- Check database file is accessible
- Check database isn't corrupted
- Enable DEBUG logging to see details

### "List should have at least 2 items"

- `compare_simulations` needs 2+ simulations
- Provide at least 2 simulation IDs

---

## 🎯 Quick Fixes

### Reset everything:

```python
# Clear cache
server.clear_cache()

# Close and recreate server
server.close()
server = SimulationMCPServer(config)
```

### Verify basic functionality:

```python
# Test simplest tool
list_tool = server.get_tool("list_simulations")
result = list_tool(limit=1)
print(f"Success: {result['success']}")
```

### Check database connection:

```python
# Verify database is accessible
with server.db_service.get_session() as session:
    from mcp.models.database_models import Simulation
    count = session.query(Simulation).count()
    print(f"Simulations in database: {count}")
```

---

## 📞 Still Need Help?

1. **Check STATUS.md** - Known issues and current capabilities
2. **Review test files** - Working examples in `tests/` directory
3. **Run demos** - `demo_all_tools.py` for comprehensive test
4. **Check logs** - Enable DEBUG logging for details

---

**Most Common Issues:**
1. Wrong database path (use absolute paths)
2. Package not installed (run `pip install -e .`)
3. Dependencies missing (run `pip install -r requirements.txt`)
4. Invalid parameters (check API_REFERENCE.md)

**Quick Test:**
```bash
cd /workspace/mcp
python3 -m mcp --db-path /workspace/simulation.db --list-tools
```

If this works, your installation is correct!