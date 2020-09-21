# Copyright 2014 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import gzip
import io
import json
import subprocess

import requests
from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.metadata.services import base
from cloudbaseinit.osutils import factory as osutils_factory
from cloudbaseinit.osutils.base import BaseOSUtils
from cloudbaseinit.utils import network

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)

MDPATH_METADATA = "/meta-data/v1.json"
MDPATH_USERDATA = "/user-data"
MDPATH_VENDORDATA = "/vendor-data"
MDPATH_PASSWORD = "/vendor-data/password/"

BAD_REQUEST = "bad_request"
TIMEOUT = 3
DIGCF_PRESENT = 2

import struct
from cloudbaseinit.osutils.windows import WindowsUtils
from six.moves import winreg
import win32con
import win32api


class UCloudService(base.BaseHTTPMetadataService, BaseOSUtils):

    """Metadata service for UCloud.
    """
    md = {}
    headers = {}

    def __init__(self):
        super(UCloudService, self).__init__(
            # Note(alexcoman): The base url used by the current metadata
            # service will be updated later by the `_test_api` method.
            base_url=CONF.ucloud.metadata_base_url,
            https_allow_insecure=True)

        self._osutils = osutils_factory.get_os_utils()
        self._metadata_host = CONF.ucloud.metadata_host
        self._crawled_metadata = {}
        self.headers = {
            'Distro-Name': 'windows',
            'UCloud-Magic': '9da657f8-27c3-4505-8934-1d7152477436'
        }
        CONF.set_kms_product_key = CONF.ucloud.set_kms_product_key
        CONF.first_logon_behaviour = CONF.ucloud.first_logon_behaviour
        CONF.username = CONF.ucloud.username

    def load(self):
        """Obtain all the required information."""
        super(UCloudService, self).load()
        """为了防止镜像中DHCP租期过长导致创建的云服务器无法正确的获取地址，需要释放当前的DHCP地址"""
        self.init_dhcp()
        self.md = self._read_metadata()
        """ResetAccount 判断是否要重置密码"""
        #if self.md.get("vendor-data").get("ResetAccount"):
            #self.removeValue()

        """对裸盘进行初始化"""
        self.init_disk()
        if CONF.ucloud.add_metadata_private_ip_route:
            network.check_metadata_ip_route(CONF.ucloud.metadata_base_url)
        try:
            self.get_host_name()

            return True
        except Exception as ex:
            LOG.exception(ex)
            LOG.debug('Metadata not found at URL \'%s\'' %
                      CONF.ucloud.metadata_base_url)
            return False

    def _read_metadata(self):
        # metadata
        mdata = self._read_md_server(MDPATH_METADATA)
        if not mdata:
            raise RuntimeError("unable to read metadata server ")
        mdata = json.loads(mdata.decode("utf-8"))
        # vendordata
        vdata = self._read_md_server(MDPATH_VENDORDATA)
        mdata['vendor-data'] = vdata
        # userdata
        udata = self._read_md_server(MDPATH_USERDATA)
        mdata['user-data'] = udata
        return mdata

    def _read_md_server(self, path):
        mdurl = self._base_url + path

        response = self._get_data(mdurl, headers=self.headers)

        return response

    def _get_data(self, path, headers=None):
        """Getting the required information using metadata service."""
        try:
            response = self._http_request(path, headers=headers)
        except requests.HTTPError as exc:
            if exc.response.status_code == 404:
                raise "NotExistingMetadataException ucloud"
            raise
        except (requests.ConnectionError, requests.Timeout) as exc:
            LOG.exception(exc)
            raise

        return response

    def get_kms_host(self):
        return self.md.get("kms")

    def get_user_data(self):
        vendorData = self.md.get("vendor-data")
        return vendorData

    def get_decoded_user_data(self):
        """Get the decoded user data, if any

        The user data can be gzip-encoded, which means
        that every access to it should verify this fact,
        leading to code duplication.
        """
        user_data = self.get_user_data()
        if user_data and user_data[:2] == self._GZIP_MAGIC_NUMBER:
            bio = io.BytesIO(user_data)
            with gzip.GzipFile(fileobj=bio, mode='rb') as out:
                user_data = out.read()

        return user_data

    def get_instance_id(self, decode=True):
        """Instance name of the virtual machine."""
        return self.md.get('instance-id')

    def get_host_name(self):
        """Hostname of the virtual machine."""
        return self.md.get('local-hostname')

    def get_admin_password(self):
        return "SHu075643@"

    """Password reset related"""
    def _get_config_key_name(self, section):
        key_name = 'SOFTWARE\\Cloudbase Solutions\\Cloudbase-Init\\' + self.md.get('instance-id') + '\\Plugins\\'
        if section:
            key_name += section.replace('/', '\\') + '\\'
        return key_name

    def removeValue(self, section=None):
        key_name = self._get_config_key_name(section)
        key = win32api.RegOpenKey(winreg.HKEY_LOCAL_MACHINE, key_name, 0, win32con.KEY_ALL_ACCESS)
        try:
            win32api.RegDeleteValue(key, "SetUserPasswordPlugin")
            win32api.RegDeleteValue(key, "CreateUserPlugin")
        except:
            pass

    def init_disk(self):
        command = " Get-Disk " \
                  "|Where partitionstyle -eq ‘raw’ " \
                  "|Initialize-Disk -PartitionStyle MBR -PassThru " \
                  "|New-Partition -AssignDriveLetter -UseMaximumSize " \
                  "|Format-Volume -FileSystem NTFS"
        self.run_powershell_command(command)

    def init_dhcp(self):
        command = " ipconfig /release"
        self.run_powershell_command(command)
        command = " ipconfig /renew"
        self.run_powershell_command(command)

    def run_powershell_command(self, command):
        path = subprocess.run('for %x in (powershell.exe) do @echo %~$PATH:x', stdout=subprocess.PIPE, shell=True) \
            .stdout.decode('utf-8').replace('\\', '\\\\')
        command = (path + command).replace("\r\n", "")
        subprocess.run(command)