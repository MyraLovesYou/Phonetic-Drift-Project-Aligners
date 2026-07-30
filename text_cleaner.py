import pandas as pd
from dateutil import parser
import sys
df = ""
try:
    print("Enter Excel File Path:")
    df = pd.read_excel(input())
except:
    sys.exit("Error: Excel file not found.")
