# mq.py
import pika, json

QUEUE = "urls"

def get_connection():
    params = pika.ConnectionParameters(host="localhost", port=5672)
    return pika.BlockingConnection(params)

def publish_url(url: str):
    conn = get_connection()
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.basic_publish(exchange="", routing_key=QUEUE, body=url)
    print(f"📤 Sent URL to queue: {url}")
    conn.close()

def consume_urls(callback):
    conn = get_connection()
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)

    def on_message(ch, method, properties, body):
        url = body.decode()
        print(f"📥 Received URL: {url}")
        callback(url)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=QUEUE, on_message_callback=on_message)
    print("Waiting for URLs. Press Ctrl+C to exit.")
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        ch.stop_consuming()
    finally:
        conn.close()

if __name__ == "__main__":
    # simple test: produce then consume
    publish_url("https://news.ycombinator.com")
