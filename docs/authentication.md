# Account authentication

The CLI authenticates through the 1Password desktop app using the official 1Password SDK. Install the desktop app, sign in, and unlock it before searching. The CLI does not ask for or store your account password, Secret Key, or a service-account token.

You must provide the account name with `--account-name` or the `OP_ACCOUNT_NAME` environment variable. Use the email address for your account or the account UUID shown by:

```sh
op account list --format json
```

Pass the account name on a single invocation:

```sh
op-find-item --account-name "name@example.com" example
```

Or set the environment variable for the current shell:

```sh
export OP_ACCOUNT_NAME="name@example.com"
op-find-item example
```

Avoid putting credentials in scripts or source control. The account name identifies the account; authentication and access are still handled by the unlocked desktop app.

## Sharing links

By default, results show the vault, item, and matching field names, not the matched field values. This permits searching password and other secret fields without printing those values in the results.

The optional `--include-link` creates a one-time share link for each matching item. Anyone who obtains a link can view the shared item once; unused links expire after one hour. Use this option only when you intend to share, and treat output containing links as sensitive.
