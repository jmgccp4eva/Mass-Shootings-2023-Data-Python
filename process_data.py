import time
import plotter as plt
import pandas as pd
import sql
import tables as tbls
import mapper
import pager

# Called by main to process all the data and make everything needed from that data
def process_data(db, tables):
    incidents, characteristics, c_i, victims, suspects = retrieve_all_data(db, tables)
    i_id2iid, chars = tbls.create_tables(incidents, characteristics, c_i, victims, suspects)
    plt.create_plots(db, incidents, characteristics, c_i, victims, suspects)
    mapper.create_all_maps(incidents, c_i, suspects, i_id2iid, chars)
    pager.build_index()

# Retrieves all the data from sql and cleans the data, returning each table as pandas dataframe
def retrieve_all_data(db, tables):
    cols = [{0: 'ID', 1: 'Incident ID', 2: 'Date', 3: 'Address', 4: 'City', 5: 'State', 6: 'Latitude', 7: 'Longitude'},
            {0: 'ID', 1: 'Characteristic'}, {0: 'ID', 1: 'Incident ID', 2: 'Characteristic ID'},
            {0: 'ID', 1: 'Incident ID', 2: 'Name', 3: 'Age', 4: 'Age Group', 5: 'Gender', 6: 'Status'},
            {0: 'ID', 1: 'Incident ID', 2: 'Name', 3: 'Age', 4: 'Age Group', 5: 'Gender', 6: 'Status'}]
    keeps = [['ID', 'Incident ID', 'Date', 'City', 'State', 'Latitude', 'Longitude']]
    data = []
    for x in range(len(cols)):
        if x == 0:
            keep = keeps[0]
        else:
            keep = 'all'
        this_data = clean_dataframe(pd.DataFrame(sql.select_all_data(db, tables[x])), cols[x], keep)
        data.append(this_data)
    return data[0], data[1], data[2], data[3], data[4]

# Renames the columns appropriately
def rename_cols(df, cols):
    df = df.rename(columns=cols)
    return df

# Takes a dataframe, renames columns, drops duplicates and gets rid of unneeded columns
# then returns updated dataframe
def clean_dataframe(df, cols, keep_cols):
    df = rename_cols(df, cols)
    df.drop_duplicates()
    if keep_cols == 'all':
        return df
    df = df[keep_cols]
    return df