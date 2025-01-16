# Info
Python3 boilerplate code for Queue Management

Currently, available only RabbitMQ

# Installing
1. Init venv:
```bash
python -m venv venv
```
2. Activate venv:
```bash
source venv/bin/activate
```
3. Install packages:
```bash
pip install -r requirements.txt
```
4. Install githooks:
```bash
pre-commit install
```
5. (Optional) Run pre-commit:
```bash
pre-commit run --all-files
```
6. Go to [infra](./infra)
```bash
cd infra
```
7. Run Docker Compose
```bash
docker compose -f docker-compose.rabbitmq.yml up -d --build
```


# Actions
To add dependencies to requirements.txt:
```bash
pipreqs . --force
```

# Testing
```bash
python -m pytest
```
