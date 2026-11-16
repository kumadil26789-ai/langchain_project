import os
import sqlite3

from dotenv import load_dotenv
from langchain_classic.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from database import DATABASE_PATH, execute_read_query, initialize_database


def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key."
        )

    initialize_database()
    database = SQLDatabase.from_uri(f"sqlite:///{DATABASE_PATH.as_posix()}")
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    query_chain = create_sql_query_chain(model, database, k=100)

    print("Ask questions about the sample employees table. Type 'exit' to quit.")
    while True:
        question = input("\nQuestion> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        try:
            sql = query_chain.invoke({"question": question})
            rows = execute_read_query(sql)
        except (ValueError, sqlite3.Error) as error:
            print(f"Could not answer that question: {error}")
            continue

        print(f"\nRead-only query: {sql.strip()}")
        if not rows:
            print("No matching employees found.")
            continue
        for row in rows:
            print(" | ".join(f"{key}: {value}" for key, value in row.items()))


if __name__ == "__main__":
    main()
