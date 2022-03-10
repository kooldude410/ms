import yaml

with open(r'app_conf.yml') as file:
    APPCONF = yaml.load(file, Loader=yaml.FullLoader)
print(APPCONF['datastore']['user'])