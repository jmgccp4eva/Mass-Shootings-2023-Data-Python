import os.path
import time
import webbrowser
from process_data import process_data as proc
import sql

# Automatically opens once everything is complete
def auto_open(path):
    html_page = f'{path}'
    # open in browser.
    new = 2
    webbrowser.open(html_page, new=new)
def main():
    start = time.perf_counter()
    db = 'data.db'
    tables = ['Incidents', 'Characteristics', 'Characteristics_Incidents', 'Victims', 'Suspects']
    if not os.path.exists(db):
        sql.initial_set_up(db, tables)
    proc(db, tables)
    end = time.perf_counter()
    diff = end - start
    auto_open('index.html')
    print(diff)

if __name__ == '__main__':
    main()