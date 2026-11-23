import json
import sys
import textwrap
from contextlib import AbstractContextManager
from dataclasses import dataclass
from enum import Enum
from operator import contains
from types import TracebackType

from onepassword import Client, Item, ItemField, ItemOverview, VaultOverview
from rich.progress import Progress, TaskID

from op_find_item import utils


class OutputFormat(Enum):
    CONSOLE = "console"
    JSON = "json"


class OutputConfiguration:
    client: Client
    include_link: bool

    def __init__(self, client: Client, include_link: bool):
        super().__init__()
        self.client = client
        self.include_link = include_link

    def get_context_manager(self) -> AbstractContextManager:
        return self

    def on_start(self) -> None:
        return

    def on_vault_start(
        self,
        vault_overview: VaultOverview,
        item_overviews: list[ItemOverview],
    ) -> None:
        return

    async def on_match(
        self,
        vault_overview: VaultOverview,
        item: Item,
        field: ItemField,
        match_number: int,
    ) -> None:
        return

    def on_item_processed(
        self,
        vault_overview: VaultOverview,
        item: Item,
    ):
        return

    def on_end(self) -> None:
        return

    def __enter__(self):
        return

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return


class ConsoleOutputConfiguration(OutputConfiguration, AbstractContextManager):
    progress: Progress
    task: TaskID

    @staticmethod
    def get_output_format() -> OutputFormat:
        return OutputFormat.CONSOLE

    def on_vault_start(
        self,
        vault_overview: VaultOverview,
        item_overviews: list[ItemOverview],
    ) -> None:
        self.task = self.progress.add_task(
            f"Searching vault {vault_overview.title}...",
            total=len(item_overviews),
        )

    async def on_match(
        self,
        vault_overview: VaultOverview,
        item: Item,
        field: ItemField,
        match_number: int,
    ) -> None:
        match_str = f"Match found in vault '{vault_overview.title}', item '{item.title}', field '{field.title}'"
        if self.include_link:
            link = await utils.get_link(self.client, item) if self.include_link else None
            match_str += f", link '{link}'"
        self.progress.print(
            match_str,
            highlight=False,
            markup=False,
        )

    def on_item_processed(
        self,
        vault_overview: VaultOverview,
        item: Item,
    ):
        self.progress.advance(self.task)

    def __enter__(self):
        self.progress = Progress()
        self.progress.__enter__()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.progress.__exit__(exc_type, exc_val, exc_tb)


class JSONOutputConfiguration(OutputConfiguration):
    @staticmethod
    def get_output_format() -> OutputFormat:
        return OutputFormat.JSON

    def on_start(self) -> None:
        sys.stdout.write("[")
        sys.stdout.flush()

    async def on_match(
        self,
        vault_overview: VaultOverview,
        item: Item,
        field: ItemField,
        match_number: int,
    ) -> None:
        output_item = OutputItem(
            vault_name=vault_overview.title,
            item_name=item.title,
            field_name=field.title,
            field_type=field.field_type.value.title(),
            link=await utils.get_link(self.client, item) if self.include_link else None,
        )
        output_item_json = json.dumps(
            output_item.__dict__,
            indent=4,
        )
        output_item_padded = textwrap.indent(output_item_json, 4 * " ")
        if match_number == 1:
            output_item_padded = "\n" + output_item_padded
        if match_number > 1:
            output_item_padded = ",\n" + output_item_padded

        sys.stdout.write(output_item_padded)
        sys.stdout.flush()

    def on_end(self) -> None:
        sys.stdout.write("\n]\n")


@dataclass(frozen=True)
class OutputItem:
    vault_name: str
    item_name: str
    field_name: str
    field_type: str
    link: str | None


@dataclass(frozen=True)
class SearchFilter:
    ignore_case: bool
    fields: frozenset[str]
    vaults: frozenset[str]

    def matches(self, field: ItemField, term: str) -> bool:
        if self.fields and not contains(self.fields, field.title):
            return False

        if not self.ignore_case and not contains(field.value, term):
            return False

        return contains(field.value.lower(), term.lower())

    def matches_vault(self, vault: str):
        return not self.vaults or contains(self.vaults, vault)
