# Deluge-Watcher

Simple script to watch Deluge and pause any torrents that have completed that are not in your whitelisted seeding trackers. 

Copy `config.yml.dist` to `config.yml` and build using `docker build ./`

Setting `testing_mode: 1` will display torrents that would be paused.

## Docker Compose

Check the sample `docker-compose.yml` file for a sample config