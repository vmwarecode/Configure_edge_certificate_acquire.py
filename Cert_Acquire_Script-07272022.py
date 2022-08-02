import time
import os
import logging
import requests
from requests.structures import CaseInsensitiveDict

# global vars
vco_url = ""
vco_token = ""
#logging
logging.basicConfig(filename="script_run.log",
					format='%(asctime)s %(message)s',
					filemode='a')
logger=logging.getLogger("urllib3")
logger.setLevel(logging.WARNING)



def get_edges():
    headers = CaseInsensitiveDict()
    headers["Authorization"] = vco_token
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = '{"id":0,"jsonrpc":"2.0","method":"enterprise/getEnterpriseEdges","params":{"edgeId": 0, "with": []}}'
    resp = requests.post(vco_url, headers=headers, data=data)
    res = resp.json()
    return res["result"]



def api_save_certificate(edge_id,count,edge_name):
    headers = CaseInsensitiveDict()
    headers["Authorization"] = vco_token
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = (
        '{"jsonrpc":"2.0","method":"edge/updateEdgeAttributes",'
        '"params":{"id":%s,"_update":{"endpointPkiMode":"CERTIFICATE_OPTIONAL"}},"id":%s}'
        % (edge_id,count)
    )
    resp = requests.post(vco_url, headers=headers, data=data)
    if resp.status_code == 200:
        logger.warning(f'finished setting certificate for edge {edge_name}')
        return True
    else:
        logger.warning(f'failed setting certificate for edge {edge_name} reason {str(resp.status_code)} , {resp.reason}')
        return False

def set_certificate():
    edges = get_edges()
    build_input=input("Please write build number ex. R341-20220628-DEV-67bbd74b49")
    count = 0
    successful_counter = 0
    for edge in edges:
        if edge["edgeState"]!="CONNECTED":
            continue
        if edge["buildNumber"]!=build_input:
            continue
        if edge["endpointPkiMode"]=="CERTIFICATE_OPTIONAL":
            continue
        edge_id = edge["id"]
        count += 1
        if api_save_certificate(edge_id,count,edge["name"]):
            successful_counter += 1
        time.sleep(1)
    logger.warning(f'Number of edges configured = {successful_counter}')


def validate_certifcate():
    edges = get_edges()
    c=0
    for edge in edges:
        if edge["endpointPkiMode"] != "CERTIFICATE_OPTIONAL":
            c+=1
    logger.warning(f'pending certificate acquire total = {c}')

def main():
    """
    Input variables
    vco_url = orchestrator url ex. "vco58-usvi1.velocloud.net"
    vco_token = user's token to run this script
    """
    hostname = os.getenv("vco_hostname")
    token = os.getenv("vco_token")
    if hostname is None:
        hostname = input("Please write vco hostname. ex. vco58-usvi1.velocloud.net")
    if token is None:
        token = input("Please paste vco token")
    global vco_token
    vco_token = f"Token {token}"
    global vco_url
    vco_url = f"https://{hostname}/portal/"
    validate_certifcate()
    set_certificate()
    print("end")
    logger.warning(f'script finished')


if __name__ == "__main__":
    main()
