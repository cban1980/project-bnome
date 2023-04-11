import json
import paramiko
from gsettings import Settings
import dbus

# Load settings and nodes from a JSON file
with open('settings.json') as f:
    data = json.load(f)

schemas = data['schemas']
nodes = data['nodes']
username = data['username']
password = data['password']

# Iterate over each node and schema and set the specified settings
for node in nodes:
    # Connect to the node via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(node, username=username, password=password)

    # Apply the specified settings for each schema
    bus = dbus.SystemBus()
    proxy = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon')
    for schema in schemas:
        settings = Settings(schema=schema, bus_proxy=proxy)
        for key, value in schemas[schema].items():
            settings.set(key, value)

        print(f"Settings applied for node {node} and schema {schema}")

    ssh.close()

print("All settings applied successfully")