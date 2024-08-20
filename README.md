# vault-actions

For Kubernetes pods that use Vault (or Openbao) as a secret-store, policies, roles, and secrets should be configured before deployment. This chart facilitates configuring these vault objects, and is designed to be included as a sub-chart in the main deployment&mdash;ensuring pre-configuration is coupled with the application's main chart.

## Usage

Define Vault objects (policies, roles, etc.) in `values.yaml`. Pass a wrapped-token for bootstrapping via the `helm install` command:

```bash
helm install myapp-bootstrap vault-actions \
    -f values.yaml \
    --set config.vault.token=<<WRAPPED_SECRET>>
```

Ensure the Vault token is created by a sufficiently privileged user. If no token is supplied, instructions for generation are provided.

# References

1. vault cubbyhole response wrapping: https://developer.hashicorp.com/vault/tutorials/secrets-management/cubbyhole-response-wrapping
