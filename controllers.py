from flask import request, jsonify, redirect
import hashlib
import redis


def hello_world():
    return "<p>Hello World</p>"


def is_valid_url(url):
    """
    Check if the URL is valid (not just 'http://domain')
    """
    if not url.startswith(('http://', 'https://')):
        return False
    if len(url) <= 7:  # if URL length is shorter than 'http://'
        return False
    return True


def generate_short_url(original_url):
    """
    Generate a short URL using MD5 hash of the original URL.
    """
    # Generate the MD5 hash of the URL
    md5_hash = hashlib.md5(original_url.encode()).hexdigest()

    # Take the first 6 characters of the MD5 hash to generate the short URL
    short_url = md5_hash[:6]

    return short_url


def check_database(conn, original_url):
    cur = conn.cursor()
    cur.execute(
        "SELECT short_url FROM url_list WHERE original_url = %s", (original_url,))
    result = cur.fetchone()

    if result:
        short_url = result[0]
        return short_url


def get_url(conn, redis_conn):
    # Get the long URL from the POST data
    data = request.json
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required."}), 400

    # Check if the URL is valid
    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL provided."}), 400

    # check for url on redis & if available, return
    try:
        # Check for URL in Redis (handle case where it might not exist)
        short_url = redis_conn.get(original_url.encode())
        if short_url is None:
            print("URL not found in Redis, checking the database...")
        else:
            # Decode the byte object to string
            short_url = short_url
            print("Found in Redis, returning...")
            return jsonify({
                "original_url": original_url,
                "short_url": short_url,
                "source": "redis"
            }), 200

    except redis.exceptions.RedisError as e:
        # Handle any Redis-specific errors (e.g., connection issues)
        print(f"Redis error occurred: {e}")
        # return jsonify({"error": "Error communicating with Redis."}), 500

    # check for url on database, if available, return
    short_url = check_database(conn, original_url)
    if short_url:
        # Storing only the short URL part in Redis
        redis_conn.set(original_url.encode(), short_url.split('/')[-1])
        return jsonify({
            "original_url": original_url,
            "short_url": short_url,
            "source": "database"
        }), 200

    # If not in redis, if not in db, Generate the short URL
    short_url = generate_short_url(original_url)

    print(f"Storing URL: {original_url} with Short URL: {short_url}")
    # Storing only the short URL part in Redis
    redis_conn.set(original_url.encode(), short_url.split('/')[-1])

    # Add to Database
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO url_list (original_url, short_url) VALUES (%s, %s)",
        (original_url, short_url)
    )
    conn.commit()
    cur.close()

    return jsonify({
        "original_url": original_url,
        "short_url": short_url,
        "source": "created"
    }), 201


def redirect_to_url(short_url, conn, redis_conn):
    # Try to get the original URL from Redis first
    original_url = redis_conn.get(short_url.encode())

    if not original_url:
        # If not found in Redis, check in the PostgreSQL database
        original_url = get_original_url_from_db(short_url, conn)

    if not original_url:
        return jsonify({"error": "Short URL not found."}), 404

    # Redirect the user to the original URL
    return redirect(original_url)


def get_original_url_from_db(short_url, conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT original_url FROM url_list WHERE short_url = %s", (short_url,))
    result = cur.fetchone()
    if result:
        return result[0]
    return None
