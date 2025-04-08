# Biocentral public_hub_services
Microservice to provide open functionality for the biocentral hub server

## Local Deployment

```shell
# 1. Install Docker
# 2. Run Redis via Docker
docker run --name redis-leaderboard -p 6380:6379 -d redis:7.4.1
# Optionally: Run redis commander for debug view in browser
docker run --name redis-commander -d --env REDIS_HOSTS=local:redis:6379 --link plm-leaderboard-redis:redis -p 8081:8081 rediscommander/redis-commander:latest
# Remove the containers if they are no longer needed
docker rm redis-commander
docker rm plm-leaderboard-redis
```