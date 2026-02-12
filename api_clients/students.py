import requests

from config import BASE_API_URL, API_KEY


def get_serial():
    cpu_serial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpu_serial = line[10:26]
        f.close()
    except:
        cpu_serial = "ERROR"
    return cpu_serial

headers = {
    "X-Device-Id": get_serial(),
    "Authorization": f"Bearer {API_KEY}",
}

def fetch_active_entry(card_id: int):
    return requests.get(BASE_API_URL + "reader/active-entry", json={"mifareNumber": str(card_id)}, headers=headers)

def add_entry(ist_id: str, workstation_id: int):
    return requests.post(BASE_API_URL + "reader/add-entry", json={"istId": ist_id, "workstationId": workstation_id},
                         headers=headers)

def close_entry(entry_id: int):
    return requests.put(BASE_API_URL + "reader/close-entry/" + str(entry_id), headers=headers)
