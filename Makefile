.PHONY: mongo-shell
mongo-shell:
	docker-compose exec mongo mongo --host mongodb://user:pass@mongo/db
