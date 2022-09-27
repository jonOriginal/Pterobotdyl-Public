import requests.exceptions
from pydactyl import PterodactylClient as Dactyl


class Api:
    def __init__(self, address):
        self.address = address

    def __call__(self, api_key):
        api = Dactyl(self.address, api_key)
        try:
            server_details = api.client.servers.list_servers()
        except requests.exceptions.HTTPError:
            raise requests.exceptions.HTTPError
        else:
            return api
