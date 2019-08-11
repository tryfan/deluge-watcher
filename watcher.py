#!/usr/bin/env python

import time
import logging
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


with open("config.yml", "r") as yamlfile:
    cfg = yaml.load(yamlfile, Loader=yaml.BaseLoader)

client = DelugeRPCClient(
    cfg['deluge']['host'],
    int(cfg['deluge']['port']),
    cfg['deluge']['username'],
    cfg['deluge']['password']
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
            for whitelisted_tracker in cfg['deluge']['tracker_whitelist']:
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
        if cfg['deluge']['testing_mode'] == '1':
            print("Action would be to pause torrent %s with id %s" % (converted_torrent['name'], converted_torrent_id))
        else:
            try:
                client.core.pause_torrent([converted_torrent_id])
                print("Paused torrent %s with id %s" % (converted_torrent['name'], converted_torrent_id))
            except client.Exception:
                logging.error(client.Exception)

    time.sleep(int(cfg['deluge']['retry_seconds']))
