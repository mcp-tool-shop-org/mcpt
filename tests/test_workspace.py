"""Tests for workspace configuration management."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from mcpt.workspace import (
    MCP_YAML_FILENAME,
    add_tool,
    remove_tool,
    read_config,
    write_config,
    write_default,
    default_yaml,
)


class TestDefaultYaml:
    """Test default YAML generation."""

    def test_default_yaml_structure(self):
        """Test default_yaml creates valid YAML structure."""
        yaml_content = default_yaml("https://example.com/registry.json", "main")
        assert "schema_version" in yaml_content
        assert "name" in yaml_content
        assert "registry" in yaml_content
        assert "tools" in yaml_content
        assert "run" in yaml_content

    def test_default_yaml_is_valid(self):
        """Test default_yaml produces valid YAML."""
        yaml_content = default_yaml("https://example.com/registry.json", "main")
        parsed = yaml.safe_load(yaml_content)
        assert isinstance(parsed, dict)
        assert parsed["schema_version"] == "0.1"


class TestWriteDefault:
    """Test write_default function."""

    def test_write_default_creates_file(self, tmp_path):
        """Test write_default creates mcp.yaml file."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        assert config_path.exists()

    def test_write_default_content_is_valid_yaml(self, tmp_path):
        """Test write_default writes valid YAML."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        config = yaml.safe_load(config_path.read_text())
        assert config["schema_version"] == "0.1"

    def test_write_default_with_custom_registry(self, tmp_path):
        """Test write_default with custom registry source."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path, "https://custom.com/registry.json", "custom-ref")
        config = yaml.safe_load(config_path.read_text())
        assert config["registry"]["source"] == "https://custom.com/registry.json"
        assert config["registry"]["ref"] == "custom-ref"


class TestReadConfig:
    """Test read_config function."""

    def test_read_config_returns_dict(self, tmp_path):
        """Test read_config returns a dictionary."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        config = read_config(config_path)
        assert isinstance(config, dict)

    def test_read_config_has_expected_keys(self, tmp_path):
        """Test read_config returns expected keys."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        config = read_config(config_path)
        assert "schema_version" in config
        assert "name" in config
        assert "registry" in config
        assert "tools" in config


class TestWriteConfig:
    """Test write_config function."""

    def test_write_config_saves_changes(self, tmp_path):
        """Test write_config writes configuration to file."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        config = read_config(config_path)
        config["name"] = "updated-workspace"
        write_config(config_path, config)
        
        updated = read_config(config_path)
        assert updated["name"] == "updated-workspace"

    def test_write_config_preserves_yaml_format(self, tmp_path):
        """Test write_config preserves YAML formatting."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        config = read_config(config_path)
        write_config(config_path, config)
        
        # Should still be readable YAML
        reread = read_config(config_path)
        assert reread is not None


class TestAddTool:
    """Test add_tool function."""

    def test_add_tool_string_format(self, tmp_path):
        """Test add_tool adds tool as string."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        result = add_tool(config_path, "file-compass")
        assert result is True
        
        config = read_config(config_path)
        assert "file-compass" in config["tools"]

    def test_add_tool_with_ref(self, tmp_path):
        """Test add_tool adds tool with git ref."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        result = add_tool(config_path, "file-compass", ref="v1.0.0")
        assert result is True
        
        config = read_config(config_path)
        tools = config["tools"]
        assert any(t.get("id") == "file-compass" and t.get("ref") == "v1.0.0" 
                   for t in tools if isinstance(t, dict))

    def test_add_tool_duplicate_returns_false(self, tmp_path):
        """Test add_tool returns False if tool already exists."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        add_tool(config_path, "file-compass")
        result = add_tool(config_path, "file-compass")
        assert result is False

    def test_add_multiple_tools(self, tmp_path):
        """Test adding multiple different tools."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        add_tool(config_path, "file-compass")
        add_tool(config_path, "tool-scan")
        add_tool(config_path, "voice-soundboard")
        
        config = read_config(config_path)
        assert len(config["tools"]) == 3


class TestRemoveTool:
    """Test remove_tool function."""

    def test_remove_tool_success(self, tmp_path):
        """Test remove_tool removes a tool."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        add_tool(config_path, "file-compass")
        result = remove_tool(config_path, "file-compass")
        assert result is True
        
        config = read_config(config_path)
        assert "file-compass" not in str(config["tools"])

    def test_remove_tool_not_found(self, tmp_path):
        """Test remove_tool returns False if tool not found."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        result = remove_tool(config_path, "nonexistent-tool")
        assert result is False

    def test_remove_tool_with_ref_format(self, tmp_path):
        """Test remove_tool works with tool in ref format."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        add_tool(config_path, "file-compass", ref="v1.0.0")
        result = remove_tool(config_path, "file-compass")
        assert result is True
        
        config = read_config(config_path)
        assert len(config["tools"]) == 0

    def test_remove_tool_preserves_others(self, tmp_path):
        """Test remove_tool preserves other tools."""
        config_path = tmp_path / MCP_YAML_FILENAME
        write_default(config_path)
        
        add_tool(config_path, "file-compass")
        add_tool(config_path, "tool-scan")
        remove_tool(config_path, "file-compass")
        
        config = read_config(config_path)
        assert "tool-scan" in config["tools"]
        assert "file-compass" not in str(config["tools"])
