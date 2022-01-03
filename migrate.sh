migrate -database "postgres://crawler:crawler@douban-crawler-db:5432/crawler?sslmode=disable&search_path=public" -path /db/migrations up

