import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests

def fetch_champion_data():
    champions_dict = {}
    base_champion_url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/"

    for champion_id in range(1, 999):
        champion_json_url = f"{base_champion_url}/{champion_id}.json"
        response = requests.get(champion_json_url)
        if response.status_code == 200:
            champion_data = response.json()
            alias = champion_data.get('alias', '') or champion_data.get('name', '')
            name = champion_data.get('name', '')
            if alias and name:
                champions_dict[name] = {"id": champion_id, "name": name, "alias": alias}
        else:
            continue

    return champions_dict

# Fetch the HTML content from the URL
url = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
response = requests.get(url)
html_content = response.content

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table
table = soup.find('table', {'class': 'article-table'})

if not table:
    raise Exception("Table not found on the page.")

# Extract the table headers
headers = [header.text.strip() for header in table.find_all('th')]

# Extract the rows
rows = table.find('tbody').find_all('tr')

community_dragon_data = fetch_champion_data()

# Extract data from each row
champions = []
for row in rows:
    cells = row.find_all('td')
    if len(cells) > 0:  # Only process rows that contain data
        champion_data = {}
        champion_data[headers[0]] = cells[0].find('a').get('title').split('/')[0]  # Champion name
        champion_data[headers[1]] = cells[1].text.strip()  # Classes
        champion_data[headers[2]] = cells[2].text.strip()  # Release Date
        champion_data[headers[3]] = cells[3].text.strip()  # Last Changed
        champion_data[headers[4]] = cells[4].text.strip()  # Blue Essence
        champion_data[headers[5]] = cells[5].text.strip()  # RP
        champion_in_community_dragon = community_dragon_data.get(champion_data[headers[0]], None)
        if not champion_in_community_dragon:
            raise Exception(f"Champion {champion_data[headers[0]]} not found in Community Dragon data.")
        champion_data['Champion ID'] = champion_in_community_dragon['id']
        champion_data['Alias'] = champion_in_community_dragon['alias']
        champions.append(champion_data)

# Helper functions
def convert_date_to_months(date_str, min_date):
    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(date_str, date_format)
    min_date_obj = datetime.strptime(min_date, date_format)
    delta = date_obj.year * 12 + date_obj.month - (min_date_obj.year * 12 + min_date_obj.month)
    return delta

def convert_version_to_float(version_str):
    major, minor = version_str[1:].split('.')
    return float(major) + float(minor) * 0.05

def normalize_value(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

# Convert classes and champion names to integer values
class_mapping = {}
class_counter = 0
champion_mapping = {}
for champion in champions:
    classes = champion['Classes']
    if classes not in class_mapping:
        class_mapping[classes] = class_counter
        class_counter += 1
    champion_alias = champion['Alias']
    champion_id = champion['Champion ID']
    if champion_alias not in champion_mapping:
        champion_mapping[champion_alias] = champion_id

# Find the minimum and maximum release dates
min_release_date = min(champion['Release Date'] for champion in champions)
max_release_date = max(champion['Release Date'] for champion in champions)

# Find the min and max values for Blue Essence and RP
min_be = min(int(champion['Blue Essence']) for champion in champions)
max_be = max(int(champion['Blue Essence']) for champion in champions)
min_rp = min(int(champion['RP']) for champion in champions)
max_rp = max(int(champion['RP']) for champion in champions)

# Convert the release dates to months and normalize
min_date_months = convert_date_to_months(min_release_date, min_release_date)
max_date_months = convert_date_to_months(max_release_date, min_release_date)

# Normalize the data
normalized_champions = []
for champion in champions:
    normalized_champion = {}
    normalized_champion['Champion'] = champion_mapping[champion['Alias']]
    normalized_champion['Classes'] = class_mapping[champion['Classes']]
    date_months = convert_date_to_months(champion['Release Date'], min_release_date)
    normalized_champion['Release Date'] = normalize_value(date_months, min_date_months, max_date_months)
    normalized_champion['Last Changed'] = convert_version_to_float(champion['Last Changed'])
    normalized_champion['Blue Essence'] = normalize_value(int(champion['Blue Essence']), min_be, max_be)
    normalized_champion['RP'] = normalize_value(int(champion['RP']), min_rp, max_rp)
    normalized_champions.append(normalized_champion)

# Convert the normalized list to JSON
normalized_json = json.dumps(normalized_champions, indent=4)

# Save the normalized JSON to a file
with open('normalized_champions.json', 'w', encoding='utf-8') as json_file:
    json_file.write(normalized_json)

# Create the denormalization data
denormalization_data = {
    "class_mapping": class_mapping,
    "champion_mapping": champion_mapping,
    "min_release_date": min_release_date,
    "max_release_date": max_release_date,
    "min_be": min_be,
    "max_be": max_be,
    "min_rp": min_rp,
    "max_rp": max_rp,
    "min_date_months": min_date_months,
    "max_date_months": max_date_months
}

# Convert the denormalization data to JSON
denormalization_json = json.dumps(denormalization_data, indent=4)

# Save the denormalization JSON to a file
with open('denormalization_data.json', 'w', encoding='utf-8') as json_file:
    json_file.write(denormalization_json)

print("Normalized and denormalization JSON files created successfully.")
