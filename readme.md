
# Welcome to the Leakdown Tester Repository!
This repository contains the codebase for the Leakdown Tester (LDT) command line tool, which enables leveraging the extensive work done by the Display-lab team in the [Knowledge-base](https://github.com/Display-Lab/knowledge-base/) against APIs. 

The script is named after a protocol for testing engine blocks, the reverse of a compression test. Pressurized air is introduced to the engine block to check for leaking points - it's a metaphor for how this tool can send large volumes of data to APIs to test for 'leaks'!

As of current date, the tool is focused around testing the [Precision Feedback Pipeline](https://github.com/Display-Lab/precision-feedback-pipeline) repo
 API, but more APIs can be configured as targets in future releases.

Continue reading for details on making use of LDT to test APIs.

# Leakdown Tester User Manual
Here are listed the currently implemented user commands, environmental variables, and instructions for use.

## Arguments
Below are the arguments that can be used to run LDT. Initializing with all default values will yield a single post request from CSV file sent to a locally hosted API instance.

---
Format for the below argument specifications:

`--argument` `datatype`
- Default value of `datatype`
- Details about the argument
---
### General Test Config Arguments
`--target` `string` 
- Default: local 
- Sets the API endpoint for the POST requests. Accepts strings 'local, heroku, cloud'.

`--tests` `integer`
- Default: 1
- Number of tests run by the script (per thread).
   + Identical to the number of requests you want the API to recieve, unless multithreading or using a full-repo test.
`--threads` `integer` 
- Default: 1
- Number of threads to run concurrent Leakdown Tests on against the same PFP API endpoint.

`--respond`
- Default: None
- A 'SetTrue' argument; Adding to your initialization will set to `True`
- Logs a useful subset of the API's successful response(s).

`--saveResponse`
- Default: None
- SetTrue; Saves the entire API response(s) to text file(s).

`--debug`
- Default: None
- SetTrue; Shows debug-focused console log.

`--saveDebug` 
- Default: None
- SetTrue: Writes LDT logs to text file. 
   + Without debug enabled, will only save INFO level logging statements (normal output, essentially).

### Behavior-setting arguments
`--postwoman`
- Default: None
- SetTrue: Sends performance data JSON payload from addendum file.
   + Name references the Postman API which is a solid API testing standalone service with extensive features. The major advantage for PFP testing is the ability to rapidly configure and test individual POST requests, which postwoman can also accomplish with the proper IDE setup.
`--useGit` `string`
- Default: None
- Connects to an input message source at GitHub.com to send the target API.
- Use a string argument with a github URL in quotes.

`--persona` `string`
- Default: None
- String choices are "alice", "bob", "chikondi", "deepa", "eugene", "fahad", "gaile". Quotes are optional.
- Selects a persona's input_message.json file to send the API as JSON content for a POST request.

`--allPersonas`
- Default: None
- SetTrue: Sends all knowledgebase persona input message files as JSON content for POST requests to the target API.

`--CP` `string`
- Default: None
- String choices are "goal_approach", "goal_gain", "goal_loss", "improving", "social_approach", "social_better", "social_gain", "social_loss", "social_worse","worsening", and "all".
- Selects a causal-pathway-based input message JSON file to send the target API for testing.

`--allCPs`
- Default: None
- SetTrue: Tests all causal-pathway-specific input message files, excepting `all_cptest.json`.

### Output Verification and Validation arguments
Note: V&V options are mutually exclusive, only one kind of operation can be performed during an LDT run.

`--vignVerify`
- Default: None 
- SetTrue: Compares output message keys 'measure' and 'acceptable_by' against vignette-validated key pair dictionary.

`--cpVerify`
- Default: None 
- SetTrue: Compares user-input and API-output message keys 'measure' and 'acceptable_by' pairs for a match.

### CSV mode-specific payload config arguments
Options for configuring the JSON payload pulled from a user-specified CSV file.

`--RI` `integer`
- Default: 0
- Specifies the first row of data to read from CSV file (0 indexed).

`--RF` `integer`
- Default: 12
- Specifies the last row of data to read from CSV file (0 indexed).

`--C`, `integer`
- Default: 10
- Specifies the number of columns to read from CSV file.

### Required file pathing arguments
`--csv` `string`
- Default: None
- Enter the filepath to the CSV file used to read from for JSON payload information.
- When specified, overwrites 'CSVPATH' environmental variable.

`--servAcc` `string`
- Default: None
- Enter the filepath to the Service Account file used to read from for OAuth2.0 authenticating POST requests to IAP-protected APIs.
- When specified, overwrites 'SAPATH' environmental variable.

## Environmental Variables
1) `CSVPATH` - Filepath to a local CSV file.
- The script checks for this on startup, as JSON content to send as a POST request is currently required. You can specify this filepath with the csv argument, or you can set the env var and specify a different filepath with the csv argument which will override the environment variable. A filepath must be specified if not using the `useGit` argument.

2) `PFP` - URL of the PFP API endpoint where the POST requests are sent.
- It is likely faster to use the `--target` argument to set the API endpoint rather than to set the environment variable here, however both methods are implemented. Use what works for you.

3) `TARGET_AUDIENCE` - Variable which contains the "target audience" part of the authentication process for connecting with the GCP PFP API. 

4) `SAPATH` - Variable that sets path to your own Service Account JSON file for use in authorizing POSTs to the GCP PFP instance.
