import pandas as pd
from dateutil import parser
import sys
from pathlib import Path
df = ""
try:
    print("Enter Excel File Path:")
    df = pd.read_excel(input())
except:
    sys.exit("Error: Excel file not found.")
print("Specify transcript output directory:")
output_path = input()
Path(output_path).mkdir(parents=True, exist_ok=True)
print(f"Directory '{output_path}' created successfully.")
subset = df[["Q42", "date", "FL_44_DO", "FL_43_DO"]]
subset = subset.dropna(subset=["Q42"])
for row in subset.itertuples():
    id = row.Q42
    date = row.date
    first_half = row.FL_44_DO
    second_half = row.FL_43_DO
    id = id.upper()
    if "P" not in id:
        continue
    std_dt = ""
    try:
        dt = parser.parse(date)
        std_dt = f"{dt.month}.{dt.day}"
    except parser.ParserError:
        print("Unable to automatically parse date. Please review the date:")
        print(date)
        print("Enter date in m.d format")
        std_dt = input()
    output_file = output_path + "/" + id + "_" + std_dt + ".txt"
    print(output_file)


print("Transcript Generation Complete!")