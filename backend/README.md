# Load env vars
set -a; source example.env; set +a

# Run local Postgres container

docker build -t althea-postgres:latest .
docker run -d -p 5432:5432 althea-postgres:latest

# Run app
flask run
gunicorn --worker-class eventlet -w 1 'app:create_app()'