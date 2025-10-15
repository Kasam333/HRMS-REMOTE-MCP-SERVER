import random
from fastmcp import FastMCP
import psycopg2

mcp = FastMCP(name="HRMS Server")

@mcp.tool
def roll_dice(n_dice: int = 1) -> list[int]:
    return [random.randint(1,6) for _ in range(n_dice)]

DB_CONFIG = [
    "dbname": 'HRMS',
    "user": 'openpg',
    "password": 'openpgpwd',
    "host": 'localhost',
    "port": '5432'
]

@


if __name__ == "__main__":
    mcp.run()
