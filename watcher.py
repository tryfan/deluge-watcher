#!/usr/bin/env python

import logging
import time
from os import environ
from pathlib import Path

import yaml
from deluge_client import DelugeRPCClient

logging.basicConfig(level="INFO")


def convert(data):
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, (str, int)):
        return str(data)
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return tuple(map(convert, data))
    if isinstance(data, list):
        return list(map(convert, data))
    if isinstance(data, set):
        return set(map(convert, data))
    return data


cfg = {}
config_file = Path("config.yml")
if config_file.is_file():
    with open("config.yml", "r") as yamlfile:
        yamlcfg = yaml.load(yamlfile, Loader=yaml.BaseLoader)
    cfg['host'] = yamlcfg['host']
    cfg['port'] = int(yamlcfg['port'])
    cfg['username'] = yamlcfg['username']
    cfg['password'] = yamlcfg['password']
    cfg['tracker_whitelist'] = yamlcfg['tracker_whitelist']
    cfg['testing_mode'] = yamlcfg['testing_mode']
    cfg['retry_seconds'] = int(yamlcfg['retry_seconds'])

if environ.get('DELUGE_HOST') is not None:
    cfg['host'] = environ.get('DELUGE_HOST')
if environ.get('DELUGE_PORT') is not None:
    cfg['port'] = int(environ.get('DELUGE_PORT'))
if environ.get('DELUGE_USERNAME') is not None:
    cfg['username'] = environ.get('DELUGE_USERNAME')
if environ.get('DELUGE_PASSWORD') is not None:
    cfg['password'] = environ.get('DELUGE_PASSWORD')
if environ.get('DELUGE_TRACKER_WHITELIST') is not None:
    cfg['tracker_whitelist_csv'] = environ.get('DELUGE_TRACKER_WHITELIST')
if environ.get('DELUGE_TESTING_MODE') is not None:
    cfg['testing_mode'] = environ.get('DELUGE_TESTING_MODE')
if environ.get('DELUGE_RETRY_SECONDS') is not None:
    cfg['retry_seconds'] = int(environ.get('DELUGE_RETRY_SECONDS'))

if 'tracker_whitelist_csv' in cfg:
    items = cfg['tracker_whitelist_csv'].split(',')
    cfg['tracker_whitelist'] = None
    cfg['tracker_whitelist'] = []
    for item in items:
        cfg['tracker_whitelist'].append(item)

client = DelugeRPCClient(
    cfg['host'],
    cfg['port'],
    cfg['username'],
    cfg['password']
)

while True:
    if not client.connected:
        try:
            client.connect()
        except client.Exception:
            logging.error(client.Exception)

    all_torrent_status_bytes = client.core.get_torrents_status(
        {},
        ['name', 'torrent_id', 'paused', 'is_finished', 'state', 'trackers']
    )

    for torrent_id, torrent in all_torrent_status_bytes.items():
        tracker_whitelist = False
        converted_torrent_id = convert(torrent_id)
        converted_torrent = convert(torrent)
        for tracker in converted_torrent['trackers']:
            for whitelisted_tracker in cfg['tracker_whitelist']:
                if whitelisted_tracker.lower() in tracker['url'].lower():
                    tracker_whitelist = True
                    continue
        if tracker_whitelist:
            continue
        if converted_torrent['is_finished'] == 'False':
            continue
        if converted_torrent['paused'] == 'True':
            continue
        print("Found torrent not in whitelist that is active and complete: %s\nid: %s" %
              (converted_torrent['name'], converted_torrent_id))
        if cfg['testing_mode'] == '1':
            print("Action would be to pause torrent %s with id %s" % (converted_torrent['name'], converted_torrent_id))
        else:
            try:
                client.core.pause_torrent([converted_torrent_id])
                print("Paused torrent %s with id %s" % (converted_torrent['name'], converted_torrent_id))
            except client.Exception:
                logging.error(client.Exception)

    time.sleep(cfg['retry_seconds'])
