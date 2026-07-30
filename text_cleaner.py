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
output_path = Path(input())
output_path.mkdir(parents=True, exist_ok=True)
print(f"Nested directories '{output_path}' created successfully.")