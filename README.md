# Where is my GPU

Discord bot that periodically checks certain e-shops for newest GPUsi (or any other products) and notifies about any change in price or stock. For now only Alza is supported but it is written in such a way that adding new e-shops is easy.

## Requirements

* Docker
* Docker Compose

## Installation

1. Register Discord App + Discord Bot with _Send Message_ and _Embed Links_ permissions.
2. Add bot to your servers + set up its permissions.
3. Obtain Channel ID where you want to post the updates (right-click on channel and select `Copy ID`).
4. Copy `config.template.conf` to `config.dev.conf` and add your Discord Bot token + channel ID into `discord` section.
5. If you are planning to use locally provided Redis then fillout `redis` section with hostname `redis`, port `6379` and database `0`.
6. Set the `scraper.interval` (in seconds) to any sensible value you want. Bot will check the updates every `scraper.interval` seconds.
7. Set up `scraper.interval` targets with URLs of those pages you want to watch. For example if I want to watch RTX3090s then I'll add `{ type = "alza", url = "graficke-karty-nvidia-geforce-rtx3090/18881468.htm" }`.
8. Run `make build` and `make dev`.
