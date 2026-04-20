# ============================================
# RESTAURANT ORDERING SYSTEM -- FASTAPI
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random
import uvicorn

app = FastAPI(
    title="Restaurant Ordering System API",
    description="Real-time REST API for Restaurant Ordering System | KIIT University",
    version="1.0.0"
)

# ── Mock Data ───────────────────────────────────────────

MENU = [
    {"menu_item_id": 1,  "name": "Paneer Butter Masala", "category": "Main Course", "price": 220, "is_available": True},
    {"menu_item_id": 2,  "name": "Chicken Biryani",      "category": "Main Course", "price": 280, "is_available": True},
    {"menu_item_id": 3,  "name": "Masala Dosa",          "category": "Breakfast",   "price": 120, "is_available": True},
    {"menu_item_id": 4,  "name": "Veg Fried Rice",       "category": "Main Course", "price": 160, "is_available": True},
    {"menu_item_id": 5,  "name": "Mango Lassi",          "category": "Beverages",   "price": 80,  "is_available": True},
    {"menu_item_id": 6,  "name": "Gulab Jamun",          "category": "Dessert",     "price": 60,  "is_available": True},
    {"menu_item_id": 7,  "name": "Butter Naan",          "category": "Bread",       "price": 40,  "is_available": True},
    {"menu_item_id": 8,  "name": "Dal Tadka",            "category": "Main Course", "price": 150, "is_available": True},
    {"menu_item_id": 9,  "name": "Cold Coffee",          "category": "Beverages",   "price": 90,  "is_available": True},
    {"menu_item_id": 10, "name": "Veg Burger",           "category": "Snacks",      "price": 110, "is_available": True},
]

ORDERS_DB = []

# ── Request Models ──────────────────────────────────────

class OrderRequest(BaseModel):
    table_id:       int
    customer_id:    int
    menu_item_id:   int
    quantity:       int
    payment_method: str
    staff_id:       Optional[int] = 1

class FeedbackRequest(BaseModel):
    order_id:    int
    customer_id: int
    rating:      int
    comment:     Optional[str] = ""

# ── Routes ──────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "project":    "Restaurant Ordering System",
        "student":    "Swayam Sanket Padhy",
        "roll_no":    "2306239",
        "university": "KIIT University",
        "batch":      "Data Engineering 2025-2026",
        "status":     "running"
    }

@app.get("/menu")
def get_menu():
    return {"menu": MENU, "total_items": len(MENU)}

@app.get("/menu/category/{category}")
def get_menu_by_category(category: str):
    items = [m for m in MENU if m["category"].lower() == category.lower()]
    if not items:
        raise HTTPException(status_code=404, detail=f"No items found in category: {category}")
    return {"category": category, "items": items}

@app.post("/order")
def place_order(order: OrderRequest):
    item = next((m for m in MENU if m["menu_item_id"] == order.menu_item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item not available")

    order_record = {
        "order_id":       random.randint(10000, 99999),
        "table_id":       order.table_id,
        "customer_id":    order.customer_id,
        "menu_item_id":   order.menu_item_id,
        "item_name":      item["name"],
        "category":       item["category"],
        "quantity":       order.quantity,
        "amount":         round(item["price"] * order.quantity, 2),
        "payment_method": order.payment_method,
        "staff_id":       order.staff_id,
        "status":         "placed",
        "entry_time":     datetime.now().isoformat()
    }
    ORDERS_DB.append(order_record)
    return {"message": "Order placed successfully", "order": order_record}

@app.get("/orders")
def get_all_orders():
    return {"total_orders": len(ORDERS_DB), "orders": ORDERS_DB}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in ORDERS_DB if o["order_id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    if not 1 <= feedback.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return {
        "message":     "Feedback submitted successfully",
        "feedback_id": random.randint(1000, 9999),
        "order_id":    feedback.order_id,
        "rating":      feedback.rating,
        "timestamp":   datetime.now().isoformat()
    }

@app.get("/analytics/summary")
def get_analytics_summary():
    if not ORDERS_DB:
        return {"message": "No orders yet"}
    total_revenue = sum(o["amount"] for o in ORDERS_DB)
    avg_value     = round(total_revenue / len(ORDERS_DB), 2)
    return {
        "total_orders":      len(ORDERS_DB),
        "total_revenue":     round(total_revenue, 2),
        "avg_order_value":   avg_value,
        "timestamp":         datetime.now().isoformat()
    }

@app.get("/analytics/top-items")
def get_top_items():
    from collections import Counter
    if not ORDERS_DB:
        return {"message": "No orders yet"}
    item_counts = Counter(o["item_name"] for o in ORDERS_DB)
    top = [{"item_name": k, "orders": v}
           for k, v in item_counts.most_common(5)]
    return {"top_items": top}

@app.get("/health")
def health_check():
    return {
        "status":    "healthy",
        "timestamp": datetime.now().isoformat(),
        "service":   "Restaurant Ordering System API"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
