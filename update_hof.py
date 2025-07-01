from time import sleep
import requests
import re
import base64



TOKEN = ''
SLEEP=1.5
HEADERS = {
    'Authorization': 'Bearer ' + TOKEN,
    'Content-Type': 'application/json'
}

def get_other_titles(repo_link):
    repo_link = repo_link.split('/')
    owner = repo_link[3]
    repo = repo_link[4]

    url = f'https://api.github.com/repos/{owner}/{repo}/contents/README.md'
    response = requests.get(url, headers=HEADERS)
    aliases = []

    response = response.json()

    if "content" not in response:
        return aliases

    response = base64.b64decode(response["content"]).decode('utf-8').splitlines()

    aliases = []
    blacklist = ["tema", "surse", "fonts", "assets", "sources", "Description", "How to Play",
                 "Instrucțiuni de compilare", "OOP Template", "Proiect POO", "OOP-Project", "OOP-Template",
                 "Nu primesc notă pentru că nu am pus titlu și descriere",
                 "instru"]

    for line in response:
        alias = None
        if line.startswith('# '):
            alias = line[2:]
        elif line.startswith('## '):
            alias = line[3:]

        skip = False
        if alias is not None and alias not in aliases:
            for banned_word in blacklist:
                if banned_word.lower() in line.lower():
                    skip = True
                    break
            if skip:
                continue
            aliases.append(alias)

    return aliases


with open('./HoF.md', encoding='utf-8') as f:
    hof = f.read()

print('Finished reading HoF.md')

document_lines = []

for line in hof.split('\n'):
    match = re.search(r'https://github.com/[^\s\)\]]+', line)
    is_available = True

    if match:
        repo_link = match.group(0)
        line = line.rstrip('?| ')

        print(f'============== {repo_link} ===============')

        try:
            response = requests.get(repo_link, allow_redirects=True, timeout=15)

            if response.status_code != 200:
                print(f'{line} is not available.')

                if '~' not in line: # daca nu a fost deja taiat
                    line = '~' + line + '~'
            else:
                if response.url != repo_link:
                    print(f"Repo-ul {repo_link} a fost mutat la {response.url}")
                    line = line.replace(repo_link, response.url)
                print(f'{line} is available.')

                available_titles = get_other_titles(repo_link)
                print('Available titles: ', end='')
                for alias in available_titles:
                    print(f'{alias} | ', end='')
                print('')

            line = line + ' | '

        except Exception as e:
            print(f'Eroare la repo-ul {repo_link}')
            print(e.with_traceback())
        sleep(SLEEP)

        print('=======================================\n')

    document_lines.append(line)

with open('./HoF.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(document_lines))
