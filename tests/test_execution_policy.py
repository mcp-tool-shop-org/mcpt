
from typer.testing import CliRunner
from mcpt.cli import app
from unittest.mock import patch, MagicMock
from pathlib import Path
import yaml
import json

runner = CliRunner()

def test_execution_blocked_missing_capability():
    """Test that execution is blocked when capabilities are missing."""
    with runner.isolated_filesystem():
        runner.invoke(app, ["init"])
        
        with patch("mcpt.cli.get_tool") as mock_tool:
            mock_tool.return_value = {
                "id": "unsafe-tool",
                "name": "Unsafe Tool",
                "capabilities": ["network"],
                "install": {"type": "git", "url": "http://example.com"}
            }
            
            # Run without grant
            result = runner.invoke(app, ["run", "unsafe-tool", "--mode", "restricted"])
            assert result.exit_code != 0
            assert "Execution Blocked" in result.stdout
            assert "network" in result.stdout

def test_execution_allowed_with_grant():
    """Test that execution is allowed when capabilities are granted."""
    with runner.isolated_filesystem():
        runner.invoke(app, ["init"])
        
        with patch("mcpt.cli.get_tool") as mock_tool:
             mock_tool.return_value = {
                "id": "safe-tool",
                "name": "Safe Tool",
                "capabilities": ["network"],
                "install": {"type": "git", "url": "http://example.com"}
            }
             
             # Add tool first (required for granting)
             runner.invoke(app, ["add", "safe-tool"])
             
             # Grant capability
             result = runner.invoke(app, ["grant", "safe-tool", "network"])
             assert result.exit_code == 0
             assert "Granted" in result.stdout
             
             # Run
             result = runner.invoke(app, ["run", "safe-tool", "--mode", "restricted"])
             assert result.exit_code == 0
             assert "Execution Blocked" not in result.stdout
             assert "Executing safe-tool" in result.stdout

def test_check_command():
    """Test check command output."""
    with runner.isolated_filesystem():
        runner.invoke(app, ["init"])
        
        with patch("mcpt.cli.get_tool") as mock_tool:
            mock_tool.return_value = {
                "id": "test-tool",
                "capabilities": ["network"],
                "install": {"type": "git", "url": "http://example.com"}
            }
            
            # Check without adding
            result = runner.invoke(app, ["check", "test-tool"])
            assert "Preflight Check" in result.stdout
            assert "Added to Workspace: No" in result.stdout
            assert "Missing Grants" in result.stdout
            
            # Add and grant
            runner.invoke(app, ["add", "test-tool"])
            runner.invoke(app, ["grant", "test-tool", "network"])
            
            result = runner.invoke(app, ["check", "test-tool"])
            assert "Added to Workspace: Yes" in result.stdout
            assert "Capabilities: All granted" in result.stdout

def test_lock_file_creation():
    """Test that install creates a lock file."""
    with runner.isolated_filesystem():
        runner.invoke(app, ["init"])
        
        with patch("mcpt.cli.get_tool") as mock_tool, \
             patch("subprocess.run") as mock_run:
            
            mock_tool.return_value = {
                "id": "test-tool",
                "install": {
                    "type": "git", 
                    "url": "http://example.com",
                    "default_ref": "main"
                }
            }
            
            # Mock successful pip install
            mock_run.return_value.stdout = "Successfully installed"
            mock_run.return_value.returncode = 0
            
            result = runner.invoke(app, ["install", "test-tool"])
            assert result.exit_code == 0
            
            # Check lock file
            assert Path("mcp.lock.yaml").exists()
            content = Path("mcp.lock.yaml").read_text()
            assert "test-tool" in content
            assert "installed_at" in content
