# Deluge-Watcher

Simple script to watch Deluge and pause any torrents that have completed that are not in your whitelisted seeding trackers. 

Copy `config.yml.dist` to `config.yml` and build using `docker build ./`

Setting `testing_mode: 0` will display torrents that would be paused.