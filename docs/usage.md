# Usage

Search terms are matched as literal substrings of field values. The default is case-sensitive. Searches include all fields, including password and other secret fields; result output does not include the matched values.

## Basic searches

```sh
# Search all vaults and fields for the case-sensitive term "github"
op-find-item github

# Match regardless of letter case
op-find-item --ignore-case github
```

## Limit the search

Repeat `--vault` and `--field` to include multiple names. Names are matched as provided:

```sh
op-find-item --vault Personal --vault Work --field username --field password github
```

## JSON output and sharing links

JSON output is useful for scripting. It includes the vault, item, field name, and field type, but not the field value:

```sh
op-find-item --output-format json --ignore-case github
```

Adding `--include-link` creates one-time share links to matching items. These links grant access to anyone who has them; read the [authentication and sharing guidance](authentication.md) before using this option.

```sh
op-find-item --output-format json --include-link github
```

Run `op-find-item --help` for all options and examples.
