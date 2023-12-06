# Leakdown Tester Changelog  
## Version 1.3.0
*Released TBD*
**Added:** Regression test examples for implementation with pytest

**Added:** Detailed summary report for multi-message debug of PFP API
- Use --report to generate a summary of measures, templates, and causal pathways which were used in feedback generation
  
**Added** Function to send local input_messages from a file directory  
- access with --sendLocals X where X is the number of files to send from the directory ('Local_inputs')  
- supports arbitrarily named JSON files, designed for use with MPOG data flows but supports any valid JSON  

**Changed:** Logging strategy from default logger to loguru
- Allows colorization, easier formatting of logging for debug review and log output
- Added in-line colorations of API key responses when using --respond

**Changed:** Refactored settings, post functions, and response handling to modules
- No functional changes to user workflow

**Changed:** Log level argument setting
- Deprecated using --debug; now use --loglvl (options: info, debug, trace)

## Version 1.2.0
*Released 11/8/23*
**Changed:** Autoverification minor tweaks to handle the new output formatting after pictoralist rework (--vignVerify)  
**Added:** --pilotVerify to verify tests with the restricted pilot launch dataset  
- added pilotPairs dict to store pairs of causal pathways and measures (tweaks likely needed)
- added documentation

## Version 1.1.2
*Released 10/17/23*
**Improvement:** Updated CSV infrastructure for easier use to support MPOG data flow testing
- Added argument "useCSV" to mandate pipeline use data from a CSV file (previously only used in-lieu of other sources)
- Made change to CSV reading function(s) "csv_jsoner"
	- Added argument for user to specify 0 indexed first column (bypass need to process group number column)
- Changed argument "C", split to args "CI" and "CF"
	- Allows user to specify the correct range of data to read in from CSV more accurately

## Version 1.1.1
*Released 10/17/23*
**Improvement:** Add dotenv support for environmental variable declaration

**Improvement:** Changed format of debug logging statements for better readability

**Improvement:** Created custom visual assets, implemented icon files where possible/stable

**Improvement:** Visual improvements 
- Changed widgets from using basic tk to ttk versions
- Rewrote button, optionmenu, label, and spinbox widgets to use theme inclusive TTK package
- Rewrote packing of all widgets throughout codebase to make more visually appealing
	- May consider grid system instead of packing if further visual elements are needed/required
- Implemented styles in labels and buttons

**Patch:** Repaired GCP authentication functionality
- Verified that bearer token generates and is valid
- Added bearer token readback (debug mode only) when IAP request sent 

**Patch:** Target-setting dropdown in GUI now functions as intended


## Version 1.1.0
*Released 9/7/23*

**Feature:** Added graphical user interface (tkinter build)
- Can be run by initializing LDT_GUI.py
- Core functions tested operational

## Version 1.0.1
*Released 9/6/23*

**Patch:** Fixed V&V functions with new structure of 'acceptable_by' key
- Restored causal pathway verification with `--cpVerify`
	- Iterates through acceptable_by pathways and searches for a match

- Restored vignette verification with `--vignVerify`
	- Searches for matches in message template keys, which correlate 1:1 to causal pathways
	- Searches for matches in measures chosen to create feedback from

- *Planned:* Verify selected measures by comparing message templates
	- Currently unnecessary, but may add functionality for further refinement of testing in the future

**Improvement:** *(Documentation only)* Retroactively changed version numbers from V1 to V0 for pre-release versions
- Updated in GitHub
- Changelog updated

## Version 1.0.0
*Released 8/31/2023*

 **Versioned:** All releases > 0.6.0 will 'live' in a new, independent repository
- Repo is at [Display-lab/Leakdown-Tester](https://github.com/Display-Lab/Leakdown-Tester)
- Liscensed with GNU General Public Liscense 3.0 (share-alike)
- Earlier versions can be found in the caches of the [precision-feedback-pipeline](https://github.com/Display-Lab/precision-feedback-pipeline) repo

 **Feature:** Added more comprehensive logging support with 'logging' module
- Use with arg `--debug` and  `--saveDebug`
- Allows extensive debug logging, shows function flow step-by-step for debug and dev
- Can save LDT output logs for review/sharing
- Configured to not impact normal outputs

 **Feature:** Added postwoman function
- Allows editing addendum file to send custom performance data from script without impacting context, footer, GitHub, or CSV.
- Named after Postman; replicates strengths of using Postman API, but telemetry free and in LDT

 **Improvement:** Implemented argument groups
- Handles user errors relative to setting multiple test behaviors or V&V operations

 **Improvement:** Restructured argument namespace setup code
- Args now organized by function

 **Improvement:** Removed redundant local variable assignments from arg namespace
- Directly reading from args namespace removes extraneous code lines
- Removes neccessity of global-scoping local vars

 **Improvement:** Added option "all" to argument --pathway
- Connects to newest test case which contains 4 months of all ten pathway's datasets

## Version 0.6.0
*Released 8/30/23*

**Feature:** Added ability to test 'causal pathway test suite' input files
- Added arg `--allCPs`
	- Tests all causal-pathway-specific input messages
- Added arg `--useCPath`
	- Causal pathway equivalent of `--usePers`
	- See readme, accepts lowercase name of causal pathway (with underscores)	
- Added modality to test_persona(), restructured to support this
	- Added "mode" variable argument, sets URL for github content retrieval
	- Restructured to handle multiple URL paths based on new "mode" variable
- Renamed `--repoTest` to `--allPersonas`
	- Reflects function better than old name
- Renamed numerous arguments to more accurately reflect function, no user changes
- Changed active print statements to de-clutter console when running LDT

 **Improvement:** refactored versioning, 'hitlists' to addendum file
+ Increases cohesion of main script file
+ Allows all files to update on GitHub when new versions are released
+ Moves long/cluttered dicts to addendum file out of sight

 **Improvement:** reworked `--vignVal` (formerly --validate)
- Reformatted prints to print valid pairs of maeasures and causal pathways, then the measure/CP pair returned by the PFP API
	- Drastically improved usefulness of script's console statements when sharing bug reports

## Version 0.5.0
*Released 8/19/23*

Added multithreading capability to the script
+ Use `--threads X` to start multiple threads to run requests simultaneously against the pipeline.
+ Changed request naming convention, allow save_resp to work properly
+ Many structural changes to support multithreading

Renamed `send_req` and `send_iap_req` to `..._post`
+ Renamed to more precisely describe their functions

Added function `post_and_respond`
+ Refactored the logic for determining which kind of post request to send based on target to this function
+ Included call to handle_response here so that responses can still be logged, printed, or validated against vignette values

## Version 0.4.3
*Released 8/18/23*

 Updated handle_response() function
+ Refactored code to check first for 200 status code response, THEN to pull JSON keys for vignette verification
+ Allows for increased description of bad API responses
+ Refactoring into handle_response eliminates 8 lines of code from script

 Updated test_persona() function
+ Allow function to send requests to GCP API
+ Altered print statement to remove unnecesary request # reporting
+ Removed total request argument as now unnecessary

 Changed arg `--reqs` to `--tests`
+ Reflects that some test modes can send upward of one request
+ Changed codebase to reflect naming convention change
+ Changed readback statements to show which test loop is running

 Renamed/reworked function `confirm_content`, now `set_behavior`
+ Function now determines what kind of test for the script to run with logicals, as well as handle the errors of the old function

 Removed function `startup_checklist`
+ Going forward, startup functions will now print a readback statement to the user as they set configuration details for the script
+ This cuts down on the amount of logical processes done by the script, but does decrease readability somewhat

 Added function `calc_total_reqs`
+ Function calculates the total number of POST requests the script will send for each initialization of the script
+ Will become more important as multithreading is implemented

 Renamed `validate_output` to `response_vign_validate`
+ Changed to better reflect what the function is accomplishing (increased clarity)

 Updated `main`
+ With inclusion of "set_behavior", can now much more clearly follow how Post requests are being sent differently based on the test behavior desired
+ Included all function calls that send a POST in the "Send POST requests" loop

## Version 0.4.2
*Released 8/16/23*

 Added env var "SAPATH"
+ Allows path to Service Account file for GCP testing to be set with env var

 Added argument "persona"
+ Used to test single persona data from knowledgebase input_message files
	* Will be helpful for debugging individual errors down the line (eg Fahad, Gaile bugs currently being encountered)

 Reworked argument and env var declaration and conflict handling
+ in-line assignment of args and env vars - decreases number of vars used overall
+ Removed if statements from `confirm_target` to support above

 Worked on GCP testing functionality
+ Assert statements added to ensure requisite info present before POSTing to GCP

 Re-worked vignette verification functionality
+ Clarified language returned by LDT to tell user verification is only against expected vignette content pairings, not validating overall message in some way.

 Refactored repo_test function
+ Removed repeat code blocks to allow for implementation of single repo test function

## Version 0.4.1
*Released 8/10/23*

 Changed `LDT_Addendum`
+ Changed from checking persona based keys to staff_number based keys
+ Allows for verification of any successful post request

 Changed verification procedure to allow any post request to be validated
+ Implemented verification of post request(s) based on using staff_number to compare against keys vs. using personas
+ Successfully tested functionality with both CSV and GitHub input messages

## Version 0.4.0
*Released 8/9/23*

 Added `LDT_Addendum.py` to Leakdown Tester folder
+ Functions as a store for large text variables that may need to periodically change without impacting `leakTester.py`
+ Contains verification target values
+ Contains header and footer of input_message JSON content for CSV payload building

 Removed function `assemble_payload`
+ Obsolete with LDT_Addendum addition	

 Added `validate` functionality to `repoTest`
+ Compares against a seperate python dictionary file with desired output message value pairs determined by the vignettes. Note: Only works alongside `repoTest`.
	* This file can be updated if vignette data changes without versioning Leakdown Tester

## Version 0.3.0
*Released 8/9/23*

 Added automated knowledgebase repo testing functionality
+ use `--repoTest` as arg to run

 Refactored script for readability and cohesion
+ GCP functionality not verified online
+ Planned: Verified GCP functionality, anticipated in next patch (V 1.3.1)

 Reformatted CSV-JSON builder
+ Removed debug key
+ Updated exepected performance data headers
+ Updated braketing to support debug key removal

## Version 0.2.0
*Released 8/7/23*

 Added Google Cloud Platform functionality
+ use `--target cloud` to test against the GCP API instance
+ Thanks Ayshwarya!

## Version 0.1.2
*Release 8/2/23*

 Updated useGit functionality
+ GitHub links now supercede CSV content without user input
	* Changed warning print to INFO to reflect above
+ useGit now accepts both 'raw' and standard github page links

 Updated startup messaging
+ Welcome message now predecates all print statements
+ Version number included in welcome message

## Version 0.1.1
*Released 8/2/23*

 Changed JSON content formatting for CSV-built messages
+ Updated to new baseline being used for full-team pipeline testing

## Version 0.1.0
*Released 8/2/23*

 Implemented useGit functionality 
+ Can now accept JSON content directly from GitHub files
+ Requires raw github link
	* Planned: implement code to convert non-raw link to raw before import, with a checker so both can be acceptable

## Version 0.0.1
*Released 7/30/23*
- Published to GitHub
- Added environment variable functionality
- Added argument functionality
- Added response printing and saving
- Created user manual
