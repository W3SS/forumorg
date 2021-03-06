import csv
import os

from app import app, get_db
from flask_assets import ManageAssets
from flask_script import Manager
from pymongo import MongoClient

client = MongoClient(host=os.environ.get('MONGODB_URI'))
db = client.get_default_database()


manager = Manager(app)
manager.add_command('assets', ManageAssets())


@manager.command
def fix_dates():
    from datetime import datetime
    cur = get_db().users.find({}, {'_id': 1, 'registered_on': 1, 'confirmed_on': 1})
    for c in cur:
        if type(c['registered_on']) == str:
            print(f'original: {c["registered_on"]}')
            new_d = datetime.strptime(c['registered_on'], '%a, %d %b %Y %H:%M:%S %Z')
            get_db().users.update_one({'_id': c['_id']}, {'$set': {'registered_on': new_d}})
            print(f'fixed: {new_d}')
        if type(c['confirmed_on']) == str:
            print(f'original: {c["confirmed_on"]}')
            new_d = datetime.strptime(c['confirmed_on'], '%a, %d %b %Y %H:%M:%S %Z')
            get_db().users.update_one({'_id': c['_id']}, {'$set': {'confirmed_on': new_d}})
            print(f'fixed: {new_d}')


@manager.command
def drop_schools_():
    cur = get_db().users.find({'profile.school_': {'$exists': True}}, {'_id': 0, 'profile.school_': 1})
    for c in cur:
        print(c)


@manager.command
def complete_companies():
    path = os.path.join(os.path.dirname(__file__), 'data/new_companies.csv')
    reader = csv.DictReader(open(path, 'rb'))
    for row in reader:
        get_db().companies.update_one({'id': row['id_entreprise']}, {'$set': {'info': row}})
        get_db().companies.update_one({'id': row['id_entreprise']}, {'$unset': {'info.id_entreprise': 1}})


@manager.command
def create_transport():
    get_db().users.update_many({}, {'$set': {'events.fra.transports': []}})


if __name__ == '__main__':
    manager.run()
