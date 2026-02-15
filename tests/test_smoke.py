"""Smoke tests for MCPT CLI."""

import re

from typer.testing import CliRunner

from mcpt.cli import app

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "mcpt" in result.stdout


def test_help():
    """Test help output."""
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


def test_list_help():
    """Test list command help."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    out = strip_ansi(result.stdout)
    assert "--json" in out
    assert "--refresh" in out


def test_info_help():
    """Test info command help."""
    result = runner.invoke(app, ["info", "--help"])
    assert result.exit_code == 0
    assert "TOOL_ID" in strip_ansi(result.stdout)


def test_search_help():
    """Test search command help."""
    result = runner.invoke(app, ["search", "--help"])
    assert result.exit_code == 0
    assert "QUERY" in strip_ansi(result.stdout)


def test_init_help():
    """Test init command help."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "--force" in strip_ansi(result.stdout)


def test_run_help():
    """Test run command help."""
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--real" in strip_ansi(result.stdout)
