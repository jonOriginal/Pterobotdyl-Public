from pydactyl import PterodactylClient as Dactyl


class Api:
    def __init__(self, address):
        self.address = address

    def __call__(self, api_key):
        api = Dactyl(self.address, api_key)
        server_details = api.client.servers.list_servers()
        return api
