"""Tests for registry client functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcpt.registry import (
    RegistryConfig,
    get_registry,
    get_registry_status,
    get_tool,
    search_tools,
    load_cached_registry,
    save_cached_registry,
)


class TestRegistryConfig:
    """Test RegistryConfig initialization."""

    def test_registry_config_defaults(self):
        """Test RegistryConfig with default values."""
        config = RegistryConfig()
        assert config.source is not None
        assert config.ref is not None

    def test_registry_config_custom_values(self):
        """Test RegistryConfig with custom values."""
        config = RegistryConfig(source="https://custom.com/registry.json", ref="custom-ref")
        assert config.source == "https://custom.com/registry.json"
        assert config.ref == "custom-ref"


class TestRegistryOperations:
    """Test registry operations."""

    @patch("mcpt.registry.client.fetch_registry")
    def test_get_registry_returns_dict(self, mock_fetch):
        """Test get_registry returns a dictionary."""
        mock_fetch.return_value = {"tools": [{"id": "test-tool"}]}
        registry = get_registry()
        assert isinstance(registry, dict)
        assert "tools" in registry

    @patch("mcpt.registry.client.fetch_registry")
    def test_get_registry_with_force_refresh(self, mock_fetch):
        """Test get_registry with force_refresh parameter."""
        mock_fetch.return_value = {"tools": []}
        get_registry(force_refresh=True)
        mock_fetch.assert_called()

    @patch("mcpt.registry.client.get_registry")
    def test_get_tool_found(self, mock_get_registry):
        """Test get_tool when tool exists."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass", "name": "File Compass"}
            ]
        }
        tool = get_tool("file-compass")
        assert tool is not None
        assert tool["id"] == "file-compass"

    @patch("mcpt.registry.client.get_registry")
    def test_get_tool_not_found(self, mock_get_registry):
        """Test get_tool when tool doesn't exist."""
        mock_get_registry.return_value = {"tools": []}
        tool = get_tool("nonexistent-tool")
        assert tool is None

    @patch("mcpt.registry.client.get_registry")
    def test_search_tools_by_keyword(self, mock_get_registry):
        """Test search_tools finds matching tools."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass", "name": "File Discovery", "tags": ["discovery"]},
                {"id": "tool-compass", "name": "Tool Discovery", "tags": ["discovery"]},
                {"id": "voice-soundboard", "name": "Voice Synthesis", "tags": ["audio"]},
            ]
        }
        results = search_tools("discovery")
        assert len(results) >= 2
        assert any(t["id"] == "file-compass" for t in results)

    @patch("mcpt.registry.client.get_registry")
    def test_search_tools_case_insensitive(self, mock_get_registry):
        """Test search_tools is case insensitive."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "file-compass", "name": "File Discovery", "tags": ["discovery"]},
            ]
        }
        results = search_tools("DISCOVERY")
        assert len(results) > 0

    @patch("mcpt.registry.client.get_registry")
    def test_search_tools_empty_query(self, mock_get_registry):
        """Test search_tools with empty query."""
        mock_get_registry.return_value = {
            "tools": [
                {"id": "tool1"},
                {"id": "tool2"},
            ]
        }
        results = search_tools("")
        assert isinstance(results, list)

    def test_get_registry_status_returns_status(self):
        """Test get_registry_status returns RegistryStatus."""
        from mcpt.registry.client import RegistryStatus
        status = get_registry_status()
        assert isinstance(status, RegistryStatus)


class TestCaching:
    """Test registry caching functionality."""

    def test_load_cached_registry_nonexistent(self, tmp_path):
        """Test load_cached_registry with nonexistent cache."""
        cfg = RegistryConfig(source="https://example.com", ref="test-nonexistent")
        with patch("mcpt.registry.client.registry_cache_path") as mock_path:
            mock_path.return_value = tmp_path / "nonexistent" / "registry.json"
            result = load_cached_registry(cfg)
            assert result is None

    def test_save_and_load_cached_registry(self, tmp_path):
        """Test save_cached_registry writes and load reads back."""
        import json
        cfg = RegistryConfig(source="https://example.com", ref="test-save")
        cache_file = tmp_path / "registry.json"
        test_data = {"tools": [{"id": "test"}]}

        with patch("mcpt.registry.client.registry_cache_path") as mock_path:
            mock_path.return_value = cache_file
            save_cached_registry(cfg, test_data)
            loaded = load_cached_registry(cfg)
            assert loaded == test_data
