import duckdb

SQL_FILE = "sql/analysis.sql"

with open(SQL_FILE, "r", encoding="utf-8") as file:
    sql = file.read()

con = duckdb.connect()

statements = [
    statement.strip()
    for statement in sql.split(";")
    if statement.strip()
]

for number, statement in enumerate(statements, start=1):
    print("\n" + "=" * 60)
    print(f"QUERY {number}")
    print("=" * 60)

    result = con.execute(statement)
    print(result.fetchdf().to_string(index=False))

con.close()
