import os

# Builds the final page...index.html to open everything else up
def build_index():
    print('Creating index.html')
    html = '<!doctype html><html lang="en"><head><meta charset="utf-8">' \
           '<meta name="viewport" content="width=device-width, initial-scale=1">' \
           '<title>Mass Shootings Data 2023</title>' \
           '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css"rel="stylesheet">' \
           '<style>.row{padding-bottom:10px;}p{text-align:center;}.col,.col-sm-2{padding: 20px;' \
           'h3{text-align:center;padding-top:20px;color:blue;}</style></head><body><div class="container">' \
           '<div class="row"><h1 style="text-align:center;padding-bottom:10px;">Mass Shootings Data 2023</h1></div>'
    html += '<div class="row"><h3>Table Data</h3></div><div class="row">'
    screenshots_files = os.listdir('Screenshots')
    tables_files = os.listdir('Tables')
    for x in range(len(screenshots_files)):
        html += '<div class="col"><p>' + screenshots_files[x][:-4] + '</p><a href="Tables/' + tables_files[x] + \
                '" target="_blank"><img class="img-thumbnail" src="Screenshots/' + screenshots_files[x] + \
                '"></a></div>'
    html += '</div><div class="row"><h3>Charts</h3></div><div class="row">'
    titles = ['Ages of Suspects', 'Ages of Victims', 'Suspect Arrests', 'Characteristics of Incidents',
              'Suspect Harm Status', 'Harm to Victims', 'Incidents by State', 'Suspect Ages', 'Victim Ages',
              '# Crime / # Victims', 'Solved vs Unsolved', '4-6 vs 6+ Victims']
    images_files = os.listdir('Images')
    for x in range(len(images_files)):
        html += '<div class="col-sm-2"><p>' + titles[x] + '</p><a href="Images/' + images_files[x] + \
                '" target="_blank"><img class="img-thumbnail" src="Images/' + images_files[x] + \
                '"></a></div>'
    html += '</div><div class="row"><h3>Maps</h3></div><div class="row">'
    ms_files = os.listdir('Map_Screenshots')
    map_files = os.listdir('Maps')
    for x in range(len(ms_files)):
        html += '<div class="col-sm-2"><p>' + ms_files[x][:-4].replace("_", " ") + '</p><a href="Maps/' + \
                map_files[x] + '" target="_blank"><img class="img-thumbnail" src="Map_Screenshots/' + \
                ms_files[x] + '"></a></div>'
    html += '</div>'
    html += '</div><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js">' \
            '</script></body></html>'
    with open('index.html', 'w', encoding='utf-8') as fout: fout.write(html)
