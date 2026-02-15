"""Tests for the featured command."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from mcpt.cli import app
from mcpt.registry import RegistryConfig
from mcpt.registry.featured import FeaturedData, Collection, Section

runner = CliRunner()


@pytest.fixture
def mock_registry_data():
    """Load mock registry data from fixtures."""
    fixture_dir = Path(__file__).parent / "fixtures" / "featured"
    with open(fixture_dir / "registry.json") as f:
        registry = json.load(f)
    with open(fixture_dir / "featured.json") as f:
        featured_raw = json.load(f)
    return registry, featured_raw


@pytest.fixture
def mock_get_featured(mock_registry_data):
    """Mock get_featured to return parsed data."""
    registry, raw = mock_registry_data
    
    # Parse manual structure (simplified logic of get_featured)
    sections = []
    if "featured" in raw:
        sections.append(Section(
            title="Tools of the Week",
            tool_ids=raw["featured"],
            description="Hand-picked tools."
        ))
        
    cols = {}
    for c in raw.get("collections", []):
        cols[c["id"]] = Collection(
            slug=c["id"],
            title=c["name"],
            tool_ids=c["tools"],
            description=c.get("description")
        )
        
    return FeaturedData(
        featured=raw.get("featured", []),
        collections=cols,
        sections=sections
    )


def test_featured_command_default(mock_get_featured, mock_registry_data):
    """Test default featured command output."""
    registry, _ = mock_registry_data
    
    with patch("mcpt.cli.get_registry", return_value=registry), \
         patch("mcpt.cli.get_featured", return_value=mock_get_featured):
        
        result = runner.invoke(app, ["featured", "--plain"])
        
        assert result.exit_code == 0
        assert "TOOLS OF THE WEEK" in result.stdout
        assert "tool-a" in result.stdout
        assert "tool-b" in result.stdout
        assert "STARTER PACK" in result.stdout


def test_featured_command_list(mock_get_featured, mock_registry_data):
    """Test listing collections."""
    registry, _ = mock_registry_data
    
    with patch("mcpt.cli.get_registry", return_value=registry), \
         patch("mcpt.cli.get_featured", return_value=mock_get_featured):
        
        result = runner.invoke(app, ["featured", "--list", "--plain"])
        
        assert result.exit_code == 0
        assert "starter" in result.stdout
        assert "advanced" in result.stdout


def test_featured_command_collection_filter(mock_get_featured, mock_registry_data):
    """Test filtering by collection."""
    registry, _ = mock_registry_data
    
    with patch("mcpt.cli.get_registry", return_value=registry), \
         patch("mcpt.cli.get_featured", return_value=mock_get_featured):
        
        # Filter for starter
        result = runner.invoke(app, ["featured", "--collection", "starter", "--plain"])
        assert result.exit_code == 0
        assert "STARTER PACK" in result.stdout
        assert "tool-a" in result.stdout
        assert "tool-b" not in result.stdout # user filtered view excludes tool-b (in advanced only)
        
        # Filter for advanced
        result = runner.invoke(app, ["featured", "--collection", "advanced", "--plain"])
        assert result.exit_code == 0
        assert "ADVANCED PACK" in result.stdout
        assert "tool-b" in result.stdout


def test_featured_command_json(mock_get_featured, mock_registry_data):
    """Test JSON output."""
    registry, _ = mock_registry_data
    
    with patch("mcpt.cli.get_registry", return_value=registry), \
         patch("mcpt.cli.get_featured", return_value=mock_get_featured):
        
        result = runner.invoke(app, ["featured", "--json"])
        
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "collections" in data
        assert "starter" in data["collections"]
        assert "sections" in data
        assert data["sections"][0]["title"] == "Tools of the Week"


def test_featured_command_no_content():
    """Test handling missing content."""
    with patch("mcpt.cli.get_registry", return_value={"tools": []}), \
         patch("mcpt.cli.get_featured", return_value=None):
        
        result = runner.invoke(app, ["featured"])
        assert result.exit_code == 1
        assert "No featured content available" in result.stdout
