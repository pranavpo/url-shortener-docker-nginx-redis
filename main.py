from flask import Flask
from routes import register_routes
from db import register_db
from redisdb import register_redis_db
# import psycopg2


def create_app():
    app = Flask(__name__)
    conn = register_db()
    redis_conn = register_redis_db()
    register_routes(app, conn, redis_conn)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=3000, debug=True)
