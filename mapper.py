import os.path
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import folium
import time
from PIL import Image
from io import BytesIO
import sql

# Creates all the map files
def create_all_maps(incidents, c_i, suspects, i_id2iid, chars):
    adventures_of_bob_and_steve = Options()
    adventures_of_bob_and_steve.headless = True
    build_map_all_incidents(incidents, c_i, 'Incidents_Map', adventures_of_bob_and_steve, i_id2iid, chars)
    build_maps_solved_unsolved(suspects, incidents, i_id2iid, 'Solved vs Unsolved', adventures_of_bob_and_steve)
    build_maps_by_month(adventures_of_bob_and_steve)

# Builds maps of incidents each month
def build_maps_by_month(adventures_of_bob_and_steve):
    print('Creating monthly maps')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
              'September', 'October', 'November', 'December']
    select = sql.select_all_data('data.db', 'Incidents')
    all_months = []
    for month in months:
        this_month = []
        for item in select:
            if item[2][:len(month)] == month:
                this_month.append(item)
        all_months.append(this_month)
    for month in all_months:
        if len(month) > 0:
            my_date = month[0][2]
            loc = my_date.find(' ')
            title = f'Monthy_Map_{my_date[:loc]}'
            create_month_map(title, month, adventures_of_bob_and_steve)

# Creates a specific month's map
def create_month_map(title, items, adventures_of_bob_and_steve):
    print(f'Creating {title}')
    map = folium.Map(location=[39.8355, -99.0909], zoom_start=5, control_scale=True)
    for item in items:
        ttip = '<strong>Incident: </strong>' + str(item[1])
        line = '<strong>Incident: </strong>' + str(item[1]) + '<br>Date: ' + str(item[2]) + \
               'Address:<br>' + str(item[3]) + '<br>' + str(item[4]) + ", " + str(item[5])
        my_popup = folium.Popup(line, max_width=500)
        latitude = float(item[6])
        longitude = float(item[7])
        folium.Marker([latitude, longitude], popup=my_popup, tooltip=ttip,
                      icon=folium.Icon(color='red')).add_to(map)
    file = f'Maps/{title}.html'
    map.save(file)
    screenshot_it(file, adventures_of_bob_and_steve)

# Creates a map showing if incident is solved vs unsolved (no suspects)
def build_maps_solved_unsolved(suspects, incidents, i_id2iid, title, adventures_of_bob_and_steve):
    print('Creating Solved/Unsolved Map')
    sus = [i_id2iid[row['Incident ID']] for index, row in suspects.iterrows()]
    has_suspects = []
    for item in sus:
        if item not in has_suspects:
            has_suspects.append(item)
    all_incidents = [row['Incident ID'] for index, row in incidents.iterrows()]
    map = folium.Map(location=[39.8355, -99.0909], zoom_start=5, control_scale=True)
    legend = """<div style='position:fixed;top: 20px; left: 50px; width: 275px; height: 100px; background-color: rgb(240, 234, 214);
        border: 1px solid black;padding-left:10px;padding-top:10px;z-index: 900;'><h5 style='text-align:center;
        font-weight:bold;'>Legend</h5><table><tr><td style='width:100px;'>Solved</td><td>
        <div style='width:25px;height:10px;background-color:blue;'></div></td></tr>
        <tr><td style='width:100px;'>Unsolved</td><td><div style='width:25px;height:10px;background-color:red;'></div></td></tr></table></div>"""
    for index, location_info in incidents.iterrows():
        sel = sql.select_all_where('data.db', 'Victims', ['id_of_incident'], [location_info['ID']], ['INT'])
        sel2 = sql.select_all_where('data.db', 'Suspects', ['id_of_incident'], [location_info['ID']], ['INT'])
        line = '<strong>Incident: </strong>' + str(location_info['Incident ID']) + '<br>' + \
               str(location_info['City']) + ", " + str(location_info['State']) + "<br># of Victims: " \
               + str(len(sel)) + "<br># of Suspects: " + str(len(sel2))
        popup = folium.Popup(line, max_width=500)
        ttip = '<strong>Incident: </strong>' + str(location_info['Incident ID'])
        if location_info['Incident ID'] in has_suspects:
            color = 'blue'
        else:
            color = 'red'
        folium.Marker([location_info["Latitude"], location_info["Longitude"]], popup=popup, tooltip=ttip,
                      icon=folium.Icon(color=color)).add_to(map)
    file = f'Maps/{title}.html'
    map.get_root().html.add_child(folium.Element(legend))
    map.save(file)
    screenshot_it(file, adventures_of_bob_and_steve)

# Builds a map of all the incidents, color coding markers by the characteristics of the incident
def build_map_all_incidents(incidents, c_i, title, adventures_of_bob_and_steve, i_id2iid, chars):
    print(f'Creating {title}')
    cid = {}
    for index, row in c_i.iterrows():
        code1 = i_id2iid[row['Incident ID']]
        code2 = chars[row['Characteristic ID']]
        if code1 not in cid.keys():
            tmp = []
        else:
            tmp = cid[code1]
        tmp.append(code2)
        cid[code1] = tmp
    color_code_dict = {'Drive-by': 'red','Party': 'green','Bar/Club': 'purple',
                       'Fight @ Illegal Street Race': 'orange','Fight': 'orange','Armed Robbery': 'pink',
                       'Domestic Violence:': 'rgb(255,114,118)', 'Execution': 'darkred', 'Home Invasion': 'beige',
                       'Shootout': 'darkblue','Workplace': 'darkgreen','School': 'cadetblue',
                       'Parking Lot': 'rgb(152,29,151)', 'College': 'lightblue', 'Ghost gun': 'white',
                       'Church' : 'lightgreen', 'Other or Unknown': 'blue', 'Drive-by & Party' : 'gray',
                       'Home Invasion & Domestic Violence  ': 'lightgray', 'Drive-by & Bar/Club': 'black'}
    legend = """<div style='position:fixed;top: 20px; left: 50px; width: 275px; height: 500px; background-color: rgb(240, 234, 214);
    border: 1px solid black;padding-left:10px;padding-top:10px;z-index: 900;'><h5 style='text-align:center;
    font-weight:bold;'>Characteristic Color Code</h5><table>"""
    for k, v in color_code_dict.items():
        legend += f"""<tr><td>{k}</td><td><div style='width:25px;height:10px;background-color:{v};'></div></td></tr>"""
    legend += """</table></div>"""
    map = folium.Map(location=[39.8355, -99.0909],zoom_start=5, control_scale=True)
    for index, location_info in incidents.iterrows():
        line = '<strong>Incident: </strong>' + str(location_info['Incident ID']) + '<br>' + \
               str(location_info['City']) + ", " + str(location_info['State'])
        sel = sql.select_all_where('data.db', 'Victims', ['id_of_incident'], [location_info['ID']], ['INT'])
        sel2 = sql.select_all_where('data.db', 'Suspects', ['id_of_incident'], [location_info['ID']], ['INT'])
        line += '<br># of Victims: ' + str(len(sel)) + "<br># of Suspects: " + str(len(sel2))
        popup = folium.Popup(line, max_width=500)
        ttip = '<strong>Incident: </strong>' + str(location_info['Incident ID'])
        color = get_color(location_info, cid)
        folium.Marker([location_info["Latitude"], location_info["Longitude"]], popup=popup, tooltip=ttip,
                      icon=folium.Icon(color=color)).add_to(map)
    if not os.path.exists('Maps'):
        os.mkdir('Maps')
    map.get_root().html.add_child(folium.Element(legend))
    file = f'Maps/{title}.html'
    map.save(file)
    screenshot_it(file, adventures_of_bob_and_steve)

# Returns the color to make the marker
def get_color(row, cid):
    if row['Incident ID'] not in cid.keys():
        return 'blue'
    else:
        if len(cid[row['Incident ID']]) == 1:
            if cid[row['Incident ID']][0] == 'Drive-by':
                return 'red'
            elif cid[row['Incident ID']][0] == 'Party':
                return 'green'
            elif cid[row['Incident ID']][0] == 'Bar/Club':
                return 'purple'
            elif cid[row['Incident ID']][0] == 'Fight @ Illegal Street Race' or cid[row['Incident ID']][0] == 'Fight':
                return 'orange'
            elif cid[row['Incident ID']][0] == 'Execution':
                return 'darkred'
            elif cid[row['Incident ID']][0] == 'Domestic Violence':
                return 'lightred'
            elif cid[row['Incident ID']][0] == 'Home Invasion':
                return 'beige'
            elif cid[row['Incident ID']][0] == 'Shootout':
                return 'darkblue'
            elif cid[row['Incident ID']][0] == 'Workplace':
                return 'darkgreen'
            elif cid[row['Incident ID']][0] == 'School':
                return 'cadetblue'
            elif cid[row['Incident ID']][0] == 'Parking Lot':
                return 'darkpurple'
            elif cid[row['Incident ID']][0] == 'College':
                return 'lightblue'
            elif cid[row['Incident ID']][0] == 'Ghost gun':
                return 'white'
            elif cid[row['Incident ID']][0] == 'Armed Robbery':
                return 'pink'
            else:
                return 'lightgreen'
        else:
            if (cid[row['Incident ID']][0] == 'Drive-by' and cid[row['Incident ID']][1] == 'Party') or (cid[row['Incident ID']][0] == 'Party' and cid[row['Incident ID']][1] == 'Drive-by'):
                return 'gray'
            elif (cid[row['Incident ID']][0] == 'Home Invasion' and cid[row['Incident ID']][1] == 'Domestic Violence'):
                return 'lightgray'
            elif (cid[row['Incident ID']][0] == 'Drive-by' and cid[row['Incident ID']][1] == 'Bar/Club'):
                return 'black'
            else:
                print(cid[row['Incident ID']])
                time.sleep(3000)

# Opens file and creates the image of the file
def screenshot_it(file, adventures_of_bob_and_steve):
    driver = webdriver.Chrome('chromedriver.exe', options=adventures_of_bob_and_steve)
    cwd = os.getcwd().replace('\\','/')
    file_name = 'file:///' + cwd + '/' + file
    driver.get(file_name)
    driver.maximize_window()
    time.sleep(3)
    png = driver.get_screenshot_as_png()
    element = driver.find_element(By.CLASS_NAME, 'folium-map')
    location = element.location
    size = driver.get_window_size()
    driver.quit()
    resize_it(png, location, size, file)

# Saves the actual image of the file
def resize_it(png, location, size, file):
    im = Image.open(BytesIO(png))
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))
    if not os.path.exists('Map_Screenshots'):
        os.mkdir('Map_Screenshots')
    file = 'Map_Screenshots' + file[4:-4] + 'png'
    im.save(file)