import ui_helpers as ui


def test_sidebar_tab_labels():
    labels = ui.get_sidebar_tab_labels()
    assert labels == ["Tools", "Data", "Settings"]
    assert len(labels) == 3


def test_example_queries_contents():
    queries = ui.get_example_queries()
    assert isinstance(queries, list)
    assert len(queries) >= 5
    assert any("simulations" in q.lower() for q in queries)


def test_tool_category_counts_and_total():
    counts = ui.get_tool_category_counts()
    assert set(counts.keys()) == {"Metadata", "Query", "Analysis", "Comparison", "Advanced", "Health"}
    assert all(isinstance(v, int) and v >= 0 for v in counts.values())

    total = ui.get_total_tool_count()
    assert total == sum(counts.values())
    assert total > 0


def test_log_levels():
    levels = ui.get_log_levels()
    assert levels[0] == "All"
    assert "ERROR" in levels
    assert levels == ["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
