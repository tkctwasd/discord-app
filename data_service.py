import json
from pathlib import Path
from datetime import datetime
import pytz

DATA_FILE = Path("data/food_data.json")
BILL_FILE = Path("data/bill_data.json")
TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_order(user, menu, price, message=None):

    data = load_data()

    today = datetime.now().strftime("%d/%m/%Y")

    for order in data["orders"]:

        if (
            order["user_id"] == user.id
            and order["date"] == today
        ):
            order["menu"] = menu
            order["price"] = int(price)
            if message is not None:
                order["message"] = message

            save_data(data)

            return order, True

    max_existing = max((o["id"] for o in data["orders"]), default=0)
    if data["next_id"] <= max_existing:
        data["next_id"] = max_existing + 1

    order = {
        "id": data["next_id"],
        "date": today,
        "user_id": user.id,
        "user_name": user.display_name,
        "menu": menu,
        "price": int(price),
        "paid": False,
        "message": message
    }

    data["orders"].append(order)
    data["next_id"] += 1

    save_data(data)

    return order, False

def get_user_debts(user_id):
    data = load_data()

    return [
        x for x in data["orders"]
        if x["user_id"] == user_id
        and not x["paid"]
        and not x.get("pending", False)
    ]


def get_all_debts():
    data = load_data()

    result = {}

    for order in data["orders"]:

        if order["paid"]:
            continue

        user_id = order["user_id"]

        result.setdefault(user_id, {
            "user_name": order["user_name"],
            "money": 0
        })

        result[user_id]["money"] += order["price"]

    return result


def mark_paid(user_id):
    data = load_data()

    total = 0
    count = 0

    for order in data["orders"]:

        if (
            order["user_id"] == user_id
            and not order["paid"]
        ):
            order["paid"] = True

            total += order["price"]
            count += 1

    save_data(data)

    return count, total


def delete_order(user_id):

    data = load_data()

    today = datetime.now().strftime("%d/%m/%Y")

    before_count = len(data["orders"])

    data["orders"] = [
        order
        for order in data["orders"]
        if not (
            order["user_id"] == user_id
            and order["date"] == today
        )
    ]

    removed = before_count - len(data["orders"])

    save_data(data)

    return removed

def mark_pending_by_ids(order_ids):
    data = load_data()
    id_set = set(order_ids)
    for order in data["orders"]:
        if order["id"] in id_set:
            order["pending"] = True
    save_data(data)


def unmark_pending_by_ids(order_ids):
    data = load_data()
    id_set = set(order_ids)
    for order in data["orders"]:
        if order["id"] in id_set:
            order["pending"] = False
    save_data(data)


def mark_paid_by_ids(order_ids):
    data = load_data()

    id_set = set(order_ids)
    count = 0
    total = 0

    for order in data["orders"]:
        if order["id"] in id_set and not order["paid"]:
            order["paid"] = True
            total += order["price"]
            count += 1

    save_data(data)

    return count, total


def record_bill(user_id, user_name, amount, content, order_ids, order_dates, confirmed_by_id, confirmed_by_name, status, reason=None):
    if BILL_FILE.exists():
        with open(BILL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"next_id": 1, "transactions": []}

    now = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")

    transaction = {
        "id": data["next_id"],
        "timestamp": now,
        "user_id": user_id,
        "user_name": user_name,
        "amount": amount,
        "content": content or "",
        "order_ids": order_ids,
        "order_dates": order_dates,
        "confirmed_by_id": confirmed_by_id,
        "confirmed_by_name": confirmed_by_name,
        "status": status,
        "reason": reason
    }

    data["transactions"].append(transaction)
    data["next_id"] += 1

    with open(BILL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return transaction


def get_today_orders():

    data = load_data()

    today = datetime.now().strftime("%d/%m/%Y")

    return [
        order
        for order in data["orders"]
        if order["date"] == today
    ]
