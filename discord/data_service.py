import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/food_data.json")


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
    ]


def get_all_debts():
    data = load_data()

    result = {}

    for order in data["orders"]:

        if order["paid"]:
            continue

        result.setdefault(
            order["user_name"],
            0
        )

        result[order["user_name"]] += order["price"]

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

def get_today_orders():

    data = load_data()

    today = datetime.now().strftime("%d/%m/%Y")

    return [
        order
        for order in data["orders"]
        if order["date"] == today
    ]
