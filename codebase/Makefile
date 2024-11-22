# psql is a good debugging option: https://www.postgresql.org/docs/current/app-psql.html.
setup-psql:
	apt update; apt install postgresql postgresql-contrib
	systemctl start postgresql

how-to-psql:
	@echo "docker exec -it postgres psql -h localhost -p 5432 -U dncc -d goodsstore"

how-to-relife-db:
	@echo "docker compose down -v"

how-to-stream-log:
	@echo "docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic log-channel --from-beginning"
	@echo "> Remove \`--from-beginning\` if history messages are not needed"
