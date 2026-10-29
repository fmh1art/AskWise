"""Finite-world inference; all correctness statements are conditional on coverage."""
from collections import Counter
from functools import lru_cache
from itertools import product
from math import log2
import random
import sqlite3


def entropy(values):
    counts = Counter(values)
    n = sum(counts.values())
    return -sum((c/n)*log2(c/n) for c in counts.values()) if n else 0.0


class Problem:
    def __init__(self, worlds, answers, questions=None, name=""):
        self.worlds = tuple(tuple(w) for w in worlds)
        self.answers = tuple(answers)
        if not self.worlds or len(self.worlds) != len(self.answers):
            raise ValueError("Nonempty aligned worlds and answers required")
        self.k = len(self.worlds[0])
        if any(len(w) != self.k for w in self.worlds):
            raise ValueError("Inconsistent dimensions")
        if len(set(self.worlds)) != len(self.worlds):
            raise ValueError("Duplicate worlds")
        self.questions = questions or [f"assumption_{j}" for j in range(self.k)]
        self.name = name

    def partitions(self, state, q):
        groups = {}
        for i in state:
            groups.setdefault(self.worlds[i][q], []).append(i)
        return tuple(tuple(g) for g in groups.values())

    def invariant(self, state):
        return bool(state) and len({self.answers[i] for i in state}) == 1

    def certificate(self, state):
        if not state or not self.invariant(state):
            return None
        return {"answer": self.answers[state[0]], "world_count": len(state),
                "scope": "enumerated candidate worlds only; completeness not established"}

    @lru_cache(None)
    def optimal(self, state):
        if self.invariant(state):
            return 0.0, None
        values = []
        for q in range(self.k):
            parts = self.partitions(state, q)
            if len(parts) > 1:
                values.append((1+sum(len(p)/len(state)*self.optimal(p)[0] for p in parts), q))
        return min(values) if values else (float("inf"), None)

    def choose(self, state, method, rng):
        available = [q for q in range(self.k) if len(self.partitions(state, q)) > 1]
        if not available:
            return None
        if method in ("ask_all", "fixed"):
            return available[0]
        if method == "random":
            return rng.choice(available)
        if method == "repair_first":
            return min(available, key=lambda q:(q == 0, q))
        if method == "optimal":
            return self.optimal(state)[1]
        if method == "local":
            # Deliberately limited ablation: change one coordinate of an anchor.
            anchor = state[0]
            for q in available:
                for j in state:
                    if all(self.worlds[j][d] == self.worlds[anchor][d] for d in range(self.k) if d != q) and self.answers[j] != self.answers[anchor]:
                        return q
            return None
        if method == "observed_then_repair":
            # Intent decisions use the anchor repair. After intent is fixed,
            # repair checks are exhaustive. This is an ablation, not full AIR.
            if 0 in available:
                anchor = state[0]
                subset = [j for j in state if self.worlds[j][1:] == self.worlds[anchor][1:]]
                if not self.invariant(subset):
                    return 0
                return -1  # irrevocably prune equal intents on observed data
            return available[0]
        def score(q):
            parts = self.partitions(state, q)
            if method == "world_entropy":
                return entropy([self.worlds[i][q] for i in state])
            if method == "answer_entropy":
                return entropy([self.answers[i] for i in state])-sum(len(p)/len(state)*entropy([self.answers[i] for i in p]) for p in parts)
            if method == "ec2":
                # Unit uniform-prior edge mass; common normalization cancels.
                # An edge remains iff both endpoints survive the observed test.
                def edges(p):
                    c=Counter(self.answers[i] for i in p)
                    return (len(p)**2-sum(v*v for v in c.values()))/2
                return edges(state)-sum(len(p)/len(state)*edges(p) for p in parts)
            raise ValueError(method)
        return max(available, key=lambda q:(score(q),-q))

    def run(self, true_index, method, seed=0, initial=None):
        state = tuple(range(len(self.worlds))) if initial is None else tuple(initial)
        if not state:
            return {"correct": False, "questions": 0, "abstained": True, "trace": []}
        rng = random.Random(seed)
        trace = []
        for _ in range(self.k+2):
            if method == "none" or (method != "ask_all" and self.invariant(state)):
                break
            q = self.choose(state, method, rng)
            if q is None:
                break
            if q == -1:
                state = tuple(i for i in state if self.worlds[i][0] == self.worlds[state[0]][0])
                trace.append({"pruned_intent_without_feedback": True})
                continue
            value = self.worlds[true_index][q]
            trace.append({"question": q, "response": value})
            state = tuple(i for i in state if self.worlds[i][q] == value)
            if not state:
                return {"correct": False, "questions": sum("question" in t for t in trace), "abstained": True, "trace": trace}
        guess = self.answers[state[0]]
        return {"correct": guess == self.answers[true_index], "questions": sum("question" in t for t in trace),
                "abstained": False, "trace": trace, "answer": guess, "certificate": self.certificate(state)}


def sales_task(seed, family="top_region"):
    """Three suspected duplicate invoices and two possible query interpretations."""
    rng = random.Random(seed)
    rows = []
    for i in range(9):
        gross=rng.randint(5,50)
        rows.append((i, rng.choice(["East","West","North"]), gross, rng.randint(0,gross//2), i//2))
    duplicate_targets = rng.sample(range(9),3)
    for j, target in enumerate(duplicate_targets):
        rows.append((9+j,)+rows[target][1:])
    worlds = list(product([0,1],repeat=4))
    answers=[]
    conn=sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders(id INTEGER, region TEXT, gross INTEGER, discount INTEGER, customer INTEGER)")
    for intent,*repair in worlds:
        conn.execute("DELETE FROM orders")
        kept=[r for r in rows if r[0]<9 or not repair[r[0]-9]]
        conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?)",kept)
        if family == "top_region":
            metric="gross-discount" if intent else "gross"
            sql=f"WITH a AS (SELECT region, SUM({metric}) AS total FROM orders GROUP BY region) SELECT region FROM a WHERE total=(SELECT MAX(total) FROM a) ORDER BY region"
        elif family == "customer_count":
            sql="SELECT COUNT(DISTINCT customer) FROM orders" if intent else "SELECT COUNT(*) FROM orders"
        elif family == "threshold_count":
            sql=f"SELECT COUNT(*) FROM orders WHERE gross{'-discount' if intent else ''} >= 25"
        else:
            raise ValueError(family)
        answers.append(tuple(tuple(r) for r in conn.execute(sql)))
    conn.close()
    problem=Problem(worlds,answers,name=f"{family}-{seed}")
    problem.rows=rows
    problem.family=family
    problem.duplicate_targets=duplicate_targets
    return problem
