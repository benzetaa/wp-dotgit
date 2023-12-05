import argparse
import requests
from bs4 import BeautifulSoup
import logging,urllib3
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_git_head_existence(url_complete):
    git_head_url = f"{url_complete.rstrip('/')}/.git/HEAD"
    try:
        response = requests.get(git_head_url, verify=False)
        if response.status_code == 200:
            resp = response.text.strip()
            return response.text.strip() == "ref: refs/heads/master", resp
        else:
            return False, None
    except requests.RequestException as e:
        logging.info(f"[{colored('ERROR', 'red')}] Erro ao verificar a existência de {git_head_url}: {e}")
        return False, None

def get_wordpress_theme(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        theme_links = soup.find_all('link', href=lambda x: x and '/wp-content/themes/' in x)
        if theme_links:
            theme_url = theme_links[0]['href']
            theme_name = theme_url.split('/wp-content/themes/')[-1].split('/')[0]
            return theme_name
        else:
            return None
    except requests.RequestException as e:
        return None

def process_url(url):
    theme = get_wordpress_theme(url)
    if theme:
        url_complete = f"{url}/wp-content/themes/{theme}"
        git_head_exists, resp = check_git_head_existence(url_complete)
        if git_head_exists:
            logging.info(f"[{colored('FOUND', 'green')}] {url}/wp-content/themes/{theme}/.git/HEAD [{colored(resp, 'yellow')}]")
        else:
            logging.info(f"[{colored('NOT FOUND', 'red')}] {url}/wp-content/themes/{theme}/.git/HEAD")

def process_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_url, map(str.strip, urls))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='URL to retrieve the WordPress theme.')
    parser.add_argument('-f', '--file', help='Text file containing a list of URLs to process.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")   

    if args.url:
        process_url(args.url)
    elif args.file:
        process_urls_from_file(args.file)
    else:
        logging.info(f"[{colored('ERROR', 'red')}] Please provide a URL using -u or the path to a file using -f.")

if __name__ == "__main__":
    main()
