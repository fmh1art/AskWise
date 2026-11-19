"""Refresh the offline revenue example using SQLite and AskWise witnesses."""
import json
from itertools import product
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from a2.relevance import witness

queries = ["SELECT SUM(amount) FROM orders",
           "SELECT SUM(amount) FROM orders WHERE status = 'Completed'"]
worlds = list(product(range(2), range(2)))
orders = [("O-101", "Completed", 60), ("O-102", "Completed", 10),
          ("O-103", "Pending", None), ("O-104", "Completed", 30)]


def build():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders (id TEXT, status TEXT, amount INTEGER)")
    db.executemany("INSERT INTO orders VALUES (?, ?, ?)", orders)
    answers = {}
    for i, (intent, repair) in enumerate(worlds):
        db.execute("UPDATE orders SET amount = ? WHERE id = 'O-103'", (repair * 50,))
        answers[i] = db.execute(queries[intent]).fetchone()[0]
    db.close()
    states = {}
    for intent, repair in product((-1, 0, 1), repeat=2):
        live = [i for i, (q, r) in enumerate(worlds)
                if intent in (-1, q) and repair in (-1, r)]
        values = {answers[i] for i in live}
        states[f"{intent},{repair}"] = {
            "live": live, "answer": values.pop() if len(values) == 1 else None,
            "witness": [witness(worlds, live, answers, k) for k in range(2)]}
    return dict(orders=orders, queries=queries, answers=list(answers.values()), states=states)


if __name__ == "__main__":
    page = Path(__file__).with_name("index.html")
    start = '<script type="application/json" id="fixture">'
    head, tail = page.read_text().split(start)
    _, body = tail.split("</script>", 1)
    page.write_text(head + start + json.dumps(build()) + "</script>" + body)
