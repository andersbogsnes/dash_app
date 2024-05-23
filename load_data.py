import csv
import typing

from db import engine, crimes

def process_row(key: str, value: str) -> typing.Any:
    if key.lower() == "shooting":
        match value:
            case "Y":
                return True
            case "" | "N":
                return False
    if key.lower() in {"lat", "long"}:
        match value:
            case "":
                return None
            case _:
                return value
    return value

with open("data/crime.csv", encoding='latin-1') as f:
    reader = csv.DictReader(f)
    data = [{k.lower(): process_row(k, v) for k, v in row.items() if k != "location"}
            for row in reader]

with engine.connect() as conn:
    conn.execute(crimes.insert(), data)
    conn.commit()