"""Tests for `op_find_item/models.py`"""

import io
import json
from runpy import run_module
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from onepassword import Item, ItemField, ItemOverview, VaultOverview

from op_find_item.models import (
    ConsoleOutputConfiguration,
    JSONOutputConfiguration,
    OutputConfiguration,
    OutputFormat,
    SearchFilter,
)


class TestOutputConfiguration:
    """Tests for op_find_item.models.OutputConfiguration"""

    def test_output_configuration_base(self):
        client = MagicMock()
        config = OutputConfiguration(client, include_link=False)
        vault = MagicMock()
        item = MagicMock()

        assert config.get_context_manager() is config
        assert config.on_start() is None
        assert config.on_vault_start(vault, []) is None
        assert config.on_item_processed(vault, item) is None
        assert config.on_end() is None
        assert config.__enter__() is None
        assert config.__exit__(None, None, None) is None
        assert config.client is client
        assert config.include_link is False


class TestConsoleOutputConfiguration:
    """Tests for op_find_item.models.ConsoleOutputConfiguration"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("include_link", [False, True])
    @patch("op_find_item.models.Progress")
    @patch("op_find_item.utils.get_link", new_callable=AsyncMock)
    async def test_console_output_configuration(self, mock_get_link, mock_progress, include_link):
        client = MagicMock()
        progress = MagicMock()
        mock_progress.return_value = progress
        config = ConsoleOutputConfiguration(client, include_link=include_link)
        mock_get_link.return_value = "https://example.test/share"
        vault = MagicMock()
        vault.title = "Personal"
        item = MagicMock()
        item.title = "Email"
        field = MagicMock()
        field.title = "password"

        config.__enter__()
        config.on_vault_start(
            cast(VaultOverview, vault), [cast(ItemOverview, object()), cast(ItemOverview, object())]
        )
        await config.on_match(cast(VaultOverview, vault), cast(Item, item), cast(ItemField, field), 1)
        config.on_item_processed(cast(VaultOverview, vault), cast(Item, item))
        config.__exit__(None, None, None)

        assert config.get_output_format() is OutputFormat.CONSOLE
        progress.add_task.assert_called_once_with("Searching vault Personal...", total=2)
        progress.advance.assert_called_once_with(config.task)
        progress.print.assert_called_once_with(
            "Match found in vault 'Personal', item 'Email', field 'password'"
            + (", link 'https://example.test/share'" if include_link else ""),
            highlight=False,
            markup=False,
        )
        if include_link:
            mock_get_link.assert_awaited_once_with(client, item)
        else:
            mock_get_link.assert_not_awaited()


class TestJSONOutputConfiguration:
    """Tests for op_find_item.models.JSONOutputConfiguration"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("include_link", [False, True])
    @patch("op_find_item.models.sys.stdout", new_callable=io.StringIO)
    @patch("op_find_item.utils.get_link", new_callable=AsyncMock)
    async def test_json_output_configuration(self, mock_get_link, stdout, include_link):
        client = MagicMock()
        config = JSONOutputConfiguration(client, include_link=include_link)
        mock_get_link.return_value = "https://example.test/share"
        vault = MagicMock()
        vault.title = "Personal"
        item = MagicMock()
        item.title = "Email"
        field = MagicMock()
        field.title = "password"
        field.field_type = MagicMock()
        field.field_type.value = "password"

        config.on_start()
        await config.on_match(
            cast(VaultOverview, vault),
            cast(Item, item),
            cast(ItemField, field),
            1,
        )
        await config.on_match(
            cast(VaultOverview, vault),
            cast(Item, item),
            cast(ItemField, field),
            2,
        )
        config.on_end()

        assert config.get_output_format() is OutputFormat.JSON
        results = json.loads(stdout.getvalue())
        assert results == [
            {
                "vault_name": "Personal",
                "item_name": "Email",
                "field_name": "password",
                "field_type": "Password",
                "link": "https://example.test/share" if include_link else None,
            },
            {
                "vault_name": "Personal",
                "item_name": "Email",
                "field_name": "password",
                "field_type": "Password",
                "link": "https://example.test/share" if include_link else None,
            },
        ]
        assert "field_value" not in results[0]
        if include_link:
            assert mock_get_link.await_count == 2
        else:
            mock_get_link.assert_not_awaited()


class TestSearchFilter:
    """Tests for op_find_item.models.SearchFilter"""

    def test_search_filter_matches_field_and_vault_names_exactly(self):
        search_filter = SearchFilter(
            ignore_case=False,
            fields=frozenset({"Password"}),
            vaults=frozenset({"Personal"}),
        )
        field = MagicMock()
        field.title = "Password"
        field.value = "SecretValue"

        assert search_filter.matches(cast(ItemField, field), "Secret")
        assert not search_filter.matches(cast(ItemField, field), "secret")
        filtered_field = MagicMock()
        filtered_field.title = "password"
        filtered_field.value = "SecretValue"
        assert not search_filter.matches(cast(ItemField, filtered_field), "Secret")
        assert search_filter.matches_vault("Personal")
        assert not search_filter.matches_vault("personal")


class TestModule:
    """Tests for the op_find_item module itself"""

    @patch("op_find_item.cli.app")
    def test_module_entry_point_invokes_cli(self, app):
        run_module("op_find_item.__main__", run_name="__main__")

        app.assert_called_once_with()
