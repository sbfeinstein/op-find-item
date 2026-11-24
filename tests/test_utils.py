"""tests for `op_find_item/utils.py`"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from op_find_item import utils
from op_find_item.models import SearchFilter


class MockOutputConfig:
    def __init__(self, client=None, include_link=False):
        self.client = client or MagicMock()
        self.include_link = include_link
        self.calls = []

    def on_start(self):
        self.calls.append(("on_start",))

    def get_context_manager(self):
        return self

    def on_vault_start(self, vault, overviews):
        self.calls.append(("on_vault_start", vault.title, len(overviews)))

    async def on_match(self, vault, item, field, num):
        link = None
        if self.include_link:
            link = await utils.get_link(self.client, item)
        self.calls.append(("on_match", vault.title, item.title, field.title, num, link))

    def on_item_processed(self, vault, item):
        self.calls.append(("on_item_processed", vault.title, item.title))

    def on_end(self):
        self.calls.append(("on_end",))

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass


class TestInitOpClient:
    """Tests for op_find_item.utils.init_op_client"""

    @pytest.mark.asyncio
    @patch("op_find_item.utils.Client", autospec=True)
    async def test_auth_success(self, mock_client):
        actual = await utils.init_op_client("jsmith@op-find-item.com")

        assert actual is not None

        captured_auth = mock_client.authenticate.call_args.kwargs.get("auth")
        assert captured_auth.account_name == "jsmith@op-find-item.com"

        mock_client.authenticate.assert_awaited_once_with(
            auth=captured_auth,
            integration_name="op-find-item",
            integration_version="v0.0.1",
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "account_name",
        [
            "jsmith@op-find-item.com",
            "jsmith",
            "  frank t00m]] ",
            "c.y. - d.ee    ",
        ],
    )
    @patch("op_find_item.utils.Client", autospec=True)
    async def test_account_name_passed_as_is(self, mock_client, account_name):
        await utils.init_op_client(account_name)
        captured_auth = mock_client.authenticate.call_args.kwargs.get("auth")
        assert captured_auth.account_name == account_name

    @pytest.mark.asyncio
    @patch("op_find_item.utils.Client", autospec=True)
    async def test_auth_failure(self, mock_client):
        mock_client.authenticate.side_effect = Exception("No can haz auth!")
        with pytest.raises(Exception, match="No can haz auth!"):
            await utils.init_op_client("jsmith@op-find-item.com")


class TestFind:
    """Tests for op_find_item.utils.find"""

    @pytest.mark.asyncio
    async def test_no_vaults(self):
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[])
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [("on_start",), ("on_end",)]

    @pytest.mark.asyncio
    async def test_vault_filtered_out(self):
        vault = MagicMock()
        vault.title = "vault1"
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset(["other"]))
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [("on_start",), ("on_end",)]

    @pytest.mark.asyncio
    async def test_vault_matching_no_items(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[])
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [("on_start",), ("on_vault_start", "vault1", 0), ("on_end",)]

    @pytest.mark.asyncio
    async def test_no_matching_fields(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field = MagicMock()
        field.title = "field1"
        field.value = "no match here"
        item.fields = [field]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]

    @pytest.mark.asyncio
    async def test_with_match(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field = MagicMock()
        field.title = "field1"
        field.value = "has term here"
        item.fields = [field]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_match", "vault1", "item1", "field1", 1, None),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]

    @pytest.mark.asyncio
    async def test_multiple_matches(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field1 = MagicMock()
        field1.title = "field1"
        field1.value = "has term1"
        field2 = MagicMock()
        field2.title = "field2"
        field2.value = "has term2"
        item.fields = [field1, field2]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_match", "vault1", "item1", "field1", 1, None),
            ("on_match", "vault1", "item1", "field2", 2, None),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]

    @pytest.mark.asyncio
    async def test_field_filtered_out(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field = MagicMock()
        field.title = "field1"
        field.value = "has term"
        item.fields = [field]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(["other"]), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]

    @pytest.mark.asyncio
    async def test_case_sensitive_no_match(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field = MagicMock()
        field.title = "field1"
        field.value = "has TERM"
        item.fields = [field]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=False, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]

    @pytest.mark.asyncio
    async def test_case_sensitive_match(self):
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field = MagicMock()
        field.title = "field1"
        field.value = "has term"
        item.fields = [field]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client)
        search_filter = SearchFilter(ignore_case=False, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_match", "vault1", "item1", "field1", 1, None),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]

    @pytest.mark.asyncio
    @patch("op_find_item.utils.get_link")
    async def test_with_link(self, mock_get_link):
        mock_get_link.return_value = "link1"
        vault = MagicMock()
        vault.title = "vault1"
        vault.id = "id1"
        overview = MagicMock()
        overview.id = "item1"
        item = MagicMock()
        item.title = "item1"
        field = MagicMock()
        field.title = "field1"
        field.value = "has term"
        item.fields = [field]
        client = MagicMock()
        client.vaults.list = AsyncMock(return_value=[vault])
        client.items.list = AsyncMock(return_value=[overview])
        client.items.get = AsyncMock(return_value=item)
        output_config = MockOutputConfig(client=client, include_link=True)
        search_filter = SearchFilter(ignore_case=True, fields=frozenset(), vaults=frozenset())
        await utils.find(client, "term", search_filter, output_config)
        assert output_config.calls == [
            ("on_start",),
            ("on_vault_start", "vault1", 1),
            ("on_match", "vault1", "item1", "field1", 1, "link1"),
            ("on_item_processed", "vault1", "item1"),
            ("on_end",),
        ]
        mock_get_link.assert_awaited_once_with(client, item)
