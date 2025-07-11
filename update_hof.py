from time import sleep
import requests
import re
import base64
from datetime import datetime


TOKEN = ''
SLEEP=1.5
HEADERS = {
    'Authorization': 'Bearer ' + TOKEN,
    'Content-Type': 'application/json'
}
CURRENT_YEAR = str(datetime.now().year)

def get_other_titles(response):
    aliases = []

    if "content" not in response:
        return aliases

    content_lines = base64.b64decode(response["content"]).decode('utf-8').splitlines()

    blacklist = [
        "tema", "surse",  #(re)surse
        "fonts", "assets", "sources", # (re)sources
        "Description", "How to Play",
        "Instrucțiuni de compilare", "OOP Template", "Proiect POO", "OOP-Project", "OOP-Template",
        "Nu primesc notă pentru că nu am pus titlu și descriere",
        "instru" # (instru)ctiuni / (instru)ctions
        "Prerequisites", "API", "Download", "Important", "Update",
        "OOP_Project", "Usage", "Document", #Document(are)/(tation)
        "Known issues", "Tasklist", "Basic Functionality", "Qubits", "Classic Bits", "Quantum Gates", "Quantum Circuits",
        "Probability Engine", "Visualisation", "Overview", "Guide", "Requirement", #Requirement(s)
        "Getting started", "About", "Getting it to run", "Install", "run", "Licence", "License", "Feature",
        "requirments", "texture", "libraries", "descriere", "pisicile", "utilizare"
    ]

    for line in content_lines:
        match = re.match(r'^#{1,2} (.+)', line)
        if match:
            alias = match.group(1).strip()
            if alias not in aliases:
                if any(banned.lower() in alias.lower() for banned in blacklist):
                    continue
                aliases.append(alias)

    return aliases

def get_README(url, readme='README.md'):
    url = url + f"/contents/{readme}"
    response = requests.get(url, allow_redirects=True, timeout=15, headers=HEADERS)
    response = response.json()

    if 'message' in response and response['message'] == 'Not Found':  # Nu a fost gasit `README.md` / `readme.md` in repo
        return -1

    return response

with open('./HoF.md', encoding='utf-8') as f:
    hof = f.read()

print('Finished reading HoF.md')

document_lines = []
is_current_year = False

for line in hof.split('\n'):
    match = re.search(r'https://github.com/[^\s\)\]]+', line)

    is_available = True

    line_year_match = re.search(r'\*\*(\d{4})-\d{4}\*\*', line)
    if line_year_match and line_year_match.group(1) == CURRENT_YEAR and is_current_year == False:
        is_current_year = True

    if match:
        repo_link = match.group(0)
        repo_handle = re.match(r'https://github\.com/([^/]+/[^/]+)', repo_link).group(1)
        line = line.rstrip('?| ')

        project_name = re.search(r'\[([^\]]+)\]', line)
        if project_name:
            project_name = project_name.group(1)

        try:
            response_readme_available = get_README(f"https://api.github.com/repos/{repo_handle}")

            if response_readme_available == -1:
                response_readme_available = get_README(f"https://api.github.com/repos/{repo_handle}", readme="readme.md")

            if response_readme_available == -1: # Nu a fost gasit `README.md` / `readme.md` in repo

                # mai fac un request pentru a verifica daca repo-ul exista
                response_repo_available = requests.get(f"https://api.github.com/repos/{repo_handle}",
                                        allow_redirects=True,
                                        timeout=15,
                                        headers=HEADERS)

                print(f'\n============== {repo_link} ===============')
                if response_repo_available.status_code != 200: # repo-ul nu exista
                    print(f'{line} is not available.')

                    if '~' not in line: # daca nu a fost deja taiat
                        line = '~' + line + '~ (dead link)'
                else: # repo-ul exista, dar nu are readme
                    print('README.md not found')
                print('=======================================\n')
            else:
                html_url = response_readme_available['html_url']
                html_url = re.sub(r'/blob/[^/]+/README\.md$', '', html_url, flags=re.IGNORECASE)

                if repo_link != html_url:
                    print(f"\nRepo-ul {repo_link} a fost mutat la {html_url}")
                    line = line.replace(repo_link, html_url)

                #print(f'{line} is available.')
                print('.', end='', flush=True)

                available_titles = get_other_titles(response_readme_available)
                print_titles = True

                if len(available_titles) == 0:
                    print_titles = False

                for title in available_titles:
                    if project_name.lower() in title.lower():
                        print_titles = False
                        break

                if print_titles:
                    print(f'\n============== {repo_link} ===============')
                    print('Available titles: ', end='')
                    print(*available_titles, sep=" | ", end='')
                    print('')
                    print('=======================================\n')

            line = line + ' | '

        except Exception as e:
            print(f'\nEroare la repo-ul {repo_link}')
            print(e.with_traceback())

        sleep(SLEEP)

    line = line.strip(' ')
    if line == '':
        if document_lines[-1] != '':
            if is_current_year == False:
                document_lines[-1] = document_lines[-1].rstrip('|')
            else:
                document_lines[-1] = document_lines[-1] + ' ?'
                is_current_year = False

    document_lines.append(line)

for i in range(len(document_lines)):
    document_lines[i] = document_lines[i].strip(' ')

with open('./HoF.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(document_lines))
