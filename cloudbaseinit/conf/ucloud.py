# Copyright 2017 Cloudbase Solutions Srl
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


"""Config options available for the UCloud metadata service."""

from oslo_config import cfg

from cloudbaseinit.conf import base as conf_base
from cloudbaseinit import constant
from cloudbaseinit.conf.default import GlobalOptions
from oslo_log import log as oslo_logging
LOG = oslo_logging.getLogger(__name__)


class UCloudOptions(conf_base.Options):
    """Config options available for the UCloud metadata service."""

    def __init__(self, config):
        super(UCloudOptions, self).__init__(config, group="ucloud")
        self._options = [
            cfg.StrOpt(
                "metadata_base_url", default="http://100.80.80.80",
                help="The URL where the service looks for metadata",
                deprecated_name="ucloud_metadata_base_url",
                deprecated_group="DEFAULT"),
            cfg.BoolOpt(
                "add_metadata_private_ip_route", default=True,
                help="Add a route for the metadata ip address to the gateway",
                deprecated_name="ucloud_add_metadata_private_ip_route",
                deprecated_group="DEFAULT"),
            cfg.StrOpt(
                "metadata_host", default="100.80.80.80",
                help="The metadata server host",
                deprecated_name="ucloud_metadata_host",
                deprecated_group="DEFAULT"),
            cfg.IntOpt(
                "password_server_port", default=80,
                help="The port number used by the Password Server."
            ),
            cfg.BoolOpt(
                'set_kms_product_key', default=True,
                help='Sets the KMS product key for this operating system'),
            cfg.StrOpt(
                'first_logon_behaviour',
                default=constant.NEVER_CHANGE,
                choices=constant.LOGON_PASSWORD_CHANGE_OPTIONS,
                help='Control the behaviour of what happens at '
                     'next logon. If this option is set to `always`, '
                     'then the user will be forced to change the password '
                     'at next logon. If it is set to '
                     '`clear_text_injected_only`, '
                     'then the user will have to change the password only if '
                     'the password is a clear text password, coming from the '
                     'metadata. The last option is `no`, when the user is '
                     'never forced to change the password.'),
            cfg.StrOpt(
                'username', default='Administrator', help='User to be added to the '
                                                          'system or updated if already existing'),

        ]

    def register(self):
        """Register the current options to the global ConfigOpts object."""
        group = cfg.OptGroup(self.group_name, title='UCloud Options')
        self._config.register_group(group)
        self._config.register_opts(self._options, group=group)

    def list(self):
        """Return a list which contains all the available options."""
        return self._options
