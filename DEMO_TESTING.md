# 🧪 Streamlit Demo - Testing Guide

Complete guide for testing the Streamlit demo application.

## 📋 Test Suite Overview

The demo includes comprehensive tests covering:
- **Unit Tests**: Individual function testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Speed and efficiency validation
- **Environment Tests**: Configuration validation

## 🚀 Running Tests

### Quick Test Run

```bash
# Run all demo tests
pytest tests/test_streamlit_demo.py -v

# Run with coverage
pytest tests/test_streamlit_demo.py --cov=streamlit_demo -v

# Run specific test class
pytest tests/test_streamlit_demo.py::TestToolExecution -v

# Run specific test
pytest tests/test_streamlit_demo.py::TestIntegration::test_mcp_server_initialization -v
```

### Full Test Suite

```bash
# Run all MCP server tests + demo tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=agentfarm_mcp --cov=streamlit_demo --cov-report=html
```

## 📊 Test Categories

### 1. Tool Definition Tests
**Location**: `TestToolDefinitionConversion`

Tests conversion of Pydantic schemas to Anthropic format.

```bash
pytest tests/test_streamlit_demo.py::TestToolDefinitionConversion -v
```

**What it tests:**
- Schema structure conversion
- Property mapping
- Required fields handling
- Constraint preservation (min/max/default)

### 2. Tool Execution Tests
**Location**: `TestToolExecution`

Tests tool execution logic and error handling.

```bash
pytest tests/test_streamlit_demo.py::TestToolExecution -v
```

**What it tests:**
- Successful tool execution
- Error handling
- Result structure validation

### 3. Visualization Tests
**Location**: `TestVisualizationHelpers`

Tests data structures for charts and tables.

```bash
pytest tests/test_streamlit_demo.py::TestVisualizationHelpers -v
```

**What it tests:**
- Population data structure
- Agent data structure
- Time series format

### 4. Result Formatting Tests
**Location**: `TestResultFormatting`

Tests result display formatting.

```bash
pytest tests/test_streamlit_demo.py::TestResultFormatting -v
```

**What it tests:**
- Success message formatting
- Error message formatting
- Execution time display

### 5. Environment Tests
**Location**: `TestEnvironmentValidation`

Tests environment variable handling.

```bash
pytest tests/test_streamlit_demo.py::TestEnvironmentValidation -v
```

**What it tests:**
- Missing API key handling
- Present API key validation
- Default database path
- Custom database path

### 6. Message Handling Tests
**Location**: `TestMessageHandling`

Tests chat message structure and handling.

```bash
pytest tests/test_streamlit_demo.py::TestMessageHandling -v
```

**What it tests:**
- Message structure
- Role validation
- Tool results attachment

### 7. Error Handling Tests
**Location**: `TestErrorHandling`

Tests error scenarios and recovery.

```bash
pytest tests/test_streamlit_demo.py::TestErrorHandling -v
```

**What it tests:**
- Database not found errors
- Tool not found errors
- Graceful error recovery

### 8. Integration Tests
**Location**: `TestIntegration`

Tests end-to-end component integration.

```bash
pytest tests/test_streamlit_demo.py::TestIntegration -v
```

**What it tests:**
- MCP server initialization
- Tool schema extraction
- Tool execution
- Health check functionality

### 9. Performance Tests
**Location**: `TestPerformance`

Tests speed and efficiency.

```bash
pytest tests/test_streamlit_demo.py::TestPerformance -v
```

**What it tests:**
- Tool execution speed (< 1s)
- Schema generation speed (< 100ms for all tools)

## 🔍 Manual Testing Checklist

### Pre-Launch Validation

```bash
# 1. Validate file structure
python3 validate_demo.py

# 2. Check Python syntax
python3 -m py_compile streamlit_demo.py

# 3. Verify imports
python3 -c "from agentfarm_mcp import MCPConfig, SimulationMCPServer; print('✅ Imports OK')"

# 4. Run automated tests
pytest tests/test_streamlit_demo.py -v
```

### UI/UX Testing

Once the app is running, manually test:

#### ✅ Basic Functionality
- [ ] App launches without errors
- [ ] Sidebar displays server status
- [ ] Server status shows "healthy"
- [ ] Tool count shows 25/25
- [ ] Cache statistics display correctly

#### ✅ Chat Interface
- [ ] Can type in chat input
- [ ] Messages appear in chat
- [ ] User messages display correctly
- [ ] Assistant responses display correctly
- [ ] Message history preserved

#### ✅ Example Queries
- [ ] Example buttons are clickable
- [ ] Clicking example auto-submits query
- [ ] Each example query works correctly
- [ ] Results display properly

#### ✅ Tool Execution
- [ ] Tools execute successfully
- [ ] Execution times display
- [ ] Tool results are expandable
- [ ] JSON data displays correctly
- [ ] Error messages display for failures

#### ✅ Visualizations
- [ ] Population charts render
- [ ] Charts are interactive (zoom, pan)
- [ ] Data tables display
- [ ] Tables are sortable
- [ ] JSON viewers are collapsible

#### ✅ Error Handling
- [ ] Invalid queries handled gracefully
- [ ] Database errors display properly
- [ ] Tool errors don't crash app
- [ ] Network errors handled

#### ✅ Performance
- [ ] App responds quickly
- [ ] No noticeable lag
- [ ] Charts render smoothly
- [ ] Cache improves speed on repeat queries

## 🧪 Test Scenarios

### Scenario 1: First-Time User
```
1. Launch app
2. See welcome screen
3. Click "List all simulations" example
4. View results
5. Try custom query
6. Explore tool results
```

**Expected**: Smooth onboarding, clear results

### Scenario 2: Population Analysis
```
1. Query: "Analyze population dynamics"
2. View interactive chart
3. Query: "What caused population crash?"
4. See multi-tool response
5. Explore critical events
```

**Expected**: Coherent multi-step analysis

### Scenario 3: Agent Research
```
1. Query: "Show top 10 surviving agents"
2. View data table
3. Query: "Get lifecycle of agent A_089"
4. See detailed history
5. Query: "Build family tree"
```

**Expected**: Deep dive into specific agents

### Scenario 4: Error Recovery
```
1. Query with invalid simulation ID
2. See error message
3. Try valid query
4. Works correctly
5. No state corruption
```

**Expected**: Graceful error handling

## 📈 Performance Benchmarks

### Expected Performance

| Operation | Expected Time | Test Coverage |
|-----------|--------------|---------------|
| Tool execution | < 100ms | ✅ Tested |
| Schema generation | < 100ms for all 25 | ✅ Tested |
| Chart rendering | < 500ms | ⚠️ Manual |
| Page load | < 2s | ⚠️ Manual |
| Query response | < 5s | ⚠️ Manual |

### Running Benchmarks

```bash
# Run performance tests
pytest tests/test_streamlit_demo.py::TestPerformance -v

# With timing details
pytest tests/test_streamlit_demo.py::TestPerformance -v -s
```

## 🐛 Debugging Tests

### Test Failures

If tests fail, check:

1. **Database Connection**
   ```bash
   ls -lh simulation.db
   # Should show file exists and has size > 0
   ```

2. **Dependencies**
   ```bash
   pip list | grep -E "streamlit|plotly|anthropic"
   # All should be installed
   ```

3. **Environment**
   ```bash
   python3 validate_demo.py
   # Should pass all checks
   ```

4. **Verbose Output**
   ```bash
   pytest tests/test_streamlit_demo.py -vv -s
   # Shows detailed output
   ```

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'streamlit'`
```bash
# Solution
pip install -r requirements-streamlit.txt
```

**Issue**: `Database file not found`
```bash
# Solution
ls simulation.db  # Verify file exists
export DB_PATH=simulation.db  # Set path if needed
```

**Issue**: Tests timeout
```bash
# Solution
pytest tests/test_streamlit_demo.py --timeout=60
```

## 📊 Coverage Report

### Generate Coverage

```bash
# Run tests with coverage
pytest tests/test_streamlit_demo.py --cov=streamlit_demo --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Unit Tests**: > 80% coverage
- **Integration Tests**: All critical paths
- **Error Handling**: All error scenarios
- **Performance Tests**: Key operations

## 🔄 Continuous Testing

### Pre-Commit Tests

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pytest tests/test_streamlit_demo.py --quiet
exit $?
```

### CI/CD Integration

For GitHub Actions (`.github/workflows/test-demo.yml`):
```yaml
name: Test Demo
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt -r requirements-streamlit.txt
      - run: pytest tests/test_streamlit_demo.py -v
```

## ✅ Test Checklist

Before deployment, ensure:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance tests meet benchmarks
- [ ] Manual UI testing complete
- [ ] Error scenarios tested
- [ ] Documentation updated
- [ ] Coverage > 80%

## 📚 Related Documentation

- **[validate_demo.py](validate_demo.py)** - Setup validation
- **[DEMO_QUICKSTART.md](DEMO_QUICKSTART.md)** - Quick start guide
- **[STREAMLIT_DEMO_README.md](STREAMLIT_DEMO_README.md)** - Full documentation
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Troubleshooting guide

## 🎯 Testing Best Practices

1. **Run tests before commits**
2. **Test both success and error paths**
3. **Validate performance regularly**
4. **Keep tests up to date with code changes**
5. **Document test failures and solutions**

---

**Test Coverage**: Unit, Integration, Performance  
**Test Count**: 20+ automated tests  
**Status**: ✅ Comprehensive test suite
