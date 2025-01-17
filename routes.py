from controllers import hello_world, get_url, redirect_to_url
from functools import partial


def register_routes(app, conn, redis_conn):
    app.add_url_rule("/", "hello_world", partial(hello_world))
    app.add_url_rule("/get_url", "get_url",
                     partial(get_url, conn, redis_conn), methods=['POST'])
    app.add_url_rule("/short_url/<short_url>", "short_url",
                     partial(redirect_to_url, conn=conn, redis_conn=redis_conn), methods=['GET'])
