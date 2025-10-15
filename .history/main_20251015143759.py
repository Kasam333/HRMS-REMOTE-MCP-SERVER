import random
from fastmcp import FastMCP
import psycopg2  # type: ignore
import base64, io

DB_CONFIG = {
    "dbname": 'HRMS1',
    "user": 'openpg',
    "password": 'openpgpwd',
    "host": 'localhost',
    "port": '5432'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

mcp = FastMCP(name="HRMS Server")


# Function to get user's group names
def get_user_groups(employee_id: int) -> list[str]:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT user_id FROM hr_employee WHERE id = %s", (employee_id,))
        result = cur.fetchone()
        if not result or not result[0]:
            return []

        user_id = result[0]

        cur.execute("""
            SELECT g.name
            FROM res_groups g
            JOIN res_groups_users_rel r ON g.id = r.gid
            WHERE r.uid = %s
        """, (user_id,))

        rows = cur.fetchall()
        groups = []

        for row in rows:
            group_name = row[0]
            if isinstance(group_name, dict):
                group_name = group_name.get("en_US", "")
            if isinstance(group_name, str):
                groups.append(group_name.strip().lower())

        return groups

    finally:
        cur.close()
        conn.close()

# ----------------------------------------------------------
# 🔹 Tool: List Employees with Group Restrictions
# ----------------------------------------------------------
@mcp.tool()
def list_employees(employee_id: int) -> list[dict]:
    user_groups = get_user_groups(employee_id)

    # Define role-based access
    admin_groups = {"admin", "administrator"}
    developer_groups = {"developer"}
    qa_groups = {"qa"}

    # Normalize all to lowercase
    user_groups = set(g.lower() for g in user_groups)

    is_admin = bool(user_groups & admin_groups)
    is_developer = bool(user_groups & developer_groups)
    is_qa = bool(user_groups & qa_groups)

    # 🔹 Admin → Full access
    if is_admin:
        access_level = "admin"
    # 🔹 Developer → Limited access
    elif is_developer:
        access_level = "developer"
    # 🔹 QA → Restricted access
    elif is_qa:
        access_level = "qa"
    else:
        return [{"error": "Access denied. You do not have permission to view employee data."}]

    conn = get_connection()
    cur = conn.cursor()

    # 🔹 Access-based query filtering
    if access_level == "admin":
        query = """
            SELECT e.id, e.name, d.name->>'en_US' AS department
            FROM hr_employee e
            LEFT JOIN hr_department d ON e.department_id = d.id
            ORDER BY e.id
        """
        cur.execute(query)
    elif access_level == "developer":
        query = """
            SELECT e.id, e.name, d.name->>'en_US' AS department
            FROM hr_employee e
            LEFT JOIN hr_department d ON e.department_id = d.id
            WHERE e.id = %s
            ORDER BY e.id
        """
        cur.execute(query, (employee_id,))
    elif access_level == "qa":
        query = """
            SELECT e.id, e.name, d.name->>'en_US' AS department
            FROM hr_employee e
            LEFT JOIN hr_department d ON e.department_id = d.id
            WHERE e.id = %s
            ORDER BY e.id
        """
        cur.execute(query, (employee_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"id": r[0], "name": r[1], "department": r[2]} for r in rows]


@mcp.tool()
def get_employee_details(employee_id: int) -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT e.id, e.serial_number, e.name, e.job_title, e.work_email, e.work_phone, d.name AS department, c.name AS company
                FROM hr_employee e
                LEFT JOIN hr_department d ON e.department_id = d.id
                LEFT JOIN res_company c ON e.company_id = c.id
                WHERE e.id = %s
                """, (employee_id,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"error": f"No Employee Found with ID {employee_id}"}
    
    return {
        "id": row[0],
        "serial_number": row[1],
        "name": row[2],
        "job_tilte": row[3],
        "work_email": row[4],
        "work_phone": row[5],
        "department": row[6],
        "company": row[7]
    }

# ----------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="http", port)
