import os
import pymysql

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

SQL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "doc", "MeloonMoney.sql")

def run():
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, autocommit=True, charset="utf8mb4")
    cur = conn.cursor()
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
    # naive split by ; while preserving ; inside
    statements = []
    buff = []
    for line in sql.splitlines():
        l = line.strip()
        if not l or l.startswith("--"):
            continue
        buff.append(line)
        if l.endswith(";"):
            statements.append("\n".join(buff))
            buff = []
    if buff:
        statements.append("\n".join(buff))
    for stmt in statements:
        cur.execute(stmt)
    cur.close()
    conn.close()

if __name__ == "__main__":
    run()
