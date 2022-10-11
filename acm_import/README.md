# Playbook and role to automatically import clusters in ACM

Just export `HUBCONFIG` pointing to the hub/acm cluster and `REGIONCONFIG` pointing to the regional cluster.

Then run:
`ansible-playbook ./post.yml`

After a minute or two the cluster will be imported on the hub.

By default it adds the 'clusterGroup=group-one' label. This can be customized with -e clustergroup='foo'
