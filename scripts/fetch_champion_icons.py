import os
import requests
import json
from bs4 import BeautifulSoup

def parse_icon_file_names(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all the <a> tags within the table body
    table = soup.find('table', id='list')
    file_names = []
    if table:
        links = table.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif'):
                file_names.append(href)
    
    return file_names

# Directory to save the champion icons
save_dir = "champion_icons"
os.makedirs(save_dir, exist_ok=True)

# Base URLs
base_icon_url = "https://raw.communitydragon.org/latest/game/assets/characters/{id}/hud/{id}_circle_0.png"
base_icon_folder_url = "https://raw.communitydragon.org/latest/game/assets/characters/{id}/hud/"
base_icon_url_alt = "https://raw.communitydragon.org/latest/game/assets/characters/{id}/hud/{id}_circle.png"
base_icon_url_alt_2 = "https://raw.communitydragon.org/latest/game/assets/characters/{id}/hud/{id}_circle_1.png"

existing_icons = os.listdir(save_dir)
existing_icon_ids = [icon.split(".")[0] for icon in existing_icons]

champion_aliases = []
with open("denormalization_data.json", "r") as f:
    denormalization_data = json.load(f)
    for alias, id in denormalization_data["champion_mapping"].items():
        champion_aliases.append((alias, id))


failed = []
# Loop through champion IDs (1-999 is an example range; adjust as needed)
for alias, champion_id in champion_aliases:   
    alias = alias.lower()
    if (alias == ''):
        # Add failed id to a file
        print(f"Failed to get alias for champion ID {champion_id}")
        continue
    # Check if the icon already exists
    if f"{alias}.png" in existing_icons:
        print(f"Icon for champion ID {champion_id} already exists.")
        continue

    # Construct the URL for the champion icon
    icon_url = base_icon_url.format(id=alias)
    icon_url_alt = base_icon_url_alt.format(id=alias)
    icon_url_alt_2 = base_icon_url_alt_2.format(id=alias)
    
    # Download the icon
    icon_response = requests.get(icon_url)
    icon_response_alt = requests.get(icon_url_alt)
    icon_response_alt_2 = requests.get(icon_url_alt)
    icon_folder = requests.get(base_icon_folder_url.format(id=alias))
    icon_names = parse_icon_file_names(icon_folder.content)
    icon_names.sort()
    # Get the file name that ends wirth square.png
    icons_square = [icon for icon in icon_names if icon.endswith("square.png")]
    icon_from_square_name = icons_square[0].replace("square.png", "circle.png") if icons_square else None
    icon_from_square = requests.get(base_icon_folder_url.format(id=alias) + icon_from_square_name) if icon_from_square_name else None
    # Get the first alphabetical result from the folder
    first_icon_name = icon_names[0] if icon_names else None
    first_icon = requests.get(base_icon_folder_url.format(id=alias) + first_icon_name) if first_icon_name else None
    
    # Select the first of these icons that is available
    icons_to_use = [
        icon_response,
        icon_response_alt,
        icon_response_alt_2,
        icon_from_square,
        first_icon
    ]
    first_valid_icon = next((icon for icon in icons_to_use if icon and icon.status_code == 200), None)
    if first_valid_icon:
        # Save the icon image to the directory
        with open(os.path.join(save_dir, f"{alias}.png"), "wb") as f:
            content = first_valid_icon.content
            succesful_url = first_valid_icon.url
            f.write(content)
        print(f"Successfully downloaded icon for champion ID {champion_id} with url {succesful_url}")
        # Write succesful url into a file
        with open("succesful_urls.txt", "a") as f:
            f.write(f"{succesful_url}\n")
    else:
        print(f"Failed to download icon for champion ID {champion_id} with url {icon_url}")
        # Add failed alias to a file
        with open("failed_alias.txt", "a") as f:
            f.write(f"{alias}\n")