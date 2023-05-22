import os.path
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO

# Creates all tables (not for SQL) for HTML
def create_tables(incidents, characteristics, c_i, victims, suspects):
    adventures_of_bob_and_steve = Options()
    adventures_of_bob_and_steve.headless = True
    i_id2iid = create_incident_table(incidents, 'Incidents', adventures_of_bob_and_steve)
    chars = create_characteristics_table(characteristics, c_i, 'Characteristics', i_id2iid, adventures_of_bob_and_steve)
    create_person_table(victims, 'Victims', i_id2iid, adventures_of_bob_and_steve)
    create_person_table(suspects, 'Suspects', i_id2iid, adventures_of_bob_and_steve)
    return i_id2iid, chars

# Creates tables for Victims and Suspects, also creates the html and images for thumbnails
def create_person_table(df, title, i_id2iid, adventures_of_bob_and_steve):
    print(f'Creating {title} table')
    df = df.drop(['ID'], axis=1)
    cols = get_column_names(df)
    table_header = build_table_head(cols, ['ID'], title)
    df = replace_data(df, cols, i_id2iid)
    table_body = build_table_body(df, cols, [])
    file = f'Tables/{title}.html'
    build_table(table_body, table_header, title, file)
    screenshot_it(file, adventures_of_bob_and_steve)

# Replaces data and returns a new dataframe
def replace_data(df, cols, i_id2iid):
    iids = []
    names = []
    ages = []
    groups = []
    genders = []
    stati = []
    for index, row in df.iterrows():
        iids.append(i_id2iid[row[cols[0]]])
        names.append(row[cols[1]])
        try:
            ages.append(int(float(row[cols[2]])))
        except ValueError:
            ages.append(row[cols[2]])
        groups.append(row[cols[3]])
        genders.append(row[cols[4]])
        stati.append(row[cols[5]])
    my_dict = {}
    my_dict[cols[0]] = iids
    my_dict[cols[1]] = names
    my_dict[cols[2]] = ages
    my_dict[cols[3]] = groups
    my_dict[cols[4]] = genders
    my_dict[cols[5]] = stati
    new_df = pd.DataFrame(my_dict)
    return new_df

# Creates HTML table for Characteristics, also creates the html and images for thumbnails
def create_characteristics_table(characteristics, c_i, title, i_id2iid, adventures_of_bob_and_steve):
    print(f'Creating {title} table')
    chars = {}
    for index, row in characteristics.iterrows():
        chars[row['ID']] = row['Characteristic']
    c_i = c_i.drop(['ID'], axis=1)
    c_i = c_i.rename(columns={'Characteristic ID' : 'Characteristic'})
    cols = get_column_names(c_i)
    table_header = build_table_head(cols, ['ID'], title)
    c_i = replace_char_table_data(c_i, cols, chars, i_id2iid)
    table_body = build_table_body(c_i, cols, [])
    file = 'Tables/Characteristics.html'
    build_table(table_body, table_header, title, file)
    screenshot_it(file, adventures_of_bob_and_steve)
    return chars

# Replaces the character table data
def replace_char_table_data(c_i, cols, chars, i_id2iid):
    iids = []
    char_info =[]
    for index, row in c_i.iterrows():
        iids.append(i_id2iid[row[cols[0]]])
        char_info.append(chars[row[cols[1]]])
    my_dict = {}
    my_dict[cols[0]] = iids
    my_dict[cols[1]] = char_info
    df = pd.DataFrame(my_dict)
    return df

# Creates HTML table for Incidents, also creates the html and images for thumbnails
def create_incident_table(incidents, title, adventures_of_bob_and_steve):
    print(f'Creating {title} table')
    i_id2iid = get_id_to_incident_id(incidents)
    cols = get_column_names(incidents)
    table_header = build_table_head(cols, ['ID'], title)
    table_body = build_table_body(incidents, cols, ['ID'])
    file = 'Tables/Incidents.html'
    build_table(table_body, table_header, title, file)
    screenshot_it(file, adventures_of_bob_and_steve)
    return i_id2iid

# Opens a Selenium page showing the table and makes a screenshot of it
# Because of Bob and Steve, the opening will be hidden from view
def screenshot_it(file, adventures_of_bob_and_steve):
    driver = webdriver.Chrome('chromedriver.exe', options=adventures_of_bob_and_steve)
    cwd = os.getcwd().replace('\\','/')
    file_name = 'file:///' + cwd + '/' + file
    driver.get(file_name)
    driver.maximize_window()
    time.sleep(3)
    element = driver.find_element(By.CLASS_NAME, 'myTable')
    location = element.location
    size = driver.get_window_size()
    png = driver.get_screenshot_as_png()
    driver.quit()
    resize_it(png, location, size, file)

# Resizes and saves the image
def resize_it(png, location, size, file):
    im = Image.open(BytesIO(png))
    left = location['x']
    top = location['y'] - 60
    right = location['x'] + size['width']
    bottom = size['height']
    im = im.crop((left, top, right, bottom))
    if not os.path.exists('Screenshots'):
        os.mkdir('Screenshots')
    file = 'Screenshots' + file[6:-4] + 'png'
    im.save(file)

# Builds an HTML table
def build_table(table_body, table_header, title, file):
    style = '<style>h3 {text-align: center;} .myTable { width:100%;text-align: left;background-color: white;}.myTable th {background-color: lightblue;text-align: center;}#second td{background-color: lightgray;}</style>'
    html = f'<!DOCTYPE html><html lang="en-US"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width" /><title>{title}</title>{style}</head><body><table class="myTable">'
    html += table_header
    html += table_body
    html += '</table></body></html>'
    if not os.path.exists('Tables'):
        os.mkdir('Tables')
    with open(file, 'w', encoding='utf-8') as fout:
        fout.write(html)

# Builds the body for HTML table
def build_table_body(df, cols, skip):
    tbody = ''
    first = True
    for index, row in df.iterrows():
        if not first:
            tbody += '<tr id="second">'
            first = True
        else:
            tbody += '<tr id="first">'
            first = False
        for col in cols:
            if col not in skip:
                tbody += f"<td>{row[col]}</td>"
        tbody += '</tr>'
    return tbody

# Builds the header for HTML table
def build_table_head(cols, skip, title):
    thead = f'<h3>{title}</h3><thead><tr>'
    for col in cols:
        if col not in skip:
            thead += f'<th>{col}</th>'
    thead += '</tr></thead>'
    return thead

# Builds a dictionary to translate id to Incident ID
def get_id_to_incident_id(df):
    my_dict = {}
    for index, row in df.iterrows():
        my_dict[row['ID']] = row['Incident ID']
    return my_dict

# Returns the column names from a dataframe
def get_column_names(df):
    cols = []
    for col in df.columns:
        cols.append(col)
    return cols