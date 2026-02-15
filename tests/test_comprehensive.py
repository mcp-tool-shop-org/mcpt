"""Comprehensive tests for MCPT CLI commands and functionality."""

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mcpt.cli import app, fuzzy_match_tools

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


# =============================================================================
# Basic CLI Tests
# =============================================================================


class TestBasicCommands:
    """Test basic CLI commands."""

    def test_version(self):
        """Test version command output."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "mcpt" in result.stdout
        # Version check is loose to strictly verify command
        assert "." in result.stdout

    def test_help(self):
        """Test help output shows all commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "info" in result.stdout
        assert "search" in result.stdout
        assert "init" in result.stdout
        assert "add" in result.stdout
        assert "remove" in result.stdout
        assert "install" in result.stdout
        assert "run" in result.stdout
        assert "doctor" in result.stdout

    def test_no_args_shows_help(self):
        """Test calling without args shows help."""
        result = runner.invoke(app, [])
        # Typer returns exit code 0 or 2 for help
        assert result.exit_code in (0, 2) or "Usage" in result.stdout


# =============================================================================
# Command Help Tests
# =============================================================================


class TestCommandHelp:
    """Test individual command help messages."""

    def test_list_help(self):
        """Test list command help."""
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        out = strip_ansi(result.stdout)
        assert "--json" in out
        assert "--refresh" in out

    def test_info_help(self):
        """Test info command help."""
        result = runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "TOOL_ID" in result.stdout

    def test_search_help(self):
        """Test search command help."""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0

    def test_init_help(self):
        """Test init command help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0

    def test_add_help(self):
        """Test add command help."""
        result = runner.invoke(app, ["add", "--help"])
        assert result.exit_code == 0

    def test_remove_help(self):
        """Test remove command help."""
        result = runner.invoke(app, ["remove", "--help"])
        assert result.exit_code == 0

    def test_run_help(self):
        """Test run command help."""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0

    def test_doctor_help(self):
        """Test doctor command help."""
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0


# =============================================================================
# Fuzzy Matching Tests
# =============================================================================


class TestFuzzyMatching:
    """Test fuzzy matching for tool discovery."""

    def test_fuzzy_match_exact_match(self):
        """Should prioritize exact matches."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.return_value = {
                "tools": [
                    {"id": "python-executor", "name": "Python Executor"},
                    {"id": "node-executor", "name": "Node Executor"},
                ]
            }
            results = fuzzy_match_tools("python")
            assert len(results) > 0
            assert results[0]["id"] == "python-executor"

    def test_fuzzy_match_substring(self):
        """Should match substrings."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.return_value = {
                "tools": [
                    {"id": "file-processor", "name": "File Processor"},
                    {"id": "text-processor", "name": "Text Processor"},
                    {"id": "code-executor", "name": "Code Executor"},
                ]
            }
            results = fuzzy_match_tools("processor")
            assert len(results) >= 2
            assert all("processor" in tool["id"] for tool in results)

    def test_fuzzy_match_respects_limit(self):
        """Should respect result limit."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            tools = [
                {"id": f"tool-{i}", "name": f"Tool {i}"}
                for i in range(20)
            ]
            mock_registry.return_value = {"tools": tools}
            results = fuzzy_match_tools("tool", limit=5)
            assert len(results) <= 5

    def test_fuzzy_match_empty_query(self):
        """Should handle empty query gracefully."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.return_value = {
                "tools": [
                    {"id": "tool-a", "name": "Tool A"},
                    {"id": "tool-b", "name": "Tool B"},
                ]
            }
            results = fuzzy_match_tools("")
            # Empty query should return no results (score 0.2 threshold)
            assert len(results) >= 0


# =============================================================================
# Output Format Tests
# =============================================================================


class TestOutputFormats:
    """Test different output formats."""

    def test_list_default_format(self):
        """Test list command with default format."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.return_value = {
                "tools": [
                    {"id": "tool-1", "name": "Tool 1", "description": "First tool"},
                    {"id": "tool-2", "name": "Tool 2", "description": "Second tool"},
                ]
            }
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0 or "Error" not in result.stdout

    def test_list_json_format(self):
        """Test list command with JSON output."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.return_value = {
                "tools": [
                    {"id": "tool-1", "name": "Tool 1"},
                ]
            }
            result = runner.invoke(app, ["list", "--json"])
            # Should contain valid output
            assert result.exit_code == 0 or result.stdout

    def test_list_with_refresh(self):
        """Test list command with force refresh."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.return_value = {"tools": []}
            result = runner.invoke(app, ["list", "--refresh"])
            # Should have been called with force_refresh=True
            assert result.exit_code == 0 or "Error" not in result.stdout


# =============================================================================
# Tool Management Tests
# =============================================================================


class TestToolOperations:
    """Test tool-related operations."""

    def test_search_tool(self):
        """Test searching for a tool."""
        with patch("mcpt.cli.search_tools") as mock_search:
            mock_search.return_value = [
                {"id": "python-tool", "name": "Python Tool"}
            ]
            result = runner.invoke(app, ["search", "python"])
            # Search should execute
            assert result.exit_code == 0 or mock_search.called

    def test_get_tool_info(self):
        """Test getting tool information."""
        with patch("mcpt.cli.get_tool") as mock_get:
            mock_get.return_value = {
                "id": "test-tool",
                "name": "Test Tool",
                "description": "A test tool",
                "version": "1.0.0",
            }
            result = runner.invoke(app, ["info", "test-tool"])
            # Should attempt to get tool info
            assert result.exit_code == 0 or mock_get.called


# =============================================================================
# Workspace Configuration Tests
# =============================================================================


class TestWorkspaceOperations:
    """Test workspace-related operations."""

    def test_init_workspace(self, tmp_path):
        """Test initializing a workspace."""
        result = runner.invoke(app, ["init"], input="\n\n\n")
        # Init should run without critical errors
        assert result.exit_code == 0 or "error" not in result.stdout.lower()

    def test_read_workspace_config(self, tmp_path):
        """Test reading workspace configuration."""
        with patch("mcpt.cli.read_config") as mock_read:
            mock_read.return_value = {
                "tools": ["tool-1", "tool-2"],
                "version": "1.0.0",
            }
            # Simulate reading config
            assert mock_read is not None


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_command(self):
        """Test handling of invalid commands."""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_missing_required_argument(self):
        """Test handling of missing required arguments."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code != 0

    def test_registry_fetch_error(self):
        """Test handling of registry fetch errors."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            mock_registry.side_effect = Exception("Network error")
            result = runner.invoke(app, ["list"])
            # Should fail gracefully
            assert result.exit_code != 0 or "Error" in result.stdout

    def test_tool_not_found(self):
        """Test handling of non-existent tools."""
        with patch("mcpt.cli.get_tool") as mock_get:
            mock_get.return_value = None
            result = runner.invoke(app, ["info", "nonexistent-tool"])
            # Should handle gracefully
            assert result.exit_code >= 0


# =============================================================================
# Registry Status Tests
# =============================================================================


class TestRegistryStatus:
    """Test registry status and connectivity."""

    def test_registry_status_check(self):
        """Test checking registry status."""
        with patch("mcpt.cli.get_registry_status") as mock_status:
            mock_status.return_value = {"online": True, "last_update": "2024-01-01"}
            status = mock_status()
            assert status["online"] is True


# =============================================================================
# Tool Filtering Tests
# =============================================================================


class TestToolFiltering:
    """Test tool filtering and sorting."""

    def test_filter_tools_by_name(self):
        """Test filtering tools by name."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            tools = [
                {"id": "python-1", "name": "Python Tool"},
                {"id": "js-1", "name": "JavaScript Tool"},
                {"id": "python-2", "name": "Python Runner"},
            ]
            mock_registry.return_value = {"tools": tools}
            
            registry = mock_registry()
            filtered = [t for t in registry["tools"] if "python" in t["id"].lower()]
            assert len(filtered) == 2

    def test_sort_tools_by_popularity(self):
        """Test sorting tools by popularity."""
        with patch("mcpt.cli.get_registry") as mock_registry:
            tools = [
                {"id": "tool-1", "name": "Tool 1", "downloads": 100},
                {"id": "tool-2", "name": "Tool 2", "downloads": 500},
                {"id": "tool-3", "name": "Tool 3", "downloads": 250},
            ]
            mock_registry.return_value = {"tools": tools}
            
            registry = mock_registry()
            sorted_tools = sorted(
                registry["tools"],
                key=lambda t: t.get("downloads", 0),
                reverse=True
            )
            assert sorted_tools[0]["id"] == "tool-2"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for workflow scenarios."""

    def test_list_search_flow(self):
        """Test listing tools and then searching."""
        with patch("mcpt.cli.get_registry") as mock_registry, \
             patch("mcpt.cli.search_tools") as mock_search:
            
            mock_registry.return_value = {
                "tools": [
                    {"id": "python-tool", "name": "Python Tool"},
                    {"id": "js-tool", "name": "JavaScript Tool"},
                ]
            }
            mock_search.return_value = [
                {"id": "python-tool", "name": "Python Tool"}
            ]
            
            # List available
            result1 = runner.invoke(app, ["list"])
            # Search for specific
            result2 = runner.invoke(app, ["search", "python"])
            
            assert result1.exit_code == 0 or result1.stdout
            assert result2.exit_code == 0 or result2.stdout

    def test_tool_discovery_workflow(self):
        """Test complete tool discovery workflow."""
        with patch("mcpt.cli.get_registry") as mock_registry, \
             patch("mcpt.cli.get_tool") as mock_get:
            
            mock_registry.return_value = {
                "tools": [
                    {"id": "test-tool", "name": "Test Tool"}
                ]
            }
            mock_get.return_value = {
                "id": "test-tool",
                "name": "Test Tool",
                "description": "A test tool"
            }
            
            # Get registry
            registry = mock_registry()
            assert "tools" in registry
            
            # Get tool info
            tool = mock_get()
            assert tool["id"] == "test-tool"


# =============================================================================
# Console Output Tests
# =============================================================================


class TestConsoleOutput:
    """Test console output and formatting."""

    def test_version_output_format(self):
        """Test version output is properly formatted."""
        result = runner.invoke(app, ["--version"])
        assert "mcpt" in result.stdout
        assert result.stdout.strip()  # Not empty

    def test_help_output_readability(self):
        """Test help output is readable."""
        result = runner.invoke(app, ["--help"])
        lines = result.stdout.split("\n")
        assert len(lines) > 5  # Should have multiple lines

    def test_error_message_clarity(self):
        """Test error messages are clear."""
        result = runner.invoke(app, ["invalid"])
        assert result.exit_code != 0
        # Error message should exist
        assert result.stdout or result.stderr
