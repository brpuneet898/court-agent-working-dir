import os, json, datetime
from neo4j import GraphDatabase
import re

# ─── CONFIG ────────────────────────────────────────────────────────────────────
BOLT_URL  = "bolt://localhost:7687"
USERNAME  = "neo4j"
PASSWORD  = "Enter your password here"
DATA_FILE  = r"Enter path to your data file here"
# ────────────────────────────────────────────────────────────────────────────────

def parse_date(d_str):
    if not isinstance(d_str, str):
        return None
    # handle ranges like "01/01/2015 - 25/03/2015"
    if "-" in d_str:
        d_str = d_str.split("-", 1)[0].strip()
    for fmt in ("%d/%m/%Y", "%B %Y"):
        try:
            dt = datetime.datetime.strptime(d_str, fmt)
            # for "%B %Y", default day=1 is fine
            return dt.date()
        except ValueError:
            continue
    return None

def strip_fences(raw):
    """
    Remove leading/trailing ```json fences if present.
    """
    lines = raw.splitlines()
    # drop first line if it starts with ```
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    # drop last line if it starts with ```
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)

def extract_inner_orders(raw_output):
    """
    Attempt to parse the payload inside raw_output.
    Returns a list of order-dicts, or raises JSONDecodeError.
    """
    payload = strip_fences(raw_output)
    return json.loads(payload)  
def import_order(tx, order):
    # safe _id
    raw_id = order.get("_id")
    if isinstance(raw_id, dict):
        oid = raw_id.get("$oid")
    else:
        oid = raw_id

    # —– unwrap/normalize insider-trading type ——————————
    itt = order.get("Type of Insider Trading")
    if not itt:
        itt = order.get("Type")          
    if not itt:
        itt = "Not applicable"           

    # ——— unwrap Monetary Penalty Imposed ——————————————
    mp = order.get("Monetary Penalty Imposed")
    if isinstance(mp, dict):
        # handle the common mongo‐json shells
        if "$numberLong" in mp:
            mp = int(mp["$numberLong"])
        elif "$numberInt" in mp:
            mp = int(mp["$numberInt"])
        elif "$numberDouble" in mp:
            mp = float(mp["$numberDouble"])
        else:
            mp = None

    jc = order.get("Judgment Criteria")
    if isinstance(jc, dict):
        jc = json.dumps(jc, ensure_ascii=False)
    pc = order.get("Penalty Criteria")
    if isinstance(pc, dict):
        pc = json.dumps(pc, ensure_ascii=False)

    params = {
        "id":                   oid,
        "dateOfOrder":          parse_date(order.get("Date of Order")),
        "dateOfAction":         parse_date(order.get("Date of Action")),
        "caseName":             order.get("Case Name"),
        "monetaryPenalty":      mp,
        "nonMonetaryPenalty":   order.get("Non-monetary Penalty"),
        "judgmentCriteria":     jc,
        "penaltyCriteria":      pc,
        "contextualMeta":       order.get("Contextual Metadata"),
        "caseSummary":          order.get("Case Summary"),
        "provisions":           order.get("Provisions", []),
        "typeOfInsiderTrading": itt,
        "pitVersion":           order.get("PIT Version"),
        "orderType":            order.get("Order Type")
    }

    tx.run("""
    MERGE (o:Order {id: $id})
      SET
        o.dateOfOrder        = $dateOfOrder,
        o.dateOfAction       = $dateOfAction,
        o.caseName           = $caseName,
        o.monetaryPenalty    = $monetaryPenalty,
        o.nonMonetaryPenalty = $nonMonetaryPenalty,
        o.judgmentCriteria   = $judgmentCriteria,
        o.penaltyCriteria    = $penaltyCriteria,
        o.contextualMeta     = $contextualMeta,
        o.caseSummary        = $caseSummary
    WITH o
    UNWIND $provisions AS prov
      MERGE (p:Provision {name: prov})
      MERGE (o)-[:HAS_PROVISION]->(p)
    WITH o
      MERGE (t:InsiderTradingType {name: $typeOfInsiderTrading})
      MERGE (o)-[:HAS_INSIDER_TRADING_TYPE]->(t)
    WITH o
      MERGE (v:PITVersion {name: $pitVersion})
      MERGE (o)-[:USES_PIT_VERSION]->(v)
    WITH o
      MERGE (ot:OrderType {name: $orderType})
      MERGE (o)-[:HAS_ORDER_TYPE]->(ot)
    """, **params)

def main():
    driver = GraphDatabase.driver(BOLT_URL, auth=(USERNAME, PASSWORD))
    with driver.session() as session:
        orders = json.load(open(DATA_FILE, encoding="utf-8"))
        total  = len(orders)

        for idx, order in enumerate(orders, start=1):
            # --- ensuring PIT Version is never None ---
            if not order.get("PIT Version"):
                order["PIT Version"] = "Not applicable"
            outer_oid = (order.get("_id", {}) .get("$oid")
                         if isinstance(order.get("_id"), dict)
                         else order.get("_id"))
            if "raw_output" in order and isinstance(order["raw_output"], str):
                try:
                    inners = extract_inner_orders(order["raw_output"])
                    for j, inner in enumerate(inners, start=1):
                        print(order)
                        inner["_id"] = {"$oid": f"{outer_oid}_{j}"}
                        session.execute_write(import_order, inner)
                    print(f"[{idx}/{total}] Unpacked {len(inners)} from {outer_oid}")
                except json.JSONDecodeError:
                    print(order)
                    print(f"[{idx}/{total}] Failed to parse raw_output of {outer_oid}, importing outer order only")
                    session.execute_write(import_order, order)
            else:
                print(order)
                session.execute_write(import_order, order)
                print(f"[{idx}/{total}] Imported order id={outer_oid}")

    driver.close()
    print("All done.")

if __name__ == "__main__":
    main()