# ============================================
# RESTAURANT ORDERING SYSTEM -- DATA QUALITY
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

import great_expectations as ge
import pandas as pd
from datetime import datetime
import json
import os

RESULTS_PATH = "/tmp/ge_results"
os.makedirs(RESULTS_PATH, exist_ok=True)

def load_sample_orders():
    return pd.DataFrame({
        "order_id":       [1001, 1002, 1003, 1004, 1005],
        "table_id":       [3, 7, 12, 1, 9],
        "customer_id":    [201, 305, 102, 450, 88],
        "menu_item_id":   [2, 5, 1, 8, 3],
        "item_name":      [
            "Chicken Biryani",
            "Mango Lassi",
            "Paneer Butter Masala",
            "Dal Tadka",
            "Masala Dosa"
        ],
        "category":       [
            "Main Course", "Beverages",
            "Main Course", "Main Course", "Breakfast"
        ],
        "quantity":       [2, 1, 3, 2, 1],
        "amount":         [560.0, 80.0, 660.0, 300.0, 120.0],
        "payment_method": ["UPI", "Cash", "Credit Card", "UPI", "Debit Card"],
        "section":        [
            "Ground Floor", "Rooftop",
            "First Floor", "Outdoor", "Ground Floor"
        ],
        "loyalty_tier":   ["gold", "bronze", "silver", "platinum", "bronze"],
        "staff_id":       [3, 7, 2, 11, 5],
        "status":         ["placed", "placed", "placed", "placed", "placed"],
        "entry_time":     [datetime.now().isoformat()] * 5
    })

def run_orders_checkpoint():
    print("=" * 60)
    print("Great Expectations -- Orders Data Quality Checkpoint")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    df    = load_sample_orders()
    df_ge = ge.from_pandas(df)

    checks = [
        # Completeness checks
        ("order_id not null",
         df_ge.expect_column_values_to_not_be_null("order_id")),
        ("amount not null",
         df_ge.expect_column_values_to_not_be_null("amount")),
        ("item_name not null",
         df_ge.expect_column_values_to_not_be_null("item_name")),
        ("table_id not null",
         df_ge.expect_column_values_to_not_be_null("table_id")),

        # Range checks
        ("amount between 1 and 100000",
         df_ge.expect_column_values_to_be_between("amount", 1, 100000)),
        ("quantity between 1 and 50",
         df_ge.expect_column_values_to_be_between("quantity", 1, 50)),
        ("table_id between 1 and 50",
         df_ge.expect_column_values_to_be_between("table_id", 1, 50)),

        # Set membership checks
        ("status valid values",
         df_ge.expect_column_values_to_be_in_set(
             "status", ["placed", "completed", "cancelled"])),
        ("payment_method valid values",
         df_ge.expect_column_values_to_be_in_set(
             "payment_method",
             ["UPI", "Cash", "Credit Card", "Debit Card", "Wallet"])),
        ("loyalty_tier valid values",
         df_ge.expect_column_values_to_be_in_set(
             "loyalty_tier",
             ["bronze", "silver", "gold", "platinum"])),
        ("category valid values",
         df_ge.expect_column_values_to_be_in_set(
             "category",
             ["Main Course", "Beverages", "Breakfast",
              "Dessert", "Bread", "Snacks"])),

        # Uniqueness check
        ("order_id unique",
         df_ge.expect_column_values_to_be_unique("order_id")),

        # Type checks
        ("amount is numeric",
         df_ge.expect_column_values_to_be_of_type("amount", "float")),
        ("quantity is integer",
         df_ge.expect_column_values_to_be_of_type("quantity", "int")),
    ]

    passed = 0
    failed = 0
    results_log = []

    for check_name, result in checks:
        success = result.success
        status  = "PASS" if success else "FAIL"
        icon    = "✓" if success else "✗"
        print(f"  [{status}] {icon}  {check_name}")
        if success:
            passed += 1
        else:
            failed += 1
        results_log.append({
            "check":   check_name,
            "status":  status,
            "success": success
        })

    print("-" * 60)
    print(f"  Total checks : {len(checks)}")
    print(f"  Passed       : {passed}")
    print(f"  Failed       : {failed}")
    print("-" * 60)

    report = {
        "run_time":     datetime.now().isoformat(),
        "dataset":      "orders",
        "total_checks": len(checks),
        "passed":       passed,
        "failed":       failed,
        "status":       "SUCCESS" if failed == 0 else "FAILED",
        "results":      results_log
    }

    report_file = f"{RESULTS_PATH}/orders_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved: {report_file}")
    print("=" * 60)

    if failed > 0:
        raise ValueError(f"{failed} data quality check(s) failed.")

    return report

if __name__ == "__main__":
    run_orders_checkpoint()
