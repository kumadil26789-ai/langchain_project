# Ask your employees table

Use plain-English questions to look up employee records in a local SQLite
database. LangChain turns each question into a SQL query; the app validates and
executes it against the `employees` table using a read-only connection, then
prints the matching rows.

## Setup

1. Use Python 3.10 or later and install the dependencies:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to your OpenAI API
   key. Optionally change `OPENAI_MODEL`.
3. Start the prompt:

   ```powershell
   python app.py
   ```

The app creates `data/company.db` with example employee records on first run.
Ask questions such as “Which employees work in Engineering?” or “Who is in New
York?”, then enter `exit` to quit.

## Safety and customization

The query executor accepts only one `SELECT` statement, opens SQLite in
read-only mode, denies writes and reads from other tables, blocks
`load_extension`, and returns at most 100 rows. Generated SQL is printed so
you can see the query used to answer each prompt.

To use your own table, update the schema and seed rows in `database.py`, and
adjust the read-authorizer table allowlist. Do not put database credentials or
API keys in source control.
