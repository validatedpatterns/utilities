# Token Generation to bridge UMB with GitHub WebHooks for automated CI-Triggers.

*To generate the token you must be logged on to Red Hat VPN*

## Procedures

### Token Generation

1. browse to: https://one.redhat.com/token-manager/#/umb-bridge
1. enter URL of repo (ex: https://github.com/hybrid-cloud-patterns/multicloud-gitops)
1. Click generate token
1. copy generated token
1. Next open browser to github.com

### GitHub Webhook Creation

1. browse to: github.com/hybrid-cloud-patterns/multicloud-gitops  > settings > webhooks
1. click `add webhook`
1. Payload URL: https://api.enterprise.redhat.com/hydra/umb-bridge/v1/publish
1. Paste the generated token under secret
1. change `Content type` to `application/json`
1. Select your events
1. click `Add webhook`

That's it!

### More Information

[GitHub WebHooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/about-webhooks)

[GitHub Event Types](https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types)
