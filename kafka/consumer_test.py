# ============================================
# RESTAURANT ORDERING SYSTEM -- KAFKA CONSUMER TEST
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

import json
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
TOPICS       = ["orders", "payments", "inventory", "feedback"]

def create_consumer(topic):
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=f"restaurant-{topic}-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

def consume_orders():
    print("Listening to ORDERS topic...")
    consumer = create_consumer("orders")
    for msg in consumer:
        order = msg.value
        print(f"ORDER  | Table {order['table_id']} | "
              f"{order['item_name']} x{order['quantity']} | "
              f"Rs.{order['amount']} | {order['payment_method']}")

def consume_payments():
    print("Listening to PAYMENTS topic...")
    consumer = create_consumer("payments")
    for msg in consumer:
        pay = msg.value
        status_icon = "✓" if pay["status"] == "success" else "✗"
        print(f"PAYMENT {status_icon} | Order {pay['order_id']} | "
              f"Rs.{pay['amount']} | Ref: {pay['transaction_ref']}")

def consume_all():
    print("=" * 55)
    print("Restaurant Kafka Consumer -- Monitoring all topics")
    print("=" * 55)
    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="restaurant-monitor-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    for msg in consumer:
        topic = msg.topic.upper().ljust(12)
        data  = msg.value
        if msg.topic == "orders":
            print(f"[{topic}] Table {data.get('table_id')} | "
                  f"{data.get('item_name')} | Rs.{data.get('amount')}")
        elif msg.topic == "payments":
            print(f"[{topic}] Order {data.get('order_id')} | "
                  f"{data.get('status').upper()} | {data.get('transaction_ref')}")
        elif msg.topic == "inventory":
            print(f"[{topic}] {data.get('item_name')} | "
                  f"Used: {data.get('quantity_used')}")
        elif msg.topic == "feedback":
            print(f"[{topic}] Order {data.get('order_id')} | "
                  f"Rating: {'★' * data.get('rating', 0)} | {data.get('comment')}")

if __name__ == "__main__":
    consume_all()
