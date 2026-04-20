# ============================================
# RESTAURANT ORDERING SYSTEM -- STREAMLIT DASHBOARD
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Restaurant Ordering System",
    page_icon="🍽️",
    layout="wide"
)

st.markdown("""
    <h1 style='text-align:center'>🍽️ Restaurant Ordering System</h1>
    <p style='text-align:center; color:gray'>
        Swayam Sanket Padhy | Roll No: 2306239 |
        Data Engineering 2025-2026 | KIIT University
    </p>
    <hr>
""", unsafe_allow_html=True)

# ── Simulated Data ──────────────────────────────────────

@st.cache_data
def generate_data(n=500):
    menu_items = [
        ("Paneer Butter Masala", "Main Course", 220),
        ("Chicken Biryani",      "Main Course", 280),
        ("Masala Dosa",          "Breakfast",   120),
        ("Veg Fried Rice",       "Main Course", 160),
        ("Mango Lassi",          "Beverages",    80),
        ("Gulab Jamun",          "Dessert",       60),
        ("Butter Naan",          "Bread",         40),
        ("Dal Tadka",            "Main Course",  150),
        ("Cold Coffee",          "Beverages",     90),
        ("Veg Burger",           "Snacks",       110),
    ]
    payments = ["UPI", "Cash", "Credit Card", "Debit Card", "Wallet"]
    sections = ["Ground Floor", "First Floor", "Rooftop", "Outdoor"]
    tiers    = ["bronze", "silver", "gold", "platinum"]

    rows = []
    base = datetime.now() - timedelta(days=30)
    for i in range(n):
        item = random.choice(menu_items)
        qty  = random.randint(1, 5)
        rows.append({
            "order_id":       10000 + i,
            "table_id":       random.randint(1, 20),
            "customer_id":    random.randint(1, 200),
            "item_name":      item[0],
            "category":       item[1],
            "price":          item[2],
            "quantity":       qty,
            "amount":         item[2] * qty,
            "payment_method": random.choice(payments),
            "section":        random.choice(sections),
            "loyalty_tier":   random.choice(tiers),
            "rating":         random.randint(1, 5),
            "order_time":     base + timedelta(
                                  minutes=random.randint(0, 43200)),
        })
    df = pd.DataFrame(rows)
    df["hour"]        = df["order_time"].dt.hour
    df["date"]        = df["order_time"].dt.date
    df["day_of_week"] = df["order_time"].dt.day_name()
    return df

df = generate_data()

# ── Sidebar Filters ─────────────────────────────────────

st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Category",
    options=df["category"].unique(),
    default=df["category"].unique()
)
payments_filter = st.sidebar.multiselect(
    "Payment Method",
    options=df["payment_method"].unique(),
    default=df["payment_method"].unique()
)
sections_filter = st.sidebar.multiselect(
    "Section",
    options=df["section"].unique(),
    default=df["section"].unique()
)

filtered = df[
    df["category"].isin(categories) &
    df["payment_method"].isin(payments_filter) &
    df["section"].isin(sections_filter)
]

# ── KPI Cards ────────────────────────────────────────────

st.subheader("Key Performance Indicators")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Orders",    f"{len(filtered):,}")
k2.metric("Total Revenue",   f"Rs. {filtered['amount'].sum():,.0f}")
k3.metric("Avg Order Value", f"Rs. {filtered['amount'].mean():,.0f}")
k4.metric("Avg Rating",      f"{filtered['rating'].mean():.2f} / 5")
k5.metric("Unique Customers",f"{filtered['customer_id'].nunique():,}")

st.markdown("---")

# ── Charts Row 1 ─────────────────────────────────────────

c1, c2 = st.columns(2)

with c1:
    st.subheader("Revenue by Category")
    cat_rev = filtered.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(cat_rev, names="category", values="amount",
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Top 5 Best-Selling Items")
    top_items = (filtered.groupby("item_name")["quantity"]
                 .sum().reset_index()
                 .sort_values("quantity", ascending=False).head(5))
    fig2 = px.bar(top_items, x="quantity", y="item_name",
                  orientation="h", color="quantity",
                  color_continuous_scale="Oranges")
    fig2.update_layout(yaxis_title="", xaxis_title="Units Sold")
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ─────────────────────────────────────────

c3, c4 = st.columns(2)

with c3:
    st.subheader("Orders by Hour of Day")
    hourly = filtered.groupby("hour")["order_id"].count().reset_index()
    hourly.columns = ["hour", "orders"]
    fig3 = px.line(hourly, x="hour", y="orders",
                   markers=True, color_discrete_sequence=["#FF7043"])
    fig3.update_layout(xaxis_title="Hour", yaxis_title="Orders")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Payment Method Distribution")
    pay_counts = filtered["payment_method"].value_counts().reset_index()
    pay_counts.columns = ["method", "count"]
    fig4 = px.bar(pay_counts, x="method", y="count",
                  color="method",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig4.update_layout(showlegend=False, xaxis_title="", yaxis_title="Transactions")
    st.plotly_chart(fig4, use_container_width=True)

# ── Charts Row 3 ─────────────────────────────────────────

c5, c6 = st.columns(2)

with c5:
    st.subheader("Daily Revenue Trend (Last 30 Days)")
    daily = filtered.groupby("date")["amount"].sum().reset_index()
    fig5 = px.area(daily, x="date", y="amount",
                   color_discrete_sequence=["#26A69A"])
    fig5.update_layout(xaxis_title="Date", yaxis_title="Revenue (Rs.)")
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    st.subheader("Revenue by Section")
    sec_rev = filtered.groupby("section")["amount"].sum().reset_index()
    fig6 = px.bar(sec_rev, x="section", y="amount",
                  color="section",
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig6.update_layout(showlegend=False, xaxis_title="", yaxis_title="Revenue (Rs.)")
    st.plotly_chart(fig6, use_container_width=True)

# ── Loyalty Tier ─────────────────────────────────────────

st.subheader("Customer Loyalty Tier Breakdown")
tier_data = filtered.groupby("loyalty_tier").agg(
    customers=("customer_id", "nunique"),
    revenue=("amount", "sum")
).reset_index()
fig7 = px.bar(tier_data, x="loyalty_tier", y="revenue",
              color="loyalty_tier", text="customers",
              color_discrete_sequence=["#CD7F32","#C0C0C0","#FFD700","#E5E4E2"],
              labels={"loyalty_tier": "Tier", "revenue": "Revenue (Rs.)"})
fig7.update_traces(texttemplate="👤 %{text}", textposition="outside")
st.plotly_chart(fig7, use_container_width=True)

# ── Raw Data Table ────────────────────────────────────────

st.subheader("Raw Orders Data")
st.dataframe(
    filtered[["order_id","item_name","category","quantity",
              "amount","payment_method","section","loyalty_tier",
              "rating","order_time"]].head(50),
    use_container_width=True
)

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray'>"
    "Swayam Sanket Padhy | Roll No: 2306239 | "
    "Data Engineering 2025-2026 | KIIT University"
    "</p>",
    unsafe_allow_html=True
)
