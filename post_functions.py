import os
import json
import time
import requests
from loguru import logger
from settings import args
from response_handling import handle_response
from LDT_Addendum import hitlistIM, hitlistCP
global oidcToken


#### POST Functions ###################################################################
### Any and all functions that send a post request live here. Protected or unprotected,
### from any content source, and against any of the available API endpoints.

## Fetch JSON content from GitHub... (V9)
def go_fetch(url):
    logger.opt(colors=True).trace("<dim>Running 'post_functions.go_fetch'...</>")
    if "github.com" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob", "")
    header = {"Accept": "application/vnd.github.v3.raw"} # tell gitHub to send as raw, uncompressed
    bone = requests.get(url, headers=header)
    
    if bone.status_code == 200:
        try:
            jasonBone = json.dumps(json.loads(bone.text), indent=4) # reconstruct as JSON with indentation
            return jasonBone
        except json.JSONDecodeError as e:
            raise Exception("Failed parsing JSON content.")
    else:
        raise Exception(f"Failed to fetch JSON content from GitHub link: {url}")



## Send POST request to unprotected URLs...
def send_post(pfp, fullMessage):
    logger.opt(colors=True).trace("<dim>Running 'post_functions.send_unprotected_post'...</>")
    header = {"Content-Type": "application/json"}
    response = requests.post(pfp, data=fullMessage, headers=header)
    return response



## Send POST request to IAP protected URLs...
def send_iap_post(url, fullMessage, method="POST"):
    logger.opt(colors=True).trace("<dim>Running  'send_iap_post'...</>")
   
    # Check if token valid, refresh expired token if not
    if oidcToken.valid != True:
        request = google.auth.transport.requests.Request()
        oidcToken.refresh(request)

    # Fetch IAP-protected URL, auth header 'Bearer', and OpenID Connect token
    fullMessage=json.loads(fullMessage)
    resp = requests.post(
    url,
    headers={
        "Authorization": "Bearer {}".format(oidcToken.token),
        "Content-Type": "application/json",  # Set content-type to JSON
    },
    json=fullMessage,
    )
    logger.debug(f"bearer Token:\n{oidcToken.token}")
    return resp



## Send POST request (IAP or Unprotected), then handle response...
def post_and_respond(fullMessage, requestID):
    logger.opt(colors=True).trace("<dim>Running 'post_functions.post_and_respond'...</>")
    try:
        if args.target != "cloud":
            response = send_post(args.pfp, fullMessage)

        elif args.target == "cloud":
            response = send_iap_post(args.pfp, fullMessage)
        
        # ALL requests go through handle_response (by design)
        handle_response(response, requestID)
    
    except Exception as e:
        logger.critical(f"{e}")



## Test a knowledgebase repo input message JSON file...
def test_inputfile(mode, inputID, requestID):
    logger.opt(colors=True).trace("<dim>Running 'post_functions.test_inputfile'...</>")
    try:
        if mode == "testIMs":   # Check if testing official persona input messages
            url = f"https://raw.githubusercontent.com/Display-Lab/knowledge-base/main/vignettes/personas/{inputID}/input_message.json"
            logger.info(f"\nTesting input_message file for persona '{inputID.upper()}'")

        elif mode == "testCPs": # Check if testing causal pathway suite input messages
            url = f"https://github.com/Display-Lab/knowledge-base/blob/main/vignettes/dev_templates/causal_pathway_test_suite/{inputID}_cptest.json"
            inputID = inputID.replace("_"," ")  # replace underscores with spaces
            logger.info(f"Testing input_message file for causal pathway '{inputID.upper()}'")
        
        jsonContent = go_fetch(url)     # retrieve github json content
        post_and_respond(jsonContent, requestID)

    except Exception as e:
        logger.critical(f"{e}")



## Automated full repo testing of all knowledgebase files...
def repo_test(mode, threadIndex, testIndex, requestID):
    logger.opt(colors=True).trace("<dim>Running 'post_functions.repo_test'...</>")
    if mode == "testIMs":   # Run when testing persona input messages
        hitlist = hitlistIM
    elif mode == "testCPs": # Run when testing causal pathway input messages
        hitlist = hitlistCP
    
    for requestIndex, inputID in enumerate(hitlist, start=1):
        requestID = f"Thread {threadIndex}, Test {testIndex}, Request {requestIndex}" # add request index to ID
        args.CP = inputID     # Sneaky way to set current causal pathway from hitlist for verification
        test_inputfile(mode, inputID, requestID)



## Send local input_message files by user spec...
def send_locals(numberToSend, folderPath, requestID):
    logger.opt(colors=True).trace("<dim>Running 'post_functions.send_locals'...</>")
    request_count = 0
    # Input message local files must be valid JSON files
    existing_files = [f for f in os.listdir(folderPath) if f.endswith(".json")]

    # Sort existing files numerically
    existing_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))

    # Take the desired number of files
    files_to_send = existing_files[:args.sendLocals]

    for file_name in files_to_send:
        request_count += 1
        if request_count % 6 == 0 and args.target == 'cloud':
            logger.info(f'Throttling requests for 30 seconds...')
            time.sleep(30)
        
        logger.debug(f'Attempting file: {file_name}')
        file_path = os.path.join(folderPath, file_name)
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                json_str = json.dumps(json_data, indent=2)  # Serialize with proper formatting
                post_and_respond(json_str, requestID)       # Send and respond to post request
        
        # Error catchers for debugging errors
        except json.decoder.JSONDecodeError as e:
            logger.warning(f"JSON decoding error in {file_name}: {e}")
        except Exception as e:
            logger.warning(f"Error reading {file_name}: {e}")
