import random
from fastmcp import FastMCP
import pycopg

mcp = FastMCP(name="Demo Server")

@mcp.tool
def roll_dice(n_dice: int = 1) -> list[int]:
    return [random.randint(1,6) for _ in range(n_dice)]


if __name__ == "__main__":
    mcp.run()
