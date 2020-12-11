build:
	@COMPOSE_PROJECT_NAME=wmig docker-compose -f docker/docker-compose.yml up --build --no-start

dev:
	@COMPOSE_PROJECT_NAME=wmig docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up

prod:
	@COMPOSE_PROJECT_NAME=wmig docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d

down:
	@COMPOSE_PROJECT_NAME=wmig docker-compose -f docker/docker-compose.yml down
