# Production usage

Run `python install.py VPROTECT_REST_API_URL VPROTECT_USER VPROTECT_USER_PASSWORD` on the destination server.
e.g. `python install.py http://localhost:8080/api admin vPr0tect`

and then run `systemctl restart httpd` to apply changes by restarting Horizon on OpenStack.

# Development

See https://docs.openstack.org/horizon/latest/contributor/quickstart.html#setup.
This plugin should be cloned in `openstack_dashboard`, which is inside the horizon folder (that means the file structure should be the same as in Horizon, since this plugin is just an extension).