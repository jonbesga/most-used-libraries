from collections import defaultdict


def remove_forks(repos):
    return list(filter(lambda repo: repo['fork'] == False, repos))


def get_repos(s, user):
    # TODO: Pagination
    r = s.get(f"https://api.github.com/users/{user}/repos?sort=updated&type=owner&per_page=30")
    return r.json()


def get_content_repo(s, user, name):
    r = s.get(f"https://api.github.com/repos/{user}/{name}/contents/")
    return r.json()


def read_file(s, url):
    r = s.get(url)
    return r.text


def get_packages_requirements(text):
    found_packages = []
    for line in text.split('\n'):
        if line.startswith('#') or line == '':
            continue
        line = line.replace('>=', '==').replace('<=', '==')
        found_packages.append(line.split('==')[0])
    return found_packages


def get_packages_packages_json(text):
    reading_packages = False
    found_packages = []
    for line in text.split('\n'):
        if "dependencies" in line or 'devDependencies' in line:
            reading_packages = True
            continue
        elif reading_packages and '}' in line:
            reading_packages = False
            continue

        if reading_packages:
            found_packages.append(line.split(':')[0].strip().replace("\"", ""))
    return found_packages


def get_packages_pipfile(text):
    reading_packages = False
    found_packages = []
    for line in text.split('\n'):
        if line == '[packages]':
            reading_packages = True
            continue
        elif reading_packages and line == '':
            reading_packages = False
            continue

        if reading_packages:
            found_packages.append(line.split(' = ')[0].replace("\"", ""))
    return found_packages


LOOKUP_FILES = {
    'package.json': {'f': get_packages_packages_json, 'type': 'javascript'},
    'Pipfile': {'f': get_packages_pipfile, 'type': 'python'},
    'requirements.txt': {'f': get_packages_requirements, 'type': 'python'},
}


def get_most_used_libraries(s):
    TOTAL_LIBRARIES = {
        'python': defaultdict(int),
        'javascript': defaultdict(int)
    }
    response = s.get('https://api.github.com/user')
    response = response.json()
    user = response['login']
    repos = get_repos(s, user)
    repos = remove_forks(repos)

    for repo in repos:
        contents = get_content_repo(s, user, repo['name'])

        for content in contents:
            if content['name'] in LOOKUP_FILES:
                text = read_file(s, content['download_url'])
                packages = LOOKUP_FILES[content['name']]['f'](text)
                for package in packages:
                    language = LOOKUP_FILES[content['name']]['type']
                    TOTAL_LIBRARIES[language][package] += 1
    return TOTAL_LIBRARIES
