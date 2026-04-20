# ============================================
# RESTAURANT ORDERING SYSTEM -- KAFKA PRODUCER
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"

MENU_ITEMS = [
    {"menu_item_id": 1, "name": "Paneer Butter Masala", "category": "Main Course", "price": 220},
    {"menu_item_id": 2, "name": "Chicken Biryani",      "category": "Main Course", "price": 280},
    {"menu_item_id": 3, "name": "Masala Dosa",          "category": "Breakfast",   "price": 120},
    {"menu_item_id": 4, "name": "Veg Fried Rice",       "category": "Main Course", "price": 160},
    {"menu_item_id": 5, "name": "Mango Lassi",          "category": "Beverages",   "price": 80},
    {"menu_item_id": 6, "name": "Gulab Jamun",          "category": "Dessert",     "price": 60},
    {"menu_item_id": 7, "name": "Butter Naan",          "category": "Bread",       "price": 40},
    {"menu_item_id": 8, "name": "Dal Tadka",            "category": "Main Course", "price": 150},
    {"menu_item_id": 9, "name": "Cold Coffee",          "category": "Beverages",   "price": 90},
    {"menu_item_id": 10,"name": "Veg Burger",           "category": "Snacks",      "price": 110},
]

PAYMENT_METHODS = ["UPI", "Cash", "Credit Card", "Debit Card", "Wallet"]
SECTIONS        = ["Ground Floor", "First Floor", "Rooftop", "Outdoor"]
LOYALTY_TIERS   = ["bronze", "silver", "gold", "platinum"]

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def generate_order():
    item     = random.choice(MENU_ITEMS)
    quantity = random.randint(1, 5)
    return {
        "order_id":       random.randint(10000, 99999),
        "table_id":       random.randint(1, 20),
        "customer_id":    random.randint(1, 500),
        "menu_item_id":   item["menu_item_id"],
        "item_name":      item["name"],
        "category":       item["category"],
        "quantity":       quantity,
        "amount":         round(item["price"] * quantity, 2),
        "payment_method": random.choice(PAYMENT_METHODS),
        "section":        random.choice(SECTIONS),
        "loyalty_tier":   random.choice(LOYALTY_TIERS),
        "staff_id":       random.randint(1, 15),
        "entry_time":     datetime.now().isoformat(),
        "status":         "placed"
    }

def generate_payment(order):
    return {
        "order_id":        order["order_id"],
        "payment_method":  order["payment_method"],
        "amount":          order["amount"],
        "status":          random.choice(["success", "success", "success", "failed"]),
        "transaction_ref": f"TXN{random.randint(100000, 999999)}",
        "timestamp":       datetime.now().isoformat()
    }

def generate_inventory_update(order):
    return {
        "menu_item_id": order["menu_item_id"],
        "item_name":    order["item_name"],
        "quantity_used": order["quantity"],
        "timestamp":    datetime.now().isoformat()
    }

def generate_feedback(order):
    return {
        "order_id":    order["order_id"],
        "customer_id": order["customer_id"],
        "rating":      random.randint(1, 5),
        "comment":     random.choice([
            "Excellent food!",
            "Good taste, slow service",
            "Average experience",
            "Will visit again!",
            "Too spicy for my taste"
        ]),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("Restaurant Kafka Producer started -- sending orders...")
    order_count = 0
    while True:
        order = generate_order()

        producer.send("orders",     value=order)
        producer.send("payments",   value=generate_payment(order))
        producer.send("inventory",  value=generate_inventory_update(order))

        if random.random() < 0.4:
            producer.send("feedback", value=generate_feedback(order))

        order_count += 1
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Order #{order_count} sent -- "
              f"{order['item_name']} x{order['quantity']} = Rs.{order['amount']}")

        time.sleep(random.uniform(0.5, 2.0))
