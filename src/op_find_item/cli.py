"""Console script for op_find_item."""

import asyncio
from io import UnsupportedOperation
from typing import Annotated

import typer
from rich.console import Console

from op_find_item import utils
from op_find_item.models import (
    ConsoleOutputConfiguration,
    JSONOutputConfiguration,
    OutputFormat,
    SearchFilter,
)
from op_find_item.utils import init_op_client

app = typer.Typer()
console = Console()


@app.command()
def main(
    account_name: Annotated[
        str,
        typer.Option(
            envvar="OP_ACCOUNT_NAME",
            help="Your 1Password account_name",
        ),
    ],
    term: Annotated[
        str,
        typer.Argument(
            help="The term to find using a simple match (no wildcards or regex)",
        ),
    ],
    ignore_case: Annotated[
        bool,
        typer.Option(
            help="Ignore case when matching TERM to field values",
        ),
    ] = False,
    include_link: Annotated[
        bool,
        typer.Option(
            help="Include link in the output that expires after opened or 1 hour has passed",
        ),
    ] = False,
    field: Annotated[
        list[str] | None,
        typer.Option(
            help="Field name to search, defaults to all if unset (may set multiple)",
        ),
    ] = None,
    vault: Annotated[
        list[str] | None,
        typer.Option(
            help="Vault name to search, defaults to all if unset (may set multiple)",
        ),
    ] = None,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            show_default=False,
            help="""
                 Choices:

                 console [black]\\[default][/]: Human-readable with progress bars

                 json: JSON output with no progress bars
                 """,
        ),
    ] = OutputFormat.CONSOLE,
) -> None:
    """
    An (unofficial) tool to find 1Password items containing a given search term.

    Requires the 1Password desktop application to be installed.

    All commands require you to supply your 1Password account name using either:
    - the --account-name parameter
    - the [cyan]OP_ACCOUNT_NAME[/] environment variable

    Set the value to one of:
    - The email address associated to your 1Password account
    - The '<account_uuid>' returned by the 1Password CLI command [bold yellow]op account list --format json[/]

    See https://developer.1password.com/docs/sdks/#step-4-initialize-the-sdk for more information.

    Examples of supplying account name:

        op-find-item --account-name '<your 1Password account name>' foo

        [cyan]OP_ACCOUNT_NAME[/]='<your 1Password account name>\' op-find-item foo

    Examples of usage with account name omitted for clarity:

        # Search all vaults and fields for "foo" with a case-sensitive search
        # This will NOT match an item with a field value of "FoO"
        op-find-item foo

        # Search all vaults and fields for "foo" with a case-insensitive search
        # This WILL match an item with a field value of "FoO"
        op-find-item --ignore-case foo

        # Search just the vault name "Family" and fields named "password" or "secret" for "FOO" with a case-sensitive search
        op-find-item --vault "Family" --field "password" --field "secret" FOO

        # Search for "foo" but format the output in JSON rather than the normal human-readable output
        # Also include a shareable one-time use link to the data on 1Password.
        # The link is valid for anybody who has it but can only be viewed once and expires after an hour if not used.
        op-find-item --output-format json --include-link foo
    """  # noqa: E501
    asyncio.run(
        cli(
            account_name=account_name,
            term=term,
            ignore_case=ignore_case,
            include_link=include_link,
            field=field,
            vault=vault,
            output_format=output_format,
        )
    )


async def cli(
    account_name: str,
    term: str,
    ignore_case: bool,
    include_link: bool,
    field: list[str] | None,
    vault: list[str] | None,
    output_format: OutputFormat,
) -> None:
    client = await init_op_client(account_name)

    if output_format == OutputFormat.CONSOLE:
        output_config = ConsoleOutputConfiguration(client, include_link)
    elif output_format == OutputFormat.JSON:
        output_config = JSONOutputConfiguration(client, include_link)
    else:
        raise UnsupportedOperation("Unsupported output format")

    await utils.find(
        client=client,
        term=term,
        search_filter=SearchFilter(
            ignore_case=ignore_case,
            fields=frozenset(field) if field else frozenset(),
            vaults=frozenset(vault) if vault else frozenset(),
        ),
        output_config=output_config,
    )


if __name__ == "__main__":
    app()
