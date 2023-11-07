import pandas as pd
import tkinter as tk
from tkinter import filedialog

def add_non_website_visits(row):
    if row.isna().iloc[2]:
        if row['url'].startswith('chrome-extension'):
            row['top domain'] = 'chrome-extension://' + row['full domain']
        else:
            row['top domain'] = row['url']
    
    return row

try:
    rolling_length = int(input('enter the number of days to average (default 7): '))
except ValueError:
    rolling_length = 7
root = tk.Tk()
root.withdraw()
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

file_path = filedialog.askopenfilename()

df = pd.read_csv(file_path, delimiter='\t', header=None)
df.columns = ['url', 'full domain', 'top domain', 'unix time', 'date', 'day of week', 'transition', 'page title']
df['date'] = pd.to_datetime(df['date']).dt.date

df = df.apply(add_non_website_visits, axis=1)

all_top_domains = df['top domain'].unique()

print(all_top_domains)

start_date = df.iloc[-1]['date']
end_date = df.iloc[0]['date']

date_range = pd.date_range(start_date, end_date, freq='D')

rolling_df = pd.DataFrame()

for i in range(0, len(date_range)-rolling_length+1):
    days = list(date_range[i:i+rolling_length])
    days = [i.date() for i in days]
    partial_df = df[df['date'].isin(days)]
    top_domains = partial_df['top domain'].unique()
    top_domains_count = {}
    for domain in top_domains:
        top_domains_count[domain] = len(partial_df[partial_df['top domain'] == domain]) / rolling_length
    name = f'{days[0]} to {days[-1]}'
    series = pd.Series(top_domains_count, name=name)
    rolling_df = pd.concat([rolling_df, pd.DataFrame({name: series})], axis=1)

rolling_df = rolling_df.transpose()

rolling_df = rolling_df.fillna(0)

rolling_df.to_csv(filedialog.asksaveasfilename(defaultextension='.tsv'), sep='\t')