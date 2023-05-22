import sqlite3
import pandas as pd

# Initial set up of database method
# Takes about 20 seconds to create all 5 tables and their indices,
# Read through 2 files, creating Pandas data frames, iterating over
# them multiple times to populate all 5 tables
def initial_set_up(db, tables):
    # files needed
    file = 'Mass Shooting Details.xlsx'
    file2 = 'export.csv'
    lat_long_dict = {}
    char_dict = {}
    fields = [['id', 'incident_id', 'incident_date', 'address', 'city', 'state', 'latitude', 'longitude'],
              ['id', 'characteristic'],
              ['id', 'id_of_incident', 'id_of_characteristics', 'FOREIGN KEY(id_of_incident)',
               'FOREIGN KEY(id_of_characteristics)'],
              ['id', 'id_of_incident', 'name', 'age', 'age_group', 'gender', 'status', 'FOREIGN KEY(id_of_incident)'],
              ['id', 'id_of_incident', 'name', 'age', 'age_group', 'gender', 'status', 'FOREIGN KEY(id_of_incident)']]
    types = [['INTEGER PRIMARY KEY', 'INT', 'TEXT', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(12)', 'REAL', 'REAL'],
             ['INTEGER PRIMARY KEY', 'VARCHAR(30)'],
             ['INTEGER PRIMARY KEY', 'INT', 'INT', 'REFERENCES Incidents(id)',
              'REFERENCES Characteristics(id)'],
             ['INTEGER PRIMARY KEY', 'INT', 'VARCHAR(50)', 'VARCHAR(3)', 'VARCHAR(10)', 'VARCHAR(6)', 'VARCHAR(20)',
              'REFERENCES Incidents(id)'],
             ['INTEGER PRIMARY KEY', 'INT', 'VARCHAR(50)', 'VARCHAR(3)', 'VARCHAR(10)', 'VARCHAR(6)', 'VARCHAR(20)',
              'REFERENCES Incidents(id)']]
    indices = [[('incident_id', 'incident_id_index')],
               [('characteristic', 'characteristic_characteristic_index')],
               [('id_of_incident', 'incident_CI_index'), ('id_of_characteristics', 'characteristics_CI_index')],
               [('age', 'age_victims_index'), ('age_group', 'age_group_victims_index'),
                ('gender', 'gender_victims_index'), ('status', 'status_victims_index')],
               [('age', 'age_suspects_index'), ('age_group', 'age_group_supects_index'),
                ('gender', 'gender_suspects_index'), ('status', 'status_suspects_index')]]
    fields, types = create_all_tables(db, tables, fields, types, indices)
    del indices
    df = pd.read_excel(file)
    char_dict, lat_long_dict = get_dictionaries(df, char_dict, lat_long_dict)
    char_dict = insert_characteristic_data(db, tables[1], fields[1], types[1], char_dict)
    df2 = pd.read_csv(file2)
    incidents = insert_incidents_data(db, df2, {}, tables[0], fields[0], types[0], lat_long_dict)
    insert_char_inc_data(db, df, tables[2], fields[2], types[2], incidents, char_dict)
    insert_victims_and_suspects_data(db, df, tables, fields, types, incidents)
    print('All tables complete')

# Inserts Victims and Suspects data into respective tables
def insert_victims_and_suspects_data(db, df, tables, fields, types, incidents):
    victims = []
    suspects = []
    for index, row in df.iterrows():
        my_id = incidents[row['Incident ID']]
        v_or_s = row['Type']
        if pd.isna(row['Name']):
            name = ""
        else:
            name = row['Name'].replace('"', "'")
        if pd.isna(row['Age']):
            age = ""
        else:
            age = row['Age']
        if pd.isna(row['Age Group']):
            age_group = ""
        else:
            age_group = row['Age Group']
        if pd.isna(row['Gender']):
            gender = None
        else:
            gender = row['Gender']
        status = row['Status']
        if v_or_s == 'Victim':
            victims.append([incidents[row['Incident ID']], name, age, age_group, gender, status])
        elif v_or_s == 'Suspect':
            suspects.append([incidents[row['Incident ID']], name, age, age_group, gender, status])
    for v in victims:
        insert_into_table(db, tables[3], fields[3], v, types[3])
    print('Victims table complete')
    for s in suspects:
        insert_into_table(db, tables[4], fields[4], s, types[4])
    print('Suspects table complete')

# Inserts data into Characteristics_Incidents table
# FK to Characteristics table, FK to Incidents table, PK auto increment
def insert_char_inc_data(db, df, table, fields, types, incidents, char_dict):
    incidents_read = []
    i_c_data = {}
    for index, row in df.iterrows():
        incident = incidents[row['Incident ID']]
        if incident not in incidents_read:
            tmp = []
            if not pd.isna(row['Characteristic1']):
                tmp.append(char_dict[row['Characteristic1'].strip()])
                if not pd.isna(row['Characteristic2']):
                    tmp.append(char_dict[row['Characteristic2'].strip()])
            i_c_data[incident] = tmp
            incidents_read.append(incident)
    for k, v in i_c_data.items():
        for x in v:
            val = []
            val.append(k)
            val.append(x)
            insert_into_table(db, table, fields, val, types)
    print('Characteristics/Incidents table complete')

# Selects what data from table provided where field(s) provided = value(s) provided
def select_what_from_where(db, table, fields, values, types, what):
    temp = "SELECT {} FROM {} WHERE ".format(what, table)
    for a in range(0, len(fields)):
        if a > 0:
            temp += " AND "
        temp += fields[a]
        temp += "="
        if types[a] == 'TEXT':
            temp += '"'
        temp += str(values[a])
        if types[a] == 'TEXT':
            temp += '"'
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(temp)
    return cur.fetchall()

# Inserts all incident data into Incidents table
def insert_incidents_data(db, df, incidents, table, fields, types, lat_long_dict):
    for index, row in df.iterrows():
        incidents[row['Incident ID']] = [row['Incident ID'], row['Incident Date'], row['Address'],
                                         row['City Or County'], row['State'],
                                         lat_long_dict[row['Incident ID']][0],
                                         lat_long_dict[row['Incident ID']][1]]
    for v in incidents.values():
        insert_into_table(db, table, fields, v, types)
    for k in incidents.keys():
        select = select_what_from_where(db, table, ['incident_id'], [k], ['INT'], 'id')[0][0]
        incidents[k] = select
    print('Inserting all Incidents into table complete')
    return incidents

# Provided, not used at the moment.  Creates a backup of the database.
def backup(db):
    conn = sqlite3.connect(db)
    b_conn = sqlite3.connect('backup1.db')
    conn.backup(b_conn)
    b_conn.close()
    conn.close()

# Returns all columns for data from table where field(s) = value(s) provided
def select_all_where(db,table_name,field,value,types):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    query = "SELECT * FROM {} WHERE ".format(table_name)
    for t in range(len(types)):
        if t>0:
            query += " AND "
        if types[t]=='TEXT':
            query += f"{field[t]}='{value[t]}'"
        else:
            query += f"{field[t]}={value[t]}"
    cur.execute(query)
    select = cur.fetchall()
    return select

# Selects and returns all data from a particular table
def select_all_data(db, table_name):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM {}""".format(table_name))
    select = cur.fetchall()
    return select

# Inserts all data into the Characteristics table
def insert_characteristic_data(db, table, fields, types, char_dict):
    for key in char_dict.keys():
        insert_into_table(db, table, fields, [key], types)
    select = select_all_data(db, table)
    for item in select:
        char_dict[item[1]] = item[0]
    print('Characteristics table complete')
    return char_dict

# Call by other insert methods to insert vals for fields of types into table provided
def insert_into_table(db, table, fields, vals, types):
    temp = "("
    for a in range(0, len(fields)):
        if a > 0:
            temp += ","
        temp += fields[a]
    temp += ") VALUES ("
    for a in range(0, len(vals)):
        if a > 0:
            temp += ","
        if types[a] == "TEXT" or types[a][:7] == "VARCHAR":
            temp += "\""
        temp += str(vals[a])
        if types[a] == "TEXT" or types[a][:7] == "VARCHAR":
            temp += "\""
    temp += ")"
    query = "INSERT INTO {}{}".format(table, temp)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()

# Creates dictionaries of characteristics and latitude/longitudes
def get_dictionaries(df, char_dict, lat_long_dict):
    for index, row in df.iterrows():
        if row['Incident ID'] not in lat_long_dict.keys():
            if not pd.isna(row['Characteristic1']):
                if row['Characteristic1'] not in char_dict.keys():
                    char_dict[row['Characteristic1']] = -1
                    if not pd.isna(row['Characteristic2']):
                        if row['Characteristic2'] not in char_dict.keys():
                            char_dict[row['Characteristic2'].strip()] = -1
            lat_long_dict[row['Incident ID']] = [row['Latitude'], row['Longitude']]
    return char_dict, lat_long_dict

# Called to create all the tables in SQLite
def create_all_tables(db, tables, fields, types, indices):
    for x in range(len(tables)):
        create_table(db, tables[x], fields[x], types[x])
        for index in indices[x]:
            create_index(db, tables[x], index[0], index[1])
        if x == 2:
            fields[x], types[x] = pop_this('end', 2, fields[x], types[x])
        elif x > 2:
            fields[x], types[x] = pop_this('end', 1, fields[x], types[x])
        fields[x], types[x] = pop_this('front', 1, fields[x], types[x])
    return fields, types

# Updates fields and types by popping off items from their lists(arrays)
def pop_this(where, qty, fields, types):
    if where == 'front':
        fields.pop(0)
        types.pop(0)
    else:
        for _ in range(qty):
            fields.pop(len(fields) - 1)
            types.pop(len(types) - 1)
    return fields, types

# creates index from table and column provided
def create_index(db, table, column, index_name):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(f"""CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({column});""")
    conn.commit()
    conn.close()
    print(f'Index {index_name} created')

# Creates table from fields and types provided
def create_table(db, table, fields, types):
    query = "CREATE TABLE IF NOT EXISTS {}(".format(table)
    temp = ''
    for x in range(0, len(fields)):
        if len(temp) > 0:
            temp += ", "
        temp = temp + fields[x] + " " + types[x]
    temp += ")"
    query += temp
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()