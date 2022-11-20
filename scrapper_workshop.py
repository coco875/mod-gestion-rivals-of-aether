import pySmartDL
import os
import zipfile
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
import bs4

path_workshop = os.getenv("LOCALAPPDATA")
path_workshop = os.path.join(path_workshop, "RivalsofAether", "workshop")

def download_file(url, path):
    path = os.path.join(os.getcwd(), path)
    obj = pySmartDL.SmartDL(url, path)
    try:
        obj.start()
        return True
    except:
        obj.stop()
        return False

def get_mod(url):
    if not os.path.exists(path_workshop):
        os.makedirs(path_workshop)

    parsed_url = urlparse(url)
    mod_id = parse_qs(parsed_url.query)['id'][0]
    
    if os.path.exists(os.path.join(path_workshop, mod_id)):
        print("Mod already downloaded", mod_id)
        return
    
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, 'html.parser')
        
    game_id = soup.find('a', {"data-panel": '{"noFocusRing":true}'})['href'].split('/')[-1]
    link = f"http://steamworkshop.download/online/steamonline.php"
    html = requests.post(link, data={"item": mod_id, "app": game_id}).text
    if "Free space left" in html:
        print("error during download")
        return
    soup = bs4.BeautifulSoup(html, 'html.parser')
    print(soup)
    try:
        link = soup.find('a')['href']
    except:
        print("error during download")
        return

    download_file(link, f"{mod_id}.zip")

    with zipfile.ZipFile(f"{mod_id}.zip", 'r') as zip_ref:
        zip_ref.extractall(path_workshop)
    os.remove(f"{mod_id}.zip")

def download_page(url):
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            if link['href'].startswith('https://steamcommunity.com/sharedfiles/filedetails/'):
                get_mod(link['href'])

def download_whole_workshop(url):
    for i in range(1, 100):
        download_page(f"{url}&p={i}")

def shearch_mod(query):
    url = f"https://steamcommunity.com/workshop/browse/?appid=383980&searchtext={query}"
    download_whole_workshop(url)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="url of the mod", default=None, nargs='?')
    parser.add_argument("-f", "--file", help="file with urls of the mods")
    args = parser.parse_args()
    if args.file:
        with open(args.file, 'r') as f:
            for line in f.readlines():
                get_mod(line)
    else:
        get_mod(args.url)