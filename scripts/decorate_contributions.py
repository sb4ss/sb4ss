"""Label snk's weekly grid with real calendar months; preserve its animation."""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
MONTHS = ('Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic')


def calendar_weeks():
    query = '''query($login:String!){user(login:$login){contributionsCollection{
      contributionCalendar{weeks{contributionDays{date contributionCount}}}
    }}}'''
    request = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': {'login': os.environ['GITHUB_PROFILE']}}).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                 'User-Agent': 'sb4ss-profile', 'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get('errors'):
        raise RuntimeError('GitHub could not return the contribution calendar')
    return payload['data']['user']['contributionsCollection']['contributionCalendar']['weeks']


def decorate(path, weeks):
    tree = ET.parse(path)
    root = tree.getroot()
    cells = [r for r in root.findall(f'.//{{{NS}}}rect') if 'c' in r.get('class', '').split()]
    if not cells:
        raise ValueError('No contribution cells found in snake SVG')
    columns = sorted({float(r.get('x', '0')) for r in cells})
    if len(columns) != len(weeks):
        raise ValueError('Calendar weeks do not match the generated snake grid')
    text_color = '#AFC5D8' if 'dark' in path.name else '#536779'
    # Snake SVG reserves 32px above the grid; place labels in that space.
    labels = ET.SubElement(root, f'{{{NS}}}g', {
        'fill': text_color, 'font-family': 'system-ui, -apple-system, Segoe UI, sans-serif',
        'font-size': '11', 'aria-label': 'Meses del calendario de contribuciones',
    })
    previous_month = None
    previous_x = -100
    for x, week in zip(columns, weeks):
        days = week['contributionDays']
        date = dt.date.fromisoformat(days[0]['date'])
        # A month starts in the week containing its first day, not the next week.
        first_of_month = next((dt.date.fromisoformat(d['date']) for d in days
                               if d['date'].endswith('-01')), None)
        month = first_of_month.month if first_of_month else date.month
        if month != previous_month:
            if x - previous_x >= 40 and columns[-1] - x >= 32:
                text = ET.SubElement(labels, f'{{{NS}}}text', {'x': str(x), 'y': '-17'})
                text.text = MONTHS[month - 1]
                previous_x = x
            previous_month = month
    total = sum(d['contributionCount'] for w in weeks for d in w['contributionDays'])
    title = ET.Element(f'{{{NS}}}title')
    title.text = f"{os.environ['GITHUB_PROFILE']}: {total} contribuciones en los últimos 12 meses"
    root.insert(0, title)
    root.set('role', 'img')
    root.set('aria-label', title.text)
    # Keep each cell's initial (real activity) color when motion is disabled.
    style = ET.SubElement(root, f'{{{NS}}}style')
    style.text = '@media(prefers-reduced-motion:reduce){*{animation:none!important}.s{display:none}}'
    tree.write(path, encoding='utf-8', xml_declaration=False)
    print(f'Updated {path.name}: {len(columns)} weeks, {total} contributions')


if __name__ == '__main__':
    weeks = calendar_weeks()
    for name in ('contributions-light.svg', 'contributions-dark.svg'):
        decorate(Path('assets') / name, weeks)
