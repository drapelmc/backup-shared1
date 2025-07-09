import os, requests, time, json
from gdrive import upload_to_drive

with open('config.json') as f:
    config = json.load(f)

headers = {
    "Authorization": f"Bearer {config['ptero_api_key']}",
    "Content-Type": "application/json"
}

for node_id in config["node_ids"]:
    servers = requests.get(f"{config['ptero_url']}/api/application/servers?per_page=500", headers=headers).json()['data']
    for server in servers:
        if server['attributes']['node'] != node_id:
            continue
        sid = server['attributes']['identifier']
        name = server['attributes']['name'].replace(" ", "_")
        print(f"🔄 Backup {name} ({sid})")
        res = requests.post(f"{config['ptero_url']}/api/client/servers/{sid}/backups", headers=headers, json={"name": f"{name}-auto", "locked": False})
        if "uuid" not in res.json(): continue
        uuid = res.json()["uuid"]

        # Polling until complete
        while True:
            stat = requests.get(f"{config['ptero_url']}/api/client/servers/{sid}/backups/{uuid}", headers=headers).json()
            if stat["completed_at"]: break
            time.sleep(10)

        url = stat["url"]
        filename = f"output/{name}.tar.gz"
        with open(filename, "wb") as f:
            f.write(requests.get(url).content)
        print(f"✅ {filename} selesai")

        upload_to_drive(filename, config['gdrive_folder_id'])
