# netdevops-performance
Testing performance of Networking Automation Frameworks using GNS3 and its API.

Topology Overview : Basic_topology.png

1. Deploy the scalable network in GNS3 using API.
2. Configure the routers with a custom configuration using Jinja2 templating.
3. Run Ansible playbooks (fetching command outputs, configuring acl & banner) and time them.
4. Run Asyncio scripts using python (fetching command outputs, configuring acl & banner) and time them.
5. Run Nornir scripts using python (fetching command outputs, configuring acl & banner) and time them.
