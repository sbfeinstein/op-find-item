"""Tests for the command-line interface."""

from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from typer.testing import CliRunner

from op_find_item import cli as cli_module
from op_find_item.models import ConsoleOutputConfiguration, JSONOutputConfiguration, OutputFormat, SearchFilter

runner = CliRunner()


def test_main_parses_options_and_arguments(monkeypatch):
    mock_cli = AsyncMock()
    monkeypatch.setattr(cli_module, "cli", mock_cli)

    result = runner.invoke(
        cli_module.app,
        [
            "--account-name",
            "user@example.com",
            "--ignore-case",
            "--include-link",
            "--field",
            "password",
            "--field",
            "username",
            "--vault",
            "Personal",
            "--output-format",
            "json",
            "needle",
        ],
    )

    assert result.exit_code == 0, result.output
    mock_cli.assert_awaited_once_with(
        account_name="user@example.com",
        term="needle",
        ignore_case=True,
        include_link=True,
        field=["password", "username"],
        vault=["Personal"],
        output_format=OutputFormat.JSON,
    )


def test_main_reads_account_name_from_environment(monkeypatch):
    mock_cli = AsyncMock()
    monkeypatch.setattr(cli_module, "cli", mock_cli)

    result = runner.invoke(cli_module.app, ["needle"], env={"OP_ACCOUNT_NAME": "user@example.com"})

    assert result.exit_code == 0, result.output
    mock_cli.assert_awaited_once_with(
        account_name="user@example.com",
        term="needle",
        ignore_case=False,
        include_link=False,
        field=None,
        vault=None,
        output_format=OutputFormat.CONSOLE,
    )


def test_main_requires_account_name():
    result = runner.invoke(cli_module.app, ["needle"], env={})

    assert result.exit_code == 2
    assert "account-name" in result.output


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("output_format", "expected_type"),
    [
        (OutputFormat.CONSOLE, ConsoleOutputConfiguration),
        (OutputFormat.JSON, JSONOutputConfiguration),
    ],
)
async def test_cli_initializes_output_and_search(
    monkeypatch,
    output_format,
    expected_type,
):
    client = MagicMock()
    init_client = AsyncMock(return_value=client)
    find = AsyncMock()
    monkeypatch.setattr(cli_module.utils, "find", find)

    await cli_module.cli(
        account_name="user@example.com",
        term="needle",
        ignore_case=True,
        include_link=True,
        field=["password"],
        vault=["Personal"],
        output_format=output_format,
        client_factory=init_client,
    )

    init_client.assert_awaited_once_with("user@example.com")
    find.assert_awaited_once()
    assert find.await_args is not None
    call = find.await_args.kwargs
    assert call["client"] is client
    assert call["term"] == "needle"
    assert call["search_filter"] == SearchFilter(
        ignore_case=True,
        fields=frozenset({"password"}),
        vaults=frozenset({"Personal"}),
    )
    assert isinstance(call["output_config"], expected_type)
    assert call["output_config"].include_link is True


@pytest.mark.asyncio
async def test_cli_rejects_unsupported_output_format(monkeypatch):
    with pytest.raises(cli_module.UnsupportedOperation, match="Unsupported output format"):
        await cli_module.cli(
            account_name="user@example.com",
            term="needle",
            ignore_case=False,
            include_link=False,
            field=None,
            vault=None,
            output_format=cast(OutputFormat, MagicMock()),
            client_factory=AsyncMock(return_value=MagicMock()),
        )
