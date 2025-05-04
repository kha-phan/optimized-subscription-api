# Optimized Subscription Management API

## Setup

### 1. Clone repo
```commandline
git clone https://github.com/kha-phan/optimized-subscription-api.git
cd optimized-subscription-api
```
### 2. Clone `.env` from `env.template` and fill out the values

### 3. Build and Start the Containers
```commandline
docker-compose up -d --build
```

### 4. Access the API
Once the containers are running, API will be accessible at http://localhost:5000

### 5. Run Migrations (if needed)
```commandline
docker-compose exec app flask db init
docker-compose exec app flask db migrate -m "Your migration message"
docker-compose exec app flask db upgrade
```

### 6. Stop the Containers
```commandline
docker-compose down
```


## For details on query optimizations explanation, please refer to [optimization_choices.md](optimization_choices.md)

