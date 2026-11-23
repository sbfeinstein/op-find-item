from onepassword import Client, DesktopAuth, Item, ItemShareDuration, ItemShareParams

from op_find_item.models import OutputConfiguration, SearchFilter


async def init_op_client(account_name: str) -> Client:
    return await Client.authenticate(
        auth=DesktopAuth(account_name=account_name),
        integration_name="op-find-item",
        integration_version="v0.0.1",
    )


async def find(
    client: Client,
    term: str,
    search_filter: SearchFilter,
    output_config: OutputConfiguration,
) -> None:
    output_config.on_start()
    with output_config.get_context_manager():
        matches_number = 0

        vaults = await client.vaults.list()

        for vault in vaults:
            if not search_filter.matches_vault(vault.title):
                continue

            item_overviews = await client.items.list(vault.id)
            output_config.on_vault_start(vault, item_overviews)
            for overview in item_overviews:
                item = await client.items.get(vault.id, overview.id)
                for field in item.fields:
                    if not search_filter.matches(field, term):
                        continue
                    matches_number += 1
                    await output_config.on_match(vault, item, field, matches_number)
                output_config.on_item_processed(vault, item)
    output_config.on_end()


async def get_link(
    client: Client,
    item: Item,
) -> str:
    policy = await client.items.shares.get_account_policy(item.vault_id, item.id)
    params = ItemShareParams(
        recipients=None,
        oneTimeOnly=True,
    )
    params.expire_after = ItemShareDuration.ONEHOUR  # to avoid type checker issues based on class internals
    share_link = await client.items.shares.create(
        item,
        policy,
        params,
    )
    return share_link
