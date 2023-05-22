import os.path
import matplotlib.pyplot as plt
import pandas as pd
import sql

# Called to create all of the charts
def create_plots(db, incidents, characteristics, c_i, victims, suspects):
    build_num_ms_by_numbers(db, incidents)
    build_ages_of_suspects_and_victims(victims, suspects)
    build_suspect_status_tables(incidents, suspects)
    build_victim_status_tables(victims)
    build_comparison_by_characteristic(characteristics, c_i)
    build_incidents_by_state(incidents)

# Iterates over incidents dataframe to get a list of states
def build_states(incidents):
    states = set()
    for index, row in incidents.iterrows():
        states.add(row['State'])
    return list(states)

# Counts number of times state is in incidents
def build_counts(states, incidents):
    counts = {}
    for state in states: counts[state] = 0
    for index, row in incidents.iterrows():
        counts[row['State']] += 1
    return counts, sorted(counts.items(), key=lambda x: x[1], reverse=True)

# Separates states into those with top 10 most occurrences and the rest (others)
def build_top_10(counts):
    top_10 = {}
    others = {}
    for x in range(len(counts)):
        if len(top_10) < 10:
            top_10[counts[x][0]] = counts[x][1]
        else:
            others[counts[x][0]] = counts[x][1]
    return top_10, others

# Sorts the counts by the state names
def alphabetize_counts_by_keys(counts):
    alph = sorted(counts.keys())
    alphabetized = {}
    for a in alph: alphabetized[a] = 0
    for k, v in counts.items():
        alphabetized[k] = v
    return alphabetized

# Builds files for how many Incidents occurred in each state
def build_incidents_by_state(incidents):
    states = build_states(incidents)
    counts, s_counts = build_counts(states, incidents)
    a_counts = alphabetize_counts_by_keys(counts)
    my_dict = {}
    my_vals = [val for val in a_counts.values()]
    my_names = [key for key in a_counts.keys()]
    my_dict['Quantities'] = my_vals
    my_dict['States'] = my_names
    df = pd.DataFrame(data=my_dict)
    my_bar = df.plot.bar(title='Incidents by State', x='States', y='Quantities',
                          legend=False, figsize=(10,14)).get_figure()
    my_bar.savefig('Images/IncidentsByState.png')

# Builds charts by Characteristic (i.e. Drive-by, @ a Bar, @ a party, etc.)
def build_comparison_by_characteristic(characteristics, c_i):
    char_in_chars = {}
    char_count = {}
    for index, row in characteristics.iterrows():
        char_in_chars[row['ID']] = row['Characteristic']
        char_count[row['ID']] = 0
    for index, row in c_i.iterrows():
        char_count[row['Characteristic ID']] += 1
    my_dict = {}
    my_vals = [val for val in char_count.values()]
    my_names = [val for val in char_in_chars.values()]
    my_dict['Quantities'] = my_vals
    my_dict['Characteristics'] = my_names
    df = pd.DataFrame(data=my_dict)
    my_bar = df.plot.barh(title='Characteristics of Incidents', x='Characteristics', y='Quantities',
                         legend=False, figsize=(16, 5)).get_figure()
    my_bar.savefig('Images/Characteristics_of_Incidents.png')

# Builds Chart for Victims and Suspects by their ages
def build_by_age(df, title, file, my_keys, title2, file2):
    max_age = get_max_age(df)
    known_unknown = [0] * 2
    ages = [0] * (max_age + 1)
    for index, row in df.iterrows():
        if len(row['Age']) > 0:
            ages[int(float(row['Age']))] += 1
            known_unknown[0] += 1
        else:
            known_unknown[1] += 1
    positions = range(len(ages))
    plot_it('bar', positions, ages, 'Age', 'Quantity', file, title, ['black', 'red', 'green', 'blue', 'orange', 'magenta'])
    plot_it('pie', my_keys, known_unknown, None, None, file2,
            title2, ['red', 'gold'])

# Gets the max age of victims or suspects
def get_max_age(df):
    max_age = -1
    for index, row in df.iterrows():
        if len(row['Age']) > 0:
            if int(float(row['Age'])) > max_age:
                max_age = int(float(row['Age']))
    return max_age

# Called to build the ages of victims and ages of suspects charts
def build_ages_of_suspects_and_victims(victims, suspects):
    build_by_age(victims, 'Ages of Victims','Images/AgesOfVictims.png', ['Known Age', 'Unknown Age'],
                 'Known vs Unknown Age of Victims', 'Images/KnownVsUnknownAgesVictims.png')
    build_by_age(suspects, 'Ages of Suspects', 'Images/AgesOfSuspects.png', ['Known Age', 'Unknown Age'],
                 'Known vs Unknown Age of Suspects', 'Images/KnownVsUnknownAgesSuspects.png')

# Builds charts for whether victim is dead, injured, etc.
def build_victim_status_tables(victims):
    stati = []
    for index, row in victims.iterrows():
        if row['Status'] not in stati:
            stati.append(row['Status'])
    status = [0] * 3
    for index, row in victims.iterrows():
        if row['Status'] == 'Killed':
            status[0] += 1
        elif row['Status'] == 'Injured':
            status[1] += 1
        else:
            status[2] += 1
    plot_it('pie', ['Killed', 'Injured'], [status[0], status[1]], None, None,
            'Images/HarmToVictims.png', 'Killed Vs. Injured Victims', ['gray', 'green'])

# Builds charts of whether suspect is arrested, injured, dead, etc.
def build_suspect_status_tables(incidents, suspects):
    at_large = 0
    injured = 0
    killed = 0
    unharmed = 0
    arrested = 0
    solved = set()
    for index, row in suspects.iterrows():
        solved.add(row['Incident ID'])
        if row['Status'] == 'Unharmed':
            unharmed += 1
            at_large += 1
        elif row['Status'] == 'Arrested':
            unharmed += 1
            arrested += 1
        elif row['Status'] == 'Killed':
            killed += 1
        elif row['Status'] == 'Injured, Arrested':
            injured += 1
            arrested += 1
        else:
            injured += 1
            at_large += 1
    plot_it('pie', ['Unharmed', 'Injured', 'Dead'], [unharmed, injured, killed], None, None, 'Images/HarmStatusSuspects.png',
            'Unharmed Vs. Injured Vs. Dead Suspects', ['green', 'blue', 'gold'])
    plot_it('pie', ['Arrested', 'At Large', 'Dead'], [arrested, at_large, killed], None, None, 'Images/ArrestStatusSuspects.png',
            'Arrested Vs. At Large Vs. Dead Suspects', ['orange', 'red', 'gray'])
    solved = list(solved)
    unsolved = [row['ID'] for index, row in incidents.iterrows() if row['ID'] not in solved]
    plot_it('pie', ['Solved', 'Unsolved'], [len(solved), len(unsolved)], None, None, 'Images/SolvedVsUnsolved.png',
            'Solved Vs. Unsolved', ['gold', 'red'])

# Sorts a dictionary of data, extracting out sizes, keys and values
def sort_dict_and_extract(sizes):
    my_keys = list(sizes.keys())
    my_keys.sort()
    sizes = {i: sizes[i] for i in my_keys}
    my_vals = list(sizes.values())
    sizes2 = [0, 0]
    for k, v in sizes.items():
        if k <= 6:
            sizes2[0] += int(v)
        else:
            sizes2[1] += int(v)
    return sizes, sizes2, my_keys, my_vals

# Creates a dictionary for keys = # of victims in incident and value = count of # of incidents
# of that particular size
def build_sizes_dict(db, incidents):
    sizes = {}
    for index, row in incidents.iterrows():
        iid = row[0]
        select = sql.select_all_where(db, 'Victims', ['id_of_incident'], [iid], ['INT'])
        if len(select) in sizes.keys():
            sizes[len(select)] += 1
        else:
            sizes[len(select)] = 1
    return sizes

# Plots the actual chart
def plot_it(typ, my_keys, my_vals, xlab, ylab, file, title, colors):
    if typ == 'bar':
        if colors is not None:
            plt.bar(my_keys, my_vals, color=colors)
        else:
            plt.bar(my_keys, my_vals)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.title(title)
        plt.savefig(file)
        plt.clf()
    elif typ == 'pie':
        vals = []
        for val in my_vals:
            vals.append(val / sum(my_vals))
        plt.pie(vals, labels=my_keys, colors=colors, autopct="%2.1f%%")
        plt.title(title)
        plt.savefig(file)
        plt.clf()
    print(f'Chart: "{title}" created')

# Builds charts for Number of Victims vs Qty and pie chart 4-6 victims vs more than 6 victims
def build_num_ms_by_numbers(db, incidents):
    sizes = build_sizes_dict(db, incidents)
    sizes, sizes2, my_keys, my_vals = sort_dict_and_extract(sizes)
    if not os.path.exists('Images'):
        os.mkdir('Images')
    plot_it("bar", my_keys, my_vals, "Number of victims", "Quantity", 'Images/NumCrimesVNumVictims.png',
            'Number of Crimes per Number of Victim', None)
    plot_it('pie', ['4 to 6 Victims', 'More Than 6 Victims'], sizes2, None, None, 'Images/UpTo6VictimsVsMore.png',
            '4 to 6 Victims Vs. More Than 6 Victims', ['red', 'gold'])
