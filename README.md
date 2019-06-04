# Production usage

Run `python install.py VPROTECT_REST_API_URL` on the destination server.
if the URL is not specified, `http://localhost:8080/api` will be used by default.


# Development

See https://docs.openstack.org/horizon/latest/contributor/quickstart.html#setup.
This plugin should be cloned in `openstack_dashboard`, which is inside the horizon folder (that means the file structure should be the same as in Horizon, since this plugin is just an extension).