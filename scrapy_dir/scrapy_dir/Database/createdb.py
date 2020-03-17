import sqlite3
import json

conn=sqlite3.connect("stocks.db")
c=conn.cursor()
c.execute("create table if not exists stocks(code text primary key,name text)")

with open("stocks.jl","r") as f:
    for line in f.readlines():
        json_data = json.loads(line)
        code=json_data['code']
        name=json_data['name']
        values=(code,name)
        c.execute("insert into stocks values(?,?)",values)
        c.execute("commit")
