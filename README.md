# youtube-trending-scraper
Data pipeline for scraping Youtube Video Trending using tools like Kafka, ElasticSearch, and Grafana.

## Setup
1. Create .env file and store your **YOUTUBE API KEY**
```bash
YOUTUBE_API_KEY="your_api_key"
```
2. Create Docker Network (maybe and volume for es)
```bash
# Create network
docker network create kafka-network
```

3. Run Services on Docker
```bash
# Start docker-compose within docker folder
docker compose-up -d
```

4. Terminate Docker Services
```bash
docker compose-down
```