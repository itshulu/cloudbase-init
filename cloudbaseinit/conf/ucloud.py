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
            cfg.ListOpt(
                'plugins',
                default=[
                    'cloudbaseinit.plugins.common.mtu.MTUPlugin',
                    'cloudbaseinit.plugins.windows.ntpclient'
                    '.NTPClientPlugin',
                    'cloudbaseinit.plugins.common.sethostname'
                    '.SetHostNamePlugin',
                    'cloudbaseinit.plugins.windows.createuser'
                    '.CreateUserPlugin',
                    'cloudbaseinit.plugins.common.networkconfig'
                    '.NetworkConfigPlugin',
                    'cloudbaseinit.plugins.windows.licensing'
                    '.WindowsLicensingPlugin',
                    'cloudbaseinit.plugins.common.sshpublickeys'
                    '.SetUserSSHPublicKeysPlugin',
                    'cloudbaseinit.plugins.windows.extendvolumes'
                    '.ExtendVolumesPlugin',
                    'cloudbaseinit.plugins.common.userdata.UserDataPlugin',
                    'cloudbaseinit.plugins.common.setuserpassword.'
                    'SetUserPasswordPlugin',
                    'cloudbaseinit.plugins.windows.winrmlistener.'
                    'ConfigWinRMListenerPlugin',
                    'cloudbaseinit.plugins.windows.winrmcertificateauth.'
                    'ConfigWinRMCertificateAuthPlugin',
                    'cloudbaseinit.plugins.common.localscripts'
                    '.LocalScriptsPlugin',
                ],
                help='List of enabled plugin classes, '
                     'to be executed in the provided order'),
            cfg.BoolOpt(
                'allow_reboot', default=True,
                help='Enables or disables the BCD auto recovery'),
            cfg.BoolOpt(
                'activate_windows', default=True,
                help='Enables or disables the BCD auto recovery'),
            cfg.StrOpt(
                'first_logon_behaviour', default='no',
                help='Enables or disables the BCD auto recovery'),
        ]

    def register(self):
        """Register the current options to the global ConfigOpts object."""
        group = cfg.OptGroup(self.group_name, title='UCloud Options')
        self._config.register_group(group)
        self._config.register_opts(self._options, group=group)

    def list(self):
        """Return a list which contains all the available options."""
        return self._options
