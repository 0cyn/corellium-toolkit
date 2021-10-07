import http.client
import json
from .util import prod_model_to_name


class CorelliumAPI:
    TOKEN_ENDPOINT = '/api/v1/tokens'
    DEVICE_ENDPOINT = '/api/v1/instances/'
    INSTANCES_ENDPOINT = '/api/instances'

    FS_ENDPOINT = '/agent/v1/file/device/'

    VPN_TOK_URL = '/api/v1/preauthed-vpn-configs/'
    VPN_DL_URL = '/api/v1/preauthed-vpn-configs/'

    @staticmethod
    def vpn_tok_fetch_url(pid, did):
        return f'/api/v1/projects/{pid}/preauth-vpn-config/{did}.ovpn'

    @staticmethod
    def vpn_file_fetch_url(token, project_name):
        # /api/v1/preauthed-vpn-configs/{token}/Corellium%20VPN%20-%20api.ovpn
        return CorelliumAPI.VPN_DL_URL + '/' + token + f'/Corellium%20VPN%20-%20{project_name}.ovpn'

    @staticmethod
    def device_fetch_ovpn_cfg(url, token, project_id, project_name, device_id):
        tok_fetch_endpoint = CorelliumAPI.vpn_tok_fetch_url(project_id, device_id)
        headers = {
            'authorization': token
        }
        conn = http.client.HTTPSConnection(url)
        conn.request("POST", tok_fetch_endpoint, "", headers)
        token = json.loads(conn.getresponse().read())['token']
        file_endpoint = CorelliumAPI.vpn_file_fetch_url(token, project_name)
        fileconn = http.client.HTTPSConnection(url)
        fileconn.request("GET", file_endpoint, "", {})
        with open(f'Corellium VPN-{project_name}.ovpn', 'wb') as fp:
            fp.write(fileconn.getresponse().read())


    @staticmethod
    def device_list_folder(url, token, device_id, loc):
        full_endpoint = CorelliumAPI.DEVICE_ENDPOINT + device_id + CorelliumAPI.FS_ENDPOINT + loc
        headers = {
            'authorization': token
        }
        # print(full_endpoint)
        conn = http.client.HTTPSConnection(url)
        conn.request("GET", full_endpoint, "", headers)
        return json.loads(conn.getresponse().read())

    @staticmethod
    def device_ctrl(url, token, device_id, endpoint):
        full_endpoint = CorelliumAPI.DEVICE_ENDPOINT + device_id + '/' + endpoint
        headers = {
            'authorization': token
        }
        conn = http.client.HTTPSConnection(url)
        conn.request("POST", full_endpoint, "", headers)

        res = conn.getresponse()
        return res.status == 204
        # no content

    @staticmethod
    def get_token(url, username, password):
        conn = http.client.HTTPSConnection(url)
        payload = json.dumps({"username": username, "password": password})

        headers = {
            'Content-Type': 'application/json'
        }

        conn.request("POST", CorelliumAPI.TOKEN_ENDPOINT, payload, headers)
        res = conn.getresponse()

        return json.loads(res.read())


class APIConnection:

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def device_ls(self, device_id, folder):
        return CorelliumAPI.device_list_folder(self.url, self.token, device_id, folder[1:])

    def device_ctrl(self, device_id, cmd):
        CorelliumAPI.device_ctrl(self.url, self.token, device_id, cmd)

    def get_instances(self):
        conn = http.client.HTTPSConnection(self.url)
        payload = json.dumps({"token": self.token})

        headers = {
            'Content-Type': 'application/json'
        }

        conn.request("POST", "/api/instances", payload, headers)
        res = conn.getresponse()
        return InstancesEndpointData(json.loads(res.read()))


class APIWrapperObjectBase:
    def __init__(self, data):
        self.raw = data


class Domain(APIWrapperObjectBase):
    def __init__(self, data):
        super().__init__(data)
        self.cores = self.raw['cores']
        self.name = self.raw['name']
        self.instances = self.raw['instances']
        self.enterprise = self.raw['licenseType'] == 'enterprise-usage'


class Project(APIWrapperObjectBase):
    def __init__(self, data):
        super().__init__(data)
        self.color = self.raw['color'] # map this to anni color codes?
        self.name = self.raw['name']
        self.id = self.raw['id']
        self.quotas = self.raw['quotas']
        self.quotas_used = self.raw['quotasUsed']
        self.keys = self.raw['keys']
        self.inet_access = self.raw['settings']['internet-access']
        self.version = self.raw['settings']['version']

        self.devices = []


class ProjectsData(APIWrapperObjectBase):
    def __init__(self, data):
        super().__init__(data)
        self.domain = Domain(self.raw['domain'])
        self.projects = []
        projects = self.raw['projects']
        for proj in projects:
            self.projects.append(Project(proj))


class CorelliumDeviceBootOptions(APIWrapperObjectBase):
    def __init__(self, data):
        super().__init__(data)

        self.aprr: bool = self.raw['aprr']
        self.authorized_keys = self.raw['authorizedKeys']
        self.boot_args = self.raw['bootArgs']
        self.cdhashes = self.raw['cdhashes']
        self.ecid = self.raw['ecid']
        self.udid = self.raw['udid']
        self.kernel_patches = self.raw['kernelPatches']
        self.pac = self.raw['pac']
        self.random_seed = self.raw['randomSeed']
        self.restore_boot_args = self.raw['restoreBootArgs']
        self.supports_string_udid = self.raw['supportsStringUDID']

    def str_indent(self, indent=0):
        ret = []
        ret.append('')
        ret.append(f'APRR: {self.aprr}')
        ret.append(f'Authorized Keys: {self.authorized_keys}')
        ret.append(f'PAC: {self.pac}')
        ret.append(f'')
        ret.append(f'Boot Args: {self.boot_args}')
        ret.append(f'CDHashes: {self.cdhashes}')
        ret.append(f'UDID: {self.udid}')
        ret.append(f'ECID: {self.ecid}')
        ret.append(f'SEED: {self.random_seed}')
        ret.append(f'')
        ret.append(f'Kernel Patches: {self.kernel_patches}')
        ret.append(f'')
        prefix = ' ' * indent
        joiner = '\n' + prefix
        return joiner.join(ret)


class CorelliumDevice(APIWrapperObjectBase):
    def __init__(self, data):
        super().__init__(data)

        self.project_id = self.raw['project']

        self.name = self.raw['name']

        if not self.name:
            self.name = prod_model_to_name(self.raw['product'])

        self.os_version = self.raw['os']
        self.os_build = self.raw['osbuild']
        self.product = self.raw['product']

        self.address = self.raw['address']
        self.services_address = self.raw['services']

        self.status = self.raw['status']

        self.patches = self.raw['patches']
        self.boot_options = CorelliumDeviceBootOptions(self.raw['bootOptions'])

        self.id = self.raw['id']
        self.ipsw = self.raw['ipsw']
        self.ipsw_md5 = self.raw['ipsw-md5']

        # is this just always the same?
        self.ipsw_url = self.raw['orig-ipsw-url']

    def ls(self, api_connection: APIConnection, folder):
        if not folder.startswith('/'):
            folder = '/'+folder
        return api_connection.device_ls(self.id, folder)

    def start(self, api_connection: APIConnection):
        api_connection.device_ctrl(self.id, 'start')

    def stop(self, api_connection: APIConnection):
        api_connection.device_ctrl(self.id, 'stop')

    def str_one_line(self):
        return f'{self.name.ljust(10)} | {self.product.ljust(10)} | {self.os_version.ljust(7)} ({self.os_build.ljust(6)}) | {self.status}'

    def __str__(self):
        ret = []
        ret.append('')
        ret.append(f'Device Name: {self.name}')
        ret.append(f'OS Version: {self.os_version}')
        ret.append(f'OS Build: {self.os_build}')
        ret.append(f'Product: {self.product}')
        ret.append('')
        ret.append(f'SSH Address: {self.address}')
        ret.append(f'Services Address: {self.services_address}')
        ret.append(f'')
        ret.append(f'Device Status: {self.status}')
        ret.append(f'')
        ret.append(f'Patches: {self.patches}')
        ret.append(f'Boot Options: {self.boot_options.str_indent(2)}')
        ret.append(f'')
        ret.append(f'ID: {self.id}')
        ret.append(f'IPSW URL: {self.ipsw}')
        return '\n'.join(ret)


class InstancesEndpointData(APIWrapperObjectBase):
    def __init__(self, data):
        super().__init__(data)

        self.projects = {}

        self.project_data = ProjectsData(self.raw['projects'])

        for project in self.project_data.projects:
            self.projects[project.id] = project

        instances: list = self.raw['instances']
        for inst in instances:
            instance = CorelliumDevice(inst)

            self.projects[instance.project_id].devices.append(instance)

