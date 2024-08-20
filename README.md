# vault-actions

For Kubernetes pods that use Vault (or Openbao) as a secret-store, policies, roles, and secrets should be configured before deployment. This chart facilitates configuring these vault objects, and is designed to be included as a sub-chart in the main deployment&mdash;ensuring pre-configuration is coupled with the application's main chart.

## Installation

The chart is available in the `jr200` public helm repo.

```
helm repo add jr200 https://jr200.github.io/helm-charts/
```

## Usage

Define Vault objects (policies, roles, etc.) in `values.yaml`. Pass a wrapped-token for bootstrapping via the `helm install` command:

```bash
helm install myapp-bootstrap jr200/vault-actions \
    -f values.yaml \
    --set config.vault.token=<<WRAPPED_SECRET>>
```

Ensure the Vault token is created by a sufficiently privileged user. If no token is supplied, instructions for generation are provided.

## Examples

Example use as a dependent chart is available in a number of `jr200/nats-*` repos.

# References

1. vault cubbyhole response wrapping: https://developer.hashicorp.com/vault/tutorials/secrets-management/cubbyhole-response-wrapping
