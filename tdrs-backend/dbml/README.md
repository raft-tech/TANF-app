# DBML / DB Diagram extension

[dbdiagram](https://dbdiagram.io) is a free, web-based tool used to design and draw entity-relationship diagrams (ERDs) for databases by writing simple code.

## How It Works
* **Code-Based Design:** You write definitions for tables, fields, and relationships using **DBML** (Database Markup Language), and the tool instantly draws an interactive visual diagram.
* **No Mouse Dragging:** Typing code prevents the messy manual formatting and spacing issues common in traditional drag-and-drop diagram software.
* **SQL Export:** You can export your completed visual schemas directly into SQL code for deployment-ready engines like PostgreSQL, MySQL, or SQL Server.

## Key Features
* **Collaboration:** Teams can share, password-protect, or collaborate on diagrams in real-time.
* **CLI Support:** A command-line interface lets users sync local `.dbml` files straight from a terminal or CI pipeline.
* **Import/Export:** You can import existing SQL scripts to auto-generate visual layouts or export your design into image and PDF formats.

## Import Current Schema
To extract the current schema, I told CoPilot in VSCode to use this example command
```bash
db2dbml postgres 'postgresql://user:password@localhost:5432/dbname' -o schema.dbml
```

I gave it this prompt:
```
I want to import the current schema using the dbdiagram cli: db2dbml postgres 'postgresql://tdpuser:something_secure@localhost:5432/tdrs_test' -o schema.dbml
Break that into appropriate schema domain files and put them into the dbdiagram folder in tdrs-backend.
```

Rather than install an NPM package for the util, it downloaded the runtime into a tmp dir and ran it from there. So it was a one-off run. If we want to run this again in the future it would be better to install the package.

## Other Notes

To view the diagram, click on a file and click the Preview button at the top right (first icon)

Google: can dbdiagram sync from a postgresql db?
