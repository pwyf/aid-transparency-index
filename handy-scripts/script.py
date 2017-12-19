from collections import OrderedDict
import csv
import json
from os.path import exists, join
from os import makedirs
import shutil


def slugify(name):
    return name.replace(' ', '-').replace(',', '').replace('.', '').lower()


# this mapping is totally arbitrary, and just for
# demonstration purposes
mapping = {
    'organisation-planning': 'Organisational planning and commitments',
    'organisation-financial': 'Finance and budgets',
    'activity-basic': 'Project attributes',
    'activity-classifications': 'Joining-up development data',
    'activity-related-documents': 'Finance and budgets',
    'activity-financial': 'Finance and budgets',
    'activity-performance': 'Performance',
    'commitment-': 'Organisational planning and commitments',
}

with open(join('..', '_data', 'source-results.csv')) as f:
    r = csv.DictReader(f)
    results = [x for x in r]

orgs = {slugify(x['organisation_name']): {
    'name': x['organisation_name'].replace('U.S.,', 'US,'),
    'slug': slugify(x['organisation_name']),
    'score': 0.,
    'by_component': OrderedDict(),
} for x in results}

for x in results:
    org = slugify(x['organisation_name'])
    sc = float(x['indicator_total_weighted_points'])
    orgs[org]['score'] += sc
    cat = mapping.get(x['indicator_category_subcategory'].lower())
    if cat not in orgs[org]['by_component']:
        orgs[org]['by_component'][cat] = 0.
    orgs[org]['by_component'][cat] += sc

orgs = OrderedDict(
    sorted(orgs.items(), key=lambda x: x[1]['score'], reverse=True))

for idx, org in enumerate(orgs.values()):
    org['rank'] = idx + 1

with open(join('..', '_data', 'results.json'), 'w') as f:
    json.dump(orgs, f)

with open('agency-template.md') as f:
    agency_tmpl = f.read()

with open('curve-template.md') as f:
    curve_tmpl = f.read()

output_path = join('..', '2016')
agencies_path = join(output_path, 'agencies')
shutil.rmtree(agencies_path, ignore_errors=True)
makedirs(agencies_path)

curves_path = join(output_path, 'curves')
shutil.rmtree(curves_path, ignore_errors=True)
makedirs(curves_path)

for org in orgs.values():
    txt = agency_tmpl.format(**org)
    with open(join(agencies_path, org['slug'] + '.md'), 'w') as f:
        f.write(txt)
    txt = curve_tmpl.format(**org)
    with open(join(curves_path, org['slug'] + '.md'), 'w') as f:
        f.write(txt)
