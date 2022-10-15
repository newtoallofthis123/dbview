# Author: NoobScience
# filename: db.py
# License: MIT
# 3rd party Modules Used:
# Rich
# psycopg2

# Import the necessary modules
# Rich for formatting
from rich.console import Console
from rich.table import Table
from rich import print
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
# For working with postgres
import psycopg2
from psycopg2 import Error
import json
import string
import random
console = Console()

try:
    # Connect to an existing database
    try:
        # Get the secrets
        file = open("stuff.json", "r")
        stuff = file.read()
        secrets = json.loads(stuff)
        connection = psycopg2.connect(user=str(secrets["username"]),
                                      password=str(secrets["password"]),
                                      host=str(secrets["host"]),
                                      port=str(secrets["port"]),
                                      database=str(secrets["database"]))
        info = connection.get_dsn_parameters()
    except:
        console.print(
            ":red_circle:Sorry, something went wrong! Maybe a wrong credential? Check stuff.json's info correctly")

    cursor = connection.cursor()

    print(
        f'{info["user"]} is connected to PostgreSQL server on {info["host"]}:{info["port"]}')

    # Generate hash for assigning to a entry
    def hash_gen():
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits
        whole = lower + upper + digits
        hash_string = random.sample(whole, 8)
        hash = "".join(hash_string)
        return hash

    # Check if a table exits
    def check_table():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dbview(
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            author TEXT,
            hash TEXT NOT NULL,
            date TIMESTAMP
        );
        """)
        console.log(":green_circle: Connected to Table :man: dbview")

    def insert(name, url, author):
        cursor.execute(f"""
        INSERT INTO dbview (name, url, author, hash, date) VALUES ('{name}', '{url}', '{author}', '{str(hash_gen())}', CURRENT_TIMESTAMP)
        """)
        search("name", name)

    def table():
        cursor.execute("SELECT * from dbview")
        records = cursor.fetchall()
        try:
            table = Table(title=Panel(
                f'Query DB [red]{info["host"]}:{info["port"]}'), show_header=True, header_style="bold green")
            table.add_column("Name", style="purple", width=20)
            table.add_column("Url", style="yellow")
            table.add_column("Author", style="cyan")
            table.add_column("Hash", style="dim")
            table.add_column("Date", no_wrap=True, style="dim blue")
            for record in records:
                table.add_row(
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    str(record[4])
                )
            table.caption = ":zap: Made by [link=https://newtoallofthis123.github.io/About]NoobScience[/link]"
            console.print(table)
        except:
            print("Name\t\t | URL\t\t | Channel\t\t | Hash\t\t | Date")
            for record in records:
                print(
                    f'{record[0]}\t\t | {record[1]}\t\t | {record[2]}\t\t | {record[3]}\t\t| {str(record[4])}\t\t')
            print("Made by NoobScience")

    def edit(key, value):
        console.print(
            "Enter The New Values to Update in the form of a name url channel")
        new_record = str(Prompt.ask("Enter Here: "))
        new_records = new_record.split()
        cursor.execute(
            f"UPDATE dbview SET name='{new_records[0]}', url='{new_records[1]}', author='{new_records[2]}' WHERE {key}='{value}'")
        # records = cursor.fetchall()
        console.log(":green_circle: Successfully Updated Database")
        table()

    def hash():
        console.print("Enter A Key and Value to get Hash")
        record_key = str(Prompt.ask("Enter a Key", choices=[
                         "name", "url", "author", "hash", "date"], default="name"))
        record_value = str(Prompt.ask("Enter a Value"))
        cursor.execute(
            f"SELECT * from dnview WHERE {record_key}='{record_value}'")
        records = cursor.fetchone()
        console.print(f"The Hash is {records[3]}")

    def delete(key, value):
        table()
        cursor.execute(f"DELETE from dbview WHERE {key}='{value}'")
        console.log(":green_circle: Successfully Updated Database")
        table()

    def drop():
        console.print(
            "Are you sure you want to Drop the database? This will delete the whole table")
        confirmation = Confirm.ask("Are you sure")
        if confirmation:
            cursor.execute("DROP table dbview;")
            console.print(
                "Dropped Table dbview: Restart the application to start a new main table")
        else:
            console.print("Skipped the drop operation")

    def search(key, value):
        cursor.execute(f"SELECT * from dbview WHERE {key}='{value}'")
        records = cursor.fetchall()
        table = Table(title=Panel(
            f'Query DB [red]{info["host"]}:{info["port"]}'), show_header=True, header_style="bold green")
        table.add_column("Name", style="purple", width=20)
        table.add_column("Url", style="yellow")
        table.add_column("Channel", style="cyan")
        table.add_column("Hash", style="dim")
        table.add_column("Date", no_wrap=True, style="dim blue")
        for record in records:
            table.add_row(
                record[0],
                record[1],
                record[2],
                record[3],
                str(record[4])
            )
        table.caption = ":zap: Made by [link=https://newtoallofthis123.github.io/About]NoobScience[/link]"
        console.print(table)
    loop = 1
    while loop != 12:
        check_table()
        action = str(Prompt.ask("Enter your name", choices=[
                     "view", "new", "edit", "delete", "drop", "quit", "hash"], default="view"))
        if action == "view":
            table()
        if action == "new":
            name = Prompt.ask("Enter the Name")
            url = Prompt.ask("Enter The URL")
            author = Prompt.ask("Enter The Author")
            insert(name, url, author)
        if action == "delete":
            record_key = str(Prompt.ask("Enter the key", choices=[
                             "name", "url", "author", "hash", "date"], default="name"))
            record_value = str(Prompt.ask("Enter the Value"))
            delete(record_key, record_value)
        if action == "drop":
            drop()
        if action == "edit":
            record_key = str(Prompt.ask("Enter the key", choices=[
                             "name", "url", "author", "hash", "date"], default="name"))
            record_value = str(Prompt.ask("Enter the Value"))
            edit(record_key, record_value)
        if action == "hash":
            hash()
        if action == "quit":
            loop = 12

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        connection.commit()
        cursor.close()
        connection.close()
        console.print(":red_heart: Thanks for using db.py")
