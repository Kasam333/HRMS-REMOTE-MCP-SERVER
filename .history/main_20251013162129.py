import random
from fastmcp import FastMCP
import psycopg2 # type: ignore
import base64, io

# @mcp.tool
# def roll_dice(n_dice: int = 1) -> list[int]:
#     return [random.randint(1,6) for _ in range(n_dice)]

DB_CONFIG = {
    "dbname": 'HRMS',
    "user": 'openpg',
    "password": 'openpgpwd',
    "host": 'localhost',
    "port": '5432'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

mcp = FastMCP(name="HRMS Server")

#Tools

@mcp.tool()
def list_employees() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT e.id, e.name, d.name AS department
                FROM hr_employee e
                LEFT JOIN hr_department d ON e.department_id = d.id
                ORDER BY e.id
                """)
    rows = cur.fetchall()
    cur.close()
    conn.close()


if __name__ == "__main__":
    mcp.run()
