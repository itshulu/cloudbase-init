# Copyright 2014 Cloudbase Solutions Srl
# Copyright 2012 Mirantis Inc.
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

import requests
from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.metadata.services import base
from cloudbaseinit.metadata.services import baseopenstackservice as baseos
from cloudbaseinit.utils import network

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)

DSNAME = "UCloud"
MDURL = "http://100.80.80.80"
MDPATH_METADATA = "/meta-data/v1.json"
MDPATH_USERDATA = "/user-data"
MDPATH_VENDORDATA = "/vendor-data"
MDCACHE_FILE = "/usr/local/ucloud/.cache/metadata.json"
RETRY_WAITSECOND = 5


class UCloudService(base.BaseHTTPMetadataService, baseos.BaseOpenStackService):
    _POST_PASSWORD_MD_VER = '2013-04-04'

    def __init__(self):
        super(UCloudService, self).__init__(
            base_url=CONF.ucloud.metadata_base_url,
            https_allow_insecure=True)
        self.headers = {
            'Distro-Name': 'windows',
            'UCloud-Magic': '9da657f8-27c3-4505-8934-1d7152477436'
        }
        self._enable_retry = True

    def load(self):
        super(UCloudService, self).load()
        if CONF.openstack.add_metadata_private_ip_route:
            network.check_metadata_ip_route(CONF.ucloud.metadata_base_url)

        try:
            self._get_meta_data()
            return True
        except Exception:
            LOG.debug('Metadata not found at URL \'%s\'' %
                      CONF.ucloud.metadata_base_url)
            return False

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
                print("shulu")
            raise
        except (requests.ConnectionError, requests.Timeout) as exc:
            LOG.exception(exc)
            raise

        return response


