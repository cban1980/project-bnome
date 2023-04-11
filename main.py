import json
import paramiko
from gsettings import Settings
import dbus
import subprocess

# Load settings and nodes from a JSON file
with open('settings.json') as f:
    data = json.load(f)

schemas = data['schemas']
nodes = data['nodes']
username = data['username']
password = data['password']

# Get a list of all user accounts on the system
users = subprocess.check_output(["cut", "-d", ":", "-f", "1", "/etc/passwd"]).decode("utf-8").split("\n")

# Iterate over each node, user, and schema and set the specified settings
for node in nodes:
    # Connect to the node via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(node, username=username, password=password)

    # Apply the specified settings for each schema and user
    bus = dbus.SystemBus()
    proxy = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon')
    for schema in schemas:
        for user in users:
            # Skip any user accounts that are empty or start with a system prefix
            if user == "" or user.startswith("_") or user.startswith("systemd"):
                continue

            settings = Settings(schema=schema, bus_proxy=proxy, path=f"/org/gnome/settings-daemon/plugins/{schema}/{user}")
            for key, value in schemas[schema].items():
                settings.set(key, value)

            print(f"Settings applied for node {node}, user {user}, and schema {schema}")

    ssh.close()

print("All settings applied successfully")