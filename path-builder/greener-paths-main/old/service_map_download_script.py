import requests
import json

def download_services():
    # Download all the services
    print("Downloading list of services...")
    url = "https://api.hel.fi/servicemap/v2/service/"
    data = {'intial_url': url,
            'description':"List of all services in the service map api", 
            'data':[]}

    while True:
        resp = requests.get(url)
        resp.raise_for_status()
        resp = resp.json()

        url = resp['next']
        data['data'].extend(resp['results'])
        if not url:
            break

    print("Finished!")

    with open('all_services.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)

def download_units(service_id=None, filename='all_units.json', verbose=True):
    # Download all the services
    print("Downloading list of units...")
    url = "https://api.hel.fi/servicemap/v2/unit/"
    params = {}
    if service_id:
        params['service'] = service_id

    data = {'intial_url': url,
            'description':"List of all services in the service map api", 
            'data':[]}
    i = 0
    while True:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        resp = resp.json()

        url = resp['next']
        data['data'].extend(resp['results'])

        if verbose & (i % 5 == 0):
            print(f"Downloaded page {i}") 

        if not url:
            break
        i += 1

    print("Finished!")

    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__=="__main__":
    # download_units()
    pass