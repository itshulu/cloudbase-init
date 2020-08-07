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

from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.metadata.services import base
from cloudbaseinit.utils import network

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)

DSNAME            = "UCloud"
MDURL             = "http://100.80.80.80"
MDPATH_METADATA   = "/meta-data/v1.json"
MDPATH_USERDATA   = "/user-data"
MDPATH_VENDORDATA = "/vendor-data"
MDCACHE_FILE      = "/usr/local/ucloud/.cache/metadata.json"
RETRY_WAITSECOND  = 5


class UCloudService(base.BaseHTTPMetadataService):
    _metadata_version = '2020-08-07'

    def __init__(self):
        super(UCloudService,self).__init__(
            base_url=CONF.ucloud.metadata_base_url,
            https_allow_insecure=True,
            https_ca_bundle=CONF.ucloud.https_ca_bundle)

    def _get_data(self, path):
        return super(self)._get_data(path)
