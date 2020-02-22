from __future__ import unicode_literals, division, absolute_import

import logging
import requests
import json

from flexget import db_schema, plugin
from flexget.config_schema import process_config
from flexget.event import event
from flexget.manager import Session
from flexget.entry import Entry

log = logging.getLogger('synology')

class Synology(object):
    schema = {
        'type': 'object',
        'properties': {
            'host': {'type': 'string'},
            'port': {'type': 'integer'},
            'username': {'type': 'string'},
            'password': {'type': 'string'},
            'secure': {'type': 'boolean'},
            'verify': {'type': 'boolean'}
        },
        'required': ['host', 'username', 'password'],
        'additionalProperties': False
    }

    def prepare_config(self, config):
        config.setdefault('port', 5001)
        config.setdefault('secure', True)
        config.setdefault('verify', False)
        return config

    def base_url(self, config):
        protocol = "https" if config['secure'] else "http"
        return protocol+"://"+config['host']+":"+str(config['port'])+"/webapi/"

    def on_task_output(self, task, config):
        if not config.get('enabled', True):
            return
        if not task.accepted:
            return
        # don't add when learning
        if task.options.learn:
            return

        config = self.prepare_config(config)

        session = requests.Session()
        session.verify = config['verify']
        api = self.api_info(config, session)
        self.login(config, session, api)

        try:
            for entry in task.accepted:
                try:
                    self.add_torrent(config, session, api, entry)
                except Exception as e:
                    entry.fail()
                    log.exception('Exception while writing: %s' % e)
        finally:
            self.logout(config, session, api)

    def api_info(self, config, session):
        url = self.base_url(config) + "query.cgi?api=SYNO.API.Info&version=1&method=query"
        log.debug("Fetching API Info %s" % url)
        response = session.get(url)
        response.raise_for_status()
        return response.json()['data']

    def login(self, config, session, api):
        url = (self.base_url(config) + api['SYNO.API.Auth']['path'] +
               "?api=SYNO.API.Auth" +
               "&version=" + str(api['SYNO.API.Auth']['maxVersion']) +
               "&method=login" +
               "&session=DownloadStation" +
               "&account=" + config['username'] +
               "&passwd=" + config['password'])
        log.debug("Login")
        response = session.get(url)
        response.raise_for_status()
        log.debug("Login Successful")

    def logout(self, config, session, api):
        url = (self.base_url(config) + api['SYNO.API.Auth']['path'] +
               "?api=SYNO.API.Auth" +
               "&version=" + str(api['SYNO.API.Auth']['maxVersion']) +
               "&method=logout")
        log.debug("Logout")
        response = session.get(url)
        response.raise_for_status()

    def add_torrent(self, config, session, api, entry):
        url = self.base_url(config) + api['SYNO.DownloadStation.Task']['path']
        payload = {
            "api": "SYNO.DownloadStation.Task",
            "version": str(api['SYNO.DownloadStation.Task']['maxVersion']),
            "method": "create",
            "uri": entry['url']
        }
        log.info("Adding torrent %s" % entry['url'])
        response = session.post(url, data=payload)
        response.raise_for_status()

@event('plugin.register')
def register_plugin():
    plugin.register(Synology, 'synology', api_ver=2)

