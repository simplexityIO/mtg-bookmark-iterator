# Helpful URLs:
# Initially based off this:
#  - https://stackoverflow.com/questions/33644387/reading-the-chrome-bookmarks-json-file-in-python/70497407#70497407
# For parsing exported bookmark file:
#  - https://jayrambhia.com/blog/fetch-bookmarks-from-browserhtml-version-using-python
# Parses bookmarks into list of folders/urls:
#  - https://github.com/andrewp-as-is/chrome-bookmarks.py/blob/master/chrome_bookmarks/__init__.py
# Yennet, Cryptic Sovereign potential cards:
#  - chrome://bookmarks/?id=10336

# Example usage:
# import sys; sys.path.append(r"C:\Main\2022\misc\mtg_bookmark_iterator"); import mtg_bookmark_iterator as mbi; from importlib import reload as r
# url_1 = "https://scryfall.com/card/m20/36/sephara-skys-blade?4"
# url_2 = "http://mythicspoiler.com/mh2/cards/sealofremoval.html?6"
# url_3 = "https://scryfall.com/card/ncc/6/the-beamtown-bullies?"
# old_url_3 = "https://www.magicspoiler.com/mtg-spoiler/the-beamtown-bullets/?1"
# url_4 = "http://mythicspoiler.com/stx/cards/plarggdeanofchaos.html"
# r(mbi); card_name = mbi.get_card_name(url_1); color_identity = mbi.get_color_identity(card_name); print(color_identity)
# r(mbi); fresh_url = mbi.get_fresh_url(url_1); print(fresh_url_1)
# r(mbi); card_name = mbi.get_card_name(url_1); print(card_name)
# urls = """..."""
# mbi.check_for_duplicates(urls)
# mbi.open_mtg_tabs(urls, open_fresh_urls=True)
# r(mbi); x = mbi.ColorIdentity("BUW"); a = mbi.ColorIdentity("WR"); b = mbi.ColorIdentity("B"); c = mbi.ColorIdentity("WUBR")
# print("x: {x}\na: {a}\nb: {b}\nc: {c}\n".format(x=x.get_color_str(), a=a.get_color_str(), b=b.get_color_str(), c=c.get_color_str()))
# r(mbi); mbi.populate_commander_url_files()

# TODO:
# [A] | Update 'get_card_name' to properly extract card name from Scryfall links
# [B] | Update 'get_card_name' to handle non-Scryfall links (ex: mythicspoiler.com, magicspoiler.com)
# [C] | Prompt for arguments instead of passing them directly
# [D] | Allow for selection between multiple URL files
# [E] | Enable color identity filtering (requires Scryfall API call to get color identity)
# [F] | Enable skipping cards that are in another URL file
# [G] | Add the ability to continue after throwing error with 'crash_with_error' and make it toggleable with a parameter. Implement this feature in 'get_card_name'.
# [H] | Create function to run to generate URL files for commanders
# [I] | Add try/except logic for HTML requests to handle the no internet scenario gracefully. This StackOverflow page seems helpful if I need the error handling to be more robust: https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
# [J] | Figure out solution for populating URLs for Queen Marchesa dragon tribal deck in 'populate_commander_url_files'.
# [K] | Utilize 'check_for_duplicates' somewhere. Either automatically or in a separate .bat file.
# [L] | Organize/tidy up this file and its sections
# [M] | Print out progress in 'open_mtg_tabs'
# [N] | Implement window snapping function for tool.
# [O] | Convert tool into exe (pyinstaller mtg_bookmark_iterator.py) and create installer .bat to set up the tool's environment. Also create a help function for how to use tool.
# [P] | Add a debug mode option to aid in debugging with just executable.
# [Q] | CANCELED: Add a cleanup function to this module to clean up the temp files (C:\Users\{USERNAME}\AppData\Local\Temp\_MEI* or os.path.dirname(os.path.abspath(__file__))) created by the PyInstaller exe when it crashes or is killed. Potentially combine this with P. -- No longer needed now that changed to using one directory version of PyInstaller instead of one file version.
#  R  | Handle KeyboardInterrupt to close batch file window to avoid "Terminate Batch Job (Y/N)?" prompt and close the window when it should be closed.
# [S] | Add config options for path to bookmarks for non-"Default" Chrome user (ie. one other than the %APPDATA%\..\Local\Google\Chrome\User Data\Default\Bookmarks)" as well as path to Chrome exe
# [T] | Change calls to 'requests' module to 'selenium' since DT at work blocks Python exe's from accessing the internet
# -U- | Suppress "D_Lib: debug printing for files"... logging prints and ..."DllCanUnloadNow returned S_OK." print when launch Python file on work PC. Happens before the first line executes. -- Upon further investigation, the issue seems to be with a piece of SW called "Viewfinity" and it looks like it is indeed on my work PC and was acquired by/incorporated into Cyberark in 2015. No workaround seems to exist so will just live with the gross prints.
# [V] | Fix issue with shortcut not having the correct "Start in" location. Currently it has the location of the python environment on my work PC.
#  W  | Investigate weird Selenium error that have seen for the third time: "unknown error: missing or invalid columnNumber (Session info: headless chrome=102.0.5005.63)". It seems intermittent and rerunning is able to fix the issue.
# -X- | Make get_card_name more robust to be able to handle if have issues with Mythic Spoiler. Work PC really didn't seem to like Mythic Spoiler's Doll Stitcher URL: http://mythicspoiler.com/mid/cards/dollstitcher.html. Seems to only be finding one script object - the first in the file - and then tries to loop over that even though the HTML has the right script object. script_objs=<script async="" src="https://static.criteo.net/js/ld/publishertag.prebid.117.js" type="text/javascript"></script> -- Made 'get_card_name' a bit more robust, but decided to skip fixing this specific error in favor of Y which should remove all these Mythic Spoiler-specific issues.
# [Y] | Create function to aid in removing all non-Scryfall URLs from a commander's bookmarks
# [Z] | Add parameter to 'raise_error' to print error, but don't pause for user input. Can utilize this in 'check_for_duplicates' and maybe elsewhere.



# IMPORTS
from bs4 import BeautifulSoup, Comment
from collections import OrderedDict
import inspect
import json
import math
import os
import pyautogui
import pydoc
import pdb
from pynput.keyboard import Key, Controller
import re
import requests
import selenium
from selenium import webdriver
import subprocess
import sys
import textwrap
import time
import traceback
import webbrowser


# GLOBALS
if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
bookmark_data_str = ""
bookmark_data = {}
config_data = {}
BOOL_VALS = ["true", "false"]
SUPPORTED_CARD_WEBSITES = ["scryfall", "mythicspoiler", "magicspoiler"]
MAX_HTML_ACCESS_ATTEMPTS = 4
SCRYFALL_DELAY = 0.1 # Seconds
scryfall_last_accessed_time = None
ALWAYS_LAUNCH_DEBUGGER = True
SIDES = ["left", "right"]
KEYBOARD = Controller()
SUPER_FLAGS = ["help", "debug", "location"]
debug_mode = False
ORIG_STDOUT = sys.stdout
script_args = sys.argv
chrome_path = ""
driver = None


# HELPER FUNCTIONS

# Print a given error and wait for user input before exiting. Optionally can launch debugger, can allow user to continue on with execution if user accepts prompt, or can continue on with execution automatically.
def raise_error(error_message, prompt_to_continue=False, continue_with_no_prompt=False, launch_debugger=False):
    if ALWAYS_LAUNCH_DEBUGGER:
        launch_debugger = True
    indent = " " * 7
    width = 100

    for line in textwrap.wrap("ERROR: %s" % error_message, width=width, subsequent_indent=indent):
        print(line)
    
    if continue_with_no_prompt:
        print()
        return
    elif prompt_to_continue:
        if launch_debugger:
            print("Press enter to continue...\n\n")
        else:
            input("Press enter to continue...\n")
            return
    
    if launch_debugger:
        print()
        pdb.set_trace()
    else:
        input()
        sys.exit()


# Pause for user input and then exit
def pause_before_exiting(display_prompt=False):
    # Pause for user input before exiting
    if display_prompt:
        input("\n\nPress enter to exit.\n");
    else:
        input()

    # Exit script
    sys.exit()


def ask_yes_no_question(question, default_value=True):
    """
    Displays a yes or no question and prompts user for a response. Returns True or False based on the user's selection.

    Args:
        question: Yes or no question to ask the user
        default_value: Boolean representing the default answer for the yes/no question. A True value indicates the default value is "Yes" and a False value indicates the default is "No".

    Returns:
        True if the user selected 'yes' and False if the user selected 'no'.
    """

    # Sanity check: Received expected boolean type for 'default_value' parameter
    if type(default_value) != bool:
        print("ERROR: Received unexpected value for 'default_value' parameter: '%s'" % default_value)
        exit()

    # Initialize variables
    if default_value:
        prompt = " (Y)es [default] / (N)o?: "
        warning = "WARNING: Unknown input received. Please enter either 'Y' (or press enter) for yes or 'N' for no."
    else:
        prompt = " (Y)es / (N)o [default]?: "
        warning = "WARNING: Unknown input received. Please enter either 'Y' for yes or 'N' (or press enter) for no."

    # Prompt user
    while True:
        response = input(question + prompt).lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        elif response == "":
            return default_value
        print(warning)


# Print heading encased by line separators
def print_heading(heading):
    separator = "-" * 50
    print(separator, heading, separator, sep="\n")


# Returns whether argument passed is a regular (ie. non-super) flag. Regular flags are prefixed by a single hyphen.
def is_reg_flag(arg):
    return len(arg) >= 2 and arg[0] == "-"and arg[1] != "-"


# Returns whether argument passed is a super flag. Super flags are prefixed by two hyphens.
def is_super_flag(arg):
    return len(arg) >= 3 and arg[0:2] == "--"


# Removes all instances of super flag from arguments passed including any associated arguments
def remove_super_flag(super_flag, num_assoc_args=0):
    global script_args
    new_args = []
    skip_count = 0
    for i in range(len(script_args)):
        if skip_count == 0:
            arg = script_args[i]
            if is_super_flag(arg) and get_flag(arg).lower() == super_flag:
                skip_count = num_assoc_args
            else:
                new_args.append(arg)
        else:
            skip_count -= 1
    script_args = new_args


# Returns flag string extracted from argument
def get_flag(arg):
    if is_reg_flag(arg):
        return arg[1:]
    elif is_super_flag(arg):
        return arg[2:]
    else:
        raise_error("Argument '%s' is not a flag" % arg)


# Converts an MTG card name to a Windows filename
def convert_card_name_to_filename(card_name):
    strings_to_remove = [",", "'"]
    strings_to_replace_with_underscores = [" "]
    strings_to_replace_with_dashes = ["/"]
    new_card_name = card_name.lower()
    for sub_str in strings_to_remove:
        new_card_name = new_card_name.replace(sub_str, "")
    for sub_str in strings_to_replace_with_underscores:
        new_card_name = new_card_name.replace(sub_str, "_")
    for sub_str in strings_to_replace_with_dashes:
        new_card_name = new_card_name.replace(sub_str, "-")
    return new_card_name


# Returns bookmark data as a JSON by default or a string if specified
def get_bookmark_data(return_string=False):
    # Load config data if haven't already
    if not config_data:
        load_config_data()

    bookmarks_filename = os.path.join(os.getenv("APPDATA"), "..\\Local\\Google\\Chrome\\User Data\\%s\\Bookmarks" % config_data["chrome_profile"])
    bookmark_file = open(bookmarks_filename, "r", encoding="utf-8")
    bookmark_data = json.load(bookmark_file)
    bookmark_file.close()

    if return_string:
        bookmark_data_str = json.dumps(bookmark_data, indent=4)
        return bookmark_data_str
    else:
        return bookmark_data

# Load bookmark data into a global string
def load_bookmark_data_str():
    global bookmark_data_str
    bookmark_data_str = get_bookmark_data(return_string=True)


# Load bookmark data into a dictionary
def load_bookmark_data():
    global bookmark_data
    bookmark_data = get_bookmark_data()


# Load config data into a global variable
def load_config_data():
    global config_data
    global chrome_path
    try:
        with open(os.path.join(ROOT_DIR, "config.json"), "r") as config_file:
            raw_config_data = json.load(config_file)
    except json.decoder.JSONDecodeError as e:
        raise_error("Config file 'config.json' is not in JSON format. JSON decoding error message: %s" % e.args[0])
    config_data = raw_config_data["profiles"][raw_config_data["profile"]]
    raw_config_data.pop("profiles")
    config_data = {**config_data, **raw_config_data}
    chrome_path = "{chrome_path} %s".format(chrome_path=config_data["chrome_path"])


# Write config data into config file
# NOTE: Untested
def write_config_data(key, value):
    global config_data
    load_config_data()
    config_data[key] = value
    with open(os.path.join(ROOT_DIR, "config.json"), "w") as config_file:
        config_data.write(json.dumps(config_data), indent=4)


# Returns URLs from URLs file as one large string
def get_urls(urls_filepath="urls.txt"):
    if not os.path.isabs(urls_filepath):
        urls_filepath = os.path.abspath(os.path.join(ROOT_DIR, urls_filepath))
    else:
        urls_filepath = os.path.abspath(urls_filepath)
    with open(urls_filepath, "r") as urls_file:
        line = urls_file.readline()
        while len(line) > 0 and line[0] == "@":
            line = urls_file.readline()
        urls = line + urls_file.read()
    return urls


# Returns set of excluded cards pulled from excluded URLs file
# LIMITATIONS:
#  - See 'get_card_name' limitations. Since some cards on Mythic Spoiler will return blank card names, these cards will be ignored when creating the excluded cards set.
def get_excluded_cards(excluded_urls_filepath="excluded_urls.txt"):
    if not os.path.isabs(excluded_urls_filepath):
        excluded_urls_filepath = os.path.abspath(os.path.join(ROOT_DIR, excluded_urls_filepath))
    else:
        excluded_urls_filepath = os.path.abspath(excluded_urls_filepath)
    with open(excluded_urls_filepath, "r") as excluded_urls_file:
        line = excluded_urls_file.readline()
        while len(line) > 0 and line[0] == "@":
            line = excluded_urls_file.readline()
        excluded_urls_str = line + excluded_urls_file.read()
    excluded_cards = set([get_card_name(url) for url in re.split(",|\s", excluded_urls_str) if len(url) > 0 and get_card_name(url)]) # Ignore blank card names from some Mythic Spoiler URLs
    return excluded_cards


# Returns file metadata which are just the first lines of the file that begin with an @
# and are followed by the metadata tag, a colon, and its value. Ex: @Name: My file name
def get_file_metadata(filepath):
    metadata = {}
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(os.path.join(ROOT_DIR, filepath))
    else:
        filepath = os.path.abspath(filepath)
    with open(filepath, "r") as the_file:
        line = the_file.readline()
        while len(line) > 0 and line[0] == "@":
            parts = [part.strip() for part in line[1:].split(":", maxsplit=1) if len(part) > 0 and not part.isspace()]
            if len(parts) == 2:
                metadata[parts[0].lower()] = parts[1]
            line = the_file.readline()
    return metadata


# Returns the name of the file. This is is the name specified in its metadata if it exists. Otherwise it is simply the filename.
def get_name(filepath):
    metadata = get_file_metadata(filepath)
    if "name" in metadata:
        return metadata["name"]
    else:
        return os.path.basename(filepath)


# Returns a list of tuples corresponding to the contents of the 'urls' folder. The first element in a tuple is the name of the file and the second its path.
# Optionally return a string representation of the URL files available.
def get_url_files(return_string_too=False):
    urls_location = os.path.abspath(os.path.join(ROOT_DIR, "urls"))
    url_files = [(get_name(os.path.join(urls_location, filename)), os.path.join(urls_location, filename)) for filename in os.listdir(urls_location) if os.path.isfile(os.path.join(urls_location, filename))]
    if return_string_too:
        url_files_str = ""
        for i in range(len(url_files)):
            url_files_str += "[%s] %s\n" % (i+1, url_files[i][0])
        if len(url_files_str) > 0:
            url_files_str = url_files_str[:-1]
        return url_files, url_files_str
    else:
        return url_files


# Using parameters provided, constructs string to execute to run 'open_mtg_tabs'
def get_open_mtg_tabs_exec_str(params):
    open_mtg_tab_exec_str = "open_mtg_tabs("
    first_param = True
    for param in params:
        if first_param:
            first_param = False
        else:
            open_mtg_tab_exec_str += ", "
        if type(params[param]) == str:
            open_mtg_tab_exec_str += "%s='%s'" % (param, params[param])
        else:
            open_mtg_tab_exec_str += "%s=%s" % (param, params[param])
    open_mtg_tab_exec_str += ")"
    return open_mtg_tab_exec_str


# Return card data pulled from Scryfall API
def get_card_data(card_name, suppress_nonessential_errors=False):
    # Access globals for modifying
    global scryfall_last_accessed_time

    # Load config data if haven't already
    if not config_data:
        load_config_data()

    # Initialize variables
    api_url = "https://api.scryfall.com/cards/search?q=%s" % (card_name.lower().replace(" ", "+"))

    # Ensure don't overload Scryfall API by waiting if needed
    if scryfall_last_accessed_time and time.time() - scryfall_last_accessed_time < SCRYFALL_DELAY:
        time.sleep(SCRYFALL_DELAY - (time.time() - scryfall_last_accessed_time))
    scryfall_last_accessed_time = time.time()

    # Use 'requests' module to access API
    if config_data["scraping_module"] == "requests":
        # Access API
        try:
            response = requests.get(api_url)
        except requests.exceptions.ConnectionError as e:
            raise_error("Unable to access the internet.")
        attempt_num = 1
        while(not response.ok and attempt_num < MAX_HTML_ACCESS_ATTEMPTS):
            try:
                response = requests.get(api_url)
            except requests.exceptions.ConnectionError as e:
                raise_error("Unable to access the internet.")
            attempt_num += 1
            time.sleep(3)
        results = response.json()
        successfully_scraped_url = response.ok
    
    # Use 'selenium' module to scrape API URL. Slower, but a necessary workaround on work PC that blocks Python exe from accessing the internet.
    elif config_data["scraping_module"] == "selenium":
        # Initialize Chrome driver if haven't already
        if not driver:
            init_driver()

        # Set wait time for HTML content to that for Scryfall API. Scryfall API shouldn't need as long of a wait time as Mythic Spoiler.
        driver.implicitly_wait(config_data["scryfall_api_wait_time"])

        # Scrape API URL
        try:
            driver.get(api_url)
        except selenium.common.exceptions.WebDriverException as e:
            if "ERR_INTERNET_DISCONNECTED" in e.msg:
                raise_error("Unable to access the internet.")
            else:
                raise_error("Unexpected error when attempting to access Scryfall API for card '%s'. Error message: %s" % (card_name, e.msg))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        html_contents = soup.find("html").text
        results = json.loads(html_contents)
        successfully_scraped_url = html_contents != ""

    # Unknown scraping module given
    else:
        raise_error("Unknown scraping module '%s'." % config_data["scraping_module"])
    
    # Return API results or throw error if was unsuccessful in getting API results
    if successfully_scraped_url and results["object"] == "list":
        return results
    elif not successfully_scraped_url and "object" in results and results["object"] == "error":
        if not suppress_nonessential_errors:
            raise_error("Scryfall API returned the following error for card '%s':\n%s" % (card_name, results["details"]))
        return None
    else:
        if not suppress_nonessential_errors:
            raise_error("Unable to access Scryfall API for card '%s'." % card_name)
        return None


# Return color identity of the given card
def get_color_identity(card_name):
    # Extract color identity from API results
    card_data = get_card_data(card_name)
    if card_data:
        color_identity = ColorIdentity(card_data["data"][0]["color_identity"])
    else:
        return None # Included for robustness only. 'get_card_data' will throw an error if return None for card data.

    # Return color identity for card    
    return color_identity


# Return Scryfall URL for the given card
def get_scryfall_url(card_name, get_fresh=False, suppress_nonessential_errors=False):
    # Extract color identity from API results
    card_data = get_card_data(card_name, suppress_nonessential_errors=suppress_nonessential_errors)
    if card_data:
        scryfall_url = card_data["data"][0]["scryfall_uri"]
        question_mark_index = scryfall_url.rfind("?")
        scryfall_url = scryfall_url[:question_mark_index]
    else:
        return None # Included for robustness only. 'get_card_data' will throw an error if return None for card data.

    # Get fresh URL if specified
    if card_data and get_fresh:
        scryfall_url = get_fresh_url(scryfall_url)

    # Return Scryfall URL for card    
    return scryfall_url


# Snaps the current window to the left or right. Right is the default.
# Note: 'pyautogui' seems to be a bit more reliable than 'pynput' as far as entering key inputs. However, it also has numerous third party dependencies.
#       Thus if have to install dependencies by hand due to perhaps not having a working pip, have included a default 'pynput' option that works well
#       with some small delays. 'pynput' is still a third party libary, but has no third party dependencies.
# LIMITATIONS:
#  - This function is not intelligent and simply enters the Win+Left or Win+Right keyboard shortcuts. Thus, if the window is already snapped (to either side), it will not end up snapped to the side specified.
def snap_window(side="right", module_to_use="pynput"):
    # Verify supplied a valid side to snap to
    if side.lower() not in SIDES:
        raise_error("'%s' is not a valid side to snap to." % side)

    # Use 'pyautogui' module to snap window
    if module_to_use == "pyautogui":
        pyautogui.keyDown("winleft")
        pyautogui.press(side.lower())
        pyautogui.keyUp("winleft")
        time.sleep(0.2)
        pyautogui.press("esc")

    # Use 'pynput' module to snap window
    elif module_to_use == "pynput":
        if side == "right":
            side_button = Key.right
        else:
            side_button = Key.left
        with KEYBOARD.pressed(Key.cmd):
            KEYBOARD.press(side_button)
            time.sleep(0.1)
            KEYBOARD.release(side_button)
        time.sleep(0.2)
        KEYBOARD.press(Key.esc)
        time.sleep(0.1)
        KEYBOARD.release(Key.esc)


# Checks if function from this module was passed in to call and calls it and exits if so. Otherwise, does nothing.
def handle_function_call():
    # Initialize variables
    curr_globals = globals()
    func_list = {}
    for el in curr_globals:
        if inspect.isfunction(curr_globals[el]):
            func_list[el] = curr_globals[el]

    # First argument passed is a regular flag and a function in this module
    if len(script_args) > 1 and is_reg_flag(script_args[1]) and get_flag(script_args[1]) in func_list:

        # Construct the function exec string from the arguments passed
        function_name = get_flag(script_args[1])
        func_exec_str = "%s(" % function_name
        idx = 2
        while idx < len(script_args):
            if is_reg_flag(script_args[idx]):
                func_exec_str += "%s=" % get_flag(script_args[idx])
            else:
                if script_args[idx].lower() in BOOL_VALS or script_args[idx].isdigit():
                    func_exec_str += "%s" % script_args[idx]
                else:
                    func_exec_str += "'%s'" % script_args[idx]

                if idx != len(script_args) - 1:
                    func_exec_str += ", "
            idx += 1
        func_exec_str += ")"
        
        # Execute the function with the given parameters and then exit script
        exec(func_exec_str)
        sys.exit()

    # First argument is not a function in this module. Do nothing.
    else:
        pass


# Checks if super flag was passed and executes the appropriate actions if so. Otherwise, does nothing.
def handle_super_flags():
    # Access globals for modifying
    global debug_mode
    global ROOT_DIR

    # Loop over arguments and process any valid super flags in the order they appear
    for i in range(1, len(sys.argv)):
        if is_super_flag(sys.argv[i]) and get_flag(sys.argv[i]).lower() in SUPER_FLAGS:

            # Get super flag
            super_flag = get_flag(sys.argv[i]).lower()

            # 'Help' super flag
            if super_flag == "help":
                print_help()

            # 'Debug' super flag
            elif super_flag == "debug":
                if not debug_mode:
                    print_heading("ENTERING DEBUG MODE")
                    debug_mode = True
                    pdb.set_trace()
                    remove_super_flag("debug")

            # 'Location' super flag
            elif super_flag == "location":
                if i+1 < len(sys.argv):
                    if os.path.exists(sys.argv[i+1]):
                        ROOT_DIR = sys.argv[i+1]
                        remove_super_flag("location", num_assoc_args=1)
                    else:
                        raise_error("Location '%s' does not exist." % sys.argv[i+1])
                else:
                    raise_error("No location supplied with 'location' super flag.")

            # Unhandled super flag. Should never get here.
            else:
                raise_error("Unhandled super flag '%s'." % super_flag)


# Print out how to utilize tool
def print_help():
    print(pydoc.render_doc(sys.modules[__name__], title="MTG Bookmark Iterator:\n\n%s", renderer=pydoc.plaintext))
    pause_before_exiting()


# Initialize Chrome driver
def init_driver(suppress_prints=False):
    # Access globals for modifying
    global driver

    # Load config data if haven't already
    if not config_data:
        load_config_data()

    # Print header if specified
    if not suppress_prints:
        print_heading("Initializing Chrome driver for Selenium...")
        print()

    # Create options for driver
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) # Don't print out anything to console
    options.add_argument("user-agent=%s" % user_agent)
    options.page_load_strategy = "eager" # Just wait for initial HTML and not images and the like

    # Create driver
    try:
        driver = webdriver.Chrome(options=options)

    # Handle the case where Chrome driver is not up-to-date with current Chrome version.
    # Note: There exists a Python module 'webdrivermanager' that can automatically update the Chrome driver. Unfortunately, it uses the 'requests' module
    #       which means that the Python exe needs to access the internet. Since this tool needs to work on my work PC and DT blocks Python exe's from
    #       accessing the internet, was unable to directly use the 'webdrivermanager' module. However, much of this logic is taken from that module.
    except selenium.common.exceptions.SessionNotCreatedException as e:
        basic_chromedriver_version_pattern = r"(supports Chrome version )(\d+)"
        chromedriver_version = re.search(basic_chromedriver_version_pattern, e.msg).group(2)
        chrome_version_pattern = r"(\d+\.\d+.\d+)(\.\d+)"
        chrome_version = re.search(chrome_version_pattern, e.msg).group(1)
        # Note: Additional way to get Chrome version which queries the registry
        # chrome_version_cmd = ["reg", "query", r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon", "/v", "version"]
        # cmd_output = subprocess.check_output(cmd).decode().strip()
        # chrome_version = re.search(chrome_version_pattern, cmd_output).group(1)
        all_chromedrivers_api_url = "https://www.googleapis.com/storage/v1/b/chromedriver/o"
        chromedriver_site_url = "https://chromedriver.chromium.org/downloads"
        webbrowser.get(chrome_path).open(all_chromedrivers_api_url)
        raise_error("Selenium requires a Chrome driver that matches your current version of Chrome. Current Chrome driver is for version {chromedriver_version} and your current Chrome version is {chrome_version}. \
Just opened the Chrome driver API URL for all Chrome drivers: '{all_chromedrivers_api_url}'. Please find the win32 \"mediaLink\" that matches version {chrome_version}. Download and extract the chromedriver zip file, put the file in C:/webdrivers, and re-run the tool. \
If you are unable to find the correct download link, visit the human-friendly site '{chromedriver_site_url}' and find it there.".format(chromedriver_version=chromedriver_version, chrome_version=chrome_version, all_chromedrivers_api_url=all_chromedrivers_api_url, chromedriver_site_url=chromedriver_site_url))

    # Define a default implicit wait for driver. Will overwrite this with respective wait times for specific sites accessing.
    driver.implicitly_wait(15) # Wait this long (in seconds) when searching for desired objects on page




# CLASSES

# Class for color identities of cards. Supports comparisons.
class ColorIdentity:
    colors = ["W", "U", "B", "R", "G"]

    # Note: 'selected_colors' can be either a string or a list
    def __init__(self, selected_colors):
        self.color_str = ""
        unsorted_color_str = ""
        
        # Treat no colors specified as WUBRG. This is how Scryfall returns the color identities for artifacts.
        if len(selected_colors) == 0:
            self.color_str = "WUBRG"
            return

        for color in selected_colors:
            if color not in self.colors:
                raise_error("Unknown color '%s'" % color)
            elif color not in self.color_str:
                unsorted_color_str += color
        for color in self.colors:
            if color in unsorted_color_str:
                self.color_str += color

    def get_color_str(self):
        return self.color_str

    def __lt__(self, other):
        if type(other) == str:
            other = ColorIdentity(other)
        if type(other) == ColorIdentity:
            other_color_str = other.get_color_str()
            if len(self.color_str) >= len(other_color_str):
                return False
            for color in self.color_str:
                if color not in other_color_str:
                    return False
            return True
        else:
            raise TypeError("'<' not supported between instances of '%s' and '%s'" % (type(self).__name__, type(other).__name__))

    def __gt__(self, other):
        if type(other) == str:
            other = ColorIdentity(other)
        if type(other) == ColorIdentity:
            other_color_str = other.get_color_str()
            if len(other_color_str) >= len(self.color_str):
                return False
            for color in other_color_str:
                if color not in self.color_str:
                    return False
            return True
        else:            
            raise TypeError("'>' not supported between instances of '%s' and '%s'" % (type(self).__name__, type(other).__name__))

    def __le__(self, other):
        if type(other) == str:
            other = ColorIdentity(other)
        if type(other) == ColorIdentity:
            other_color_str = other.get_color_str()
            if len(self.color_str) > len(other_color_str):
                return False
            for color in self.color_str:
                if color not in other_color_str:
                    return False
            return True
        else:
            raise TypeError("'<=' not supported between instances of '%s' and '%s'" % (type(self).__name__, type(other).__name__))

    def __ge__(self, other):
        if type(other) == str:
            other = ColorIdentity(other)
        if type(other) == ColorIdentity:
            other_color_str = other.get_color_str()
            if len(other_color_str) > len(self.color_str):
                return False
            for color in other_color_str:
                if color not in self.color_str:
                    return False
            return True
        else:
            raise TypeError("'>=' not supported between instances of '%s' and '%s'" % (type(self).__name__, type(other).__name__))

    def __eq__(self, other):
        if type(other) == str:
            other = ColorIdentity(other)
        if type(other) == ColorIdentity:
            other_color_str = other.get_color_str()
            return self.color_str == other_color_str
        else:
            return False

    def __ne__(self, other):
        if type(other) == str:
            other = ColorIdentity(other)
        if type(other) == ColorIdentity:
            other_color_str = other.get_color_str()
            return self.color_str != other_color_str
        else:
            return True

    def __repr__(self):
        ret_str = "%s(" % (type(self).__name__)
        for el in self.__dict__:
            ret_str += "%s=%r, " % (el, self.__dict__[el])
        if ret_str[-2:] == ", ":
            ret_str = ret_str[:-2] + ")"
        return ret_str

    def __str__(self):
        return self.color_str




# FUNCTIONS

# Checks list of URLs for duplicate cards
# LIMITATIONS:
#  - See 'get_card_name' limitations. Since some cards on Mythic Spoiler will return blank card names, cannot check them for duplicates.
def check_for_duplicates(urls=None):
    # Initialize variables
    cards_seen = OrderedDict()
    found_duplicates = False
    url_files, url_files_str = get_url_files(return_string_too=True)
    url_files_str = "[0] All of the below\n" + url_files_str
    check_all_files = False
    finished_checking = False
    idx = 0
    title = None
    
    # If no URLs are provided, prompt user to select which file(s) to use
    if not urls:
        selected_option = input("Choose file(s) to check for duplicates (default=urls.txt):\n%s\n " % url_files_str)
        if selected_option.isdigit():
            if int(selected_option) == 0:
                check_all_files = True
            else:
                title, urls = url_files[int(selected_option)-1]
        elif selected_option == "":
            title = urls = "urls.txt" 
        else:
            raise_error("Unexpected selection '%s" % selected_option)

    # Convert URLs to list if passed in as a string (including as a filename or just listed in a string)
    if not check_all_files:
        if type(urls) == str:
            if os.path.exists(urls):
                if not title:
                    title = urls
                urls = get_urls(urls)
            urls = [url for url in re.split(",|\s", urls) if len(url) > 0]
        if type(urls) not in [list]:
            raise_error("Unexpected type '%s' for 'urls'" % type(urls).__name__)

    # Check file(s) for duplicates
    while not finished_checking:

        # If checking all files, load the next file's URLs to check
        if check_all_files:
            title = url_files[idx][0]
            urls = [url for url in re.split(",|\s", get_urls(url_files[idx][1])) if len(url) > 0]

        # Iterate over URLs
        if title:
            print("\nChecking %s..." % title)
        else:
            print("\nChecking...")
        for url in urls:
            card_name = get_card_name(url, continue_with_no_prompt=True)
            if card_name: # Ignore blank card names from some Mythic Spoiler URLs
                if card_name in cards_seen:
                    found_duplicates = True
                    cards_seen[card_name].append(url)
                else:
                    cards_seen[card_name] = [url]

        # Print results
        if title:
            print_heading(title)
        else:
            print()
        if found_duplicates:
            print("Duplicates found:\n")
            for card_name in cards_seen:
                if len(cards_seen[card_name]) > 1:
                    print("Card: '%s'" % card_name)
                    for url in cards_seen[card_name]:
                        print(" - %s" % url)
                    print()
        else:
            print("No duplicates found.")

        # Determine whether finished checking for duplicates and prep for next file to check if not
        if check_all_files and idx < len(url_files) - 1:
            idx += 1
            cards_seen.clear()
            found_duplicates = False
        else:
            finished_checking = True

    # Pause before exiting
    pause_before_exiting()



# Convert all non-Scryfall URLs from a list to their Scryfall counterparts
def convert_urls_to_scryfall(urls=None):
    # Initialize variables
    non_scryfall_urls = OrderedDict()
    non_scryfall_count = 0
    urls_processed = 0
    url_files, url_files_str = get_url_files(return_string_too=True)
    url_files_str = "[0] All of the below\n" + url_files_str
    convert_all_files = False
    finished_converting = False
    idx = 0
    title = None
    get_card_name_for_search = lambda card_name: card_name.lower().replace(" ", "+")
    api_base_url = "https://api.scryfall.com/cards/search?q={card_name}"
    scryfall_base_url = "https://scryfall.com/search?q={card_name}"
    
    # If no URLs are provided, prompt user to select which file(s) to use
    if not urls:
        selected_option = input("Choose file(s) to convert to Scryfall URLs (default=urls.txt):\n%s\n " % url_files_str)
        if selected_option.isdigit():
            if int(selected_option) == 0:
                convert_all_files = True
            else:
                title, urls = url_files[int(selected_option)-1]
        elif selected_option == "":
            title = urls = "urls.txt" 
        else:
            raise_error("Unexpected selection '%s" % selected_option)

    # Convert URLs to list if passed in as a string (including as a filename or just listed in a string)
    if not convert_all_files:
        if type(urls) == str:
            if os.path.exists(urls):
                if not title:
                    title = urls
                urls = get_urls(urls)
            urls = [url for url in re.split(",|\s", urls) if len(url) > 0]
        if type(urls) not in [list]:
            raise_error("Unexpected type '%s' for 'urls'" % type(urls).__name__)

    # Convert URLs to Scryfall counterparts
    while not finished_converting:

        # If converting all files, load the next file's URLs to convert
        if convert_all_files:
            title = url_files[idx][0]
            urls = [url for url in re.split(",|\s", get_urls(url_files[idx][1])) if len(url) > 0]

        # Iterate over URLs
        if title:
            print("\nFinding non-Scryfall URLs for %s..." % title)
        else:
            print("\nFinding non-Scryfall URLs...")
        for url in urls:
            url_card_website = None
            for card_website in SUPPORTED_CARD_WEBSITES:
                if card_website in url:
                    url_card_website = card_website
                    break
            if url_card_website != "scryfall":
                non_scryfall_count += 1
                card_name = get_card_name(url, suppress_nonessential_errors=True)
                if card_name not in non_scryfall_urls:
                    non_scryfall_urls[card_name] = [url]
                else:
                    non_scryfall_urls[card_name].append(url)

        # Print results and open tabs to convert bookmarks
        if title:
            print_heading(title)
        else:
            print()
        if non_scryfall_count > 0:
            if "" in non_scryfall_urls:
                blank_card_name_count = len(non_scryfall_urls[""])
            else:
                blank_card_name_count = 0
            print("Found %s non-Scryfall URLs (extracted card names from %s of them):\n" % (non_scryfall_count, non_scryfall_count-blank_card_name_count))
            for card_name in non_scryfall_urls:
                if card_name != "":
                    urls_processed += 1
                    scryfall_url = get_scryfall_url(card_name, get_fresh=True, suppress_nonessential_errors=True)
                    print("Card: '%s'" % card_name)
                    for url in non_scryfall_urls[card_name]:
                        print(" - [OLD] %s" % url)
                        webbrowser.get(chrome_path).open(url)
                    if scryfall_url:
                        print(" - [NEW] %s" % scryfall_url)
                        webbrowser.get(chrome_path).open(scryfall_url)
                    else:
                        print(" - [NEW] Unable to get Scryfall URL for card")
                    input("\n[%s/%s] PAUSED: Convert URL now. Press enter to continue." % (urls_processed, non_scryfall_count))
                    print("\n")
            if blank_card_name_count > 0:
                print("Unable to find card names for %s URLs:" % blank_card_name_count)
                for url in non_scryfall_urls[""]:
                    urls_processed += 1
                    print(" - [OLD] %s" % url)
                    webbrowser.get(chrome_path).open(url)
                    input("\n[%s/%s] PAUSED: Convert URL now. Press enter to continue." % (urls_processed, non_scryfall_count))
                    print()
            print("Finished converting %s of %s URLs.\n" % (urls_processed, non_scryfall_count))

        else:
            print("All URLs are Scryfall URLs.\n")

        # Determine whether finished converting and prep for next file to convert if not
        if convert_all_files and idx < len(url_files) - 1:
            idx += 1
            non_scryfall_urls.clear()
            non_scryfall_count = 0
            urls_processed = 0
        else:
            finished_converting = True

    # Pause before exiting
    pause_before_exiting()


# Populates URL files for commanders in Chrome bookmarks
def populate_commander_url_files(suppress_prints=False):
    # Load config data if haven't already and update bookmark data
    if not config_data:
        load_config_data()
    load_bookmark_data()

    # Initialize variables
    commander_path = config_data["commander_path"]
    root = bookmark_data["roots"]
    curr_dir = None
    for location in root:
        if root[location]["name"].lower() == commander_path[0].lower():
            curr_dir = root[location]
    if not curr_dir:
        raise_error("'%s' is not a valid location for bookmarks." % commander_path[0])
    commander_dir = None
    found_dir = False

    # Find commander folder in bookmarks
    for i in range(1, len(commander_path)):
        for el in curr_dir["children"]:
            if el["type"] == "folder" and el["name"].lower() == commander_path[i].lower():
                curr_dir = el
                found_dir = True
                break
        if found_dir:
            found_dir = False
        else:
            raise_error("Unable to find folder '%s' in bookmarks." % os.path.join(*commander_path[:i+1]))
    if int(curr_dir["id"]) == config_data["commander_bookmarks_id"]:
        commander_dir = curr_dir
    else:
        raise_error("Folder '%s' in bookmarks is not the 'Commander' folder." % os.path.join(*commander_path))

    # Loop through commanders and create/populate their URL files
    for el_1 in commander_dir["children"]:
        if int(el_1["id"]) not in config_data["excluded_commander_bookmarks_ids"]:
            commander_name = el_1["name"]
            found_potential_cards = False

            for el_2 in el_1["children"]:
                potential_cards = None

                if "potential" in el_2["name"].lower() and "cards" in el_2["name"].lower():
                    potential_cards = el_2
                    found_potential_cards = True
                    modifier = " ".join([substr.strip() for substr in re.split("potential|cards", el_2["name"].lower()) if substr.strip()]).capitalize()

                    if modifier:
                        url_filepath = os.path.join(ROOT_DIR, "urls", convert_card_name_to_filename("%s_%s" % (commander_name, modifier)) + ".txt")
                    else:
                        url_filepath = os.path.join(ROOT_DIR, "urls", convert_card_name_to_filename(commander_name) + ".txt")
                    if not suppress_prints:
                        if modifier:
                            print("Processing %s | %s..." % (commander_name, modifier))
                        else:
                            print("Processing %s..." % commander_name)
                    with open(url_filepath, "w+") as url_file:
                        if modifier:
                            url_file.write("@Name: %s | %s\n" % (commander_name, modifier))
                        else:
                            url_file.write("@Name: %s\n" % commander_name)
                        for el_2 in potential_cards["children"]:
                            if el_2["type"] == "url":
                                url = el_2["url"]
                                url_file.write(url + "\n")

            if not found_potential_cards:
                raise_error("Unable to find a 'Potential cards' folder for commander '%s'." % commander_name)
    

# Return card name for the given URL
# LIMITATIONS: 
#  - Adventure cards and other split cards will not return the same card name depending on the site the URL belongs to since Scryfall includes the
#    second card name in the URL while Mythic Spoiler and Magic Spoiler do not.
#  - Some cards on Mythic Spoiler do not have the card name embedded anywhere in the HTML, seemingly since the card image is so clear. Thus these card
#    names will get returned as empty strings and should be ignored. Ex: http://mythicspoiler.com/khm/cards/talesoftheancestors.html
def get_card_name(url, suppress_nonessential_errors=False, continue_with_no_prompt=False):
    # Load config data if haven't already
    if not config_data:
        load_config_data()

    # Initialize variables
    url_card_website = None
    for card_website in SUPPORTED_CARD_WEBSITES:
        if card_website in url:
            url_card_website = card_website
            break

    # Scrape the card name from the URL if it's from Mythic Spoiler (since its URLs smash all the words together)
    if url_card_website == "mythicspoiler":
        # Use 'requests' module to scrape URL
        if config_data["scraping_module"] == "requests":
            # Scrape URL
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError as e:
                raise_error("Unable to access the internet.")
            attempt_num = 1
            while(not response.ok and attempt_num < MAX_HTML_ACCESS_ATTEMPTS):
                try:
                    response = requests.get(url)
                except requests.exceptions.ConnectionError as e:
                    raise_error("Unable to access the internet.")
                attempt_num += 1
                time.sleep(3)
            soup = BeautifulSoup(response.text, "html.parser")
            successfully_scraped_url = response.ok

        # Use 'selenium' module to scrape URL. Slower, but a necessary workaround on work PC that blocks Python exe from accessing the internet.
        elif config_data["scraping_module"] == "selenium":
            # Initialize Chrome driver if haven't already
            if not driver:
                init_driver()

            # Set wait time for HTML content to that for Mythic Spoiler. Mythic Spoiler has video ads that constantly update and thus the HTML is always changing and never completely "finishes" loading.
            driver.implicitly_wait(config_data["mythicspoiler_wait_time"])

            # Scrape URL
            try:
                driver.get(url)
            except selenium.common.exceptions.WebDriverException as e:
                if "ERR_INTERNET_DISCONNECTED" in e.msg:
                    raise_error("Unable to access the internet.")
                else:
                    if not suppress_nonessential_errors:
                        raise_error("Unexpected error when scraping card name for Mythic Spoiler URL: '%s'. Error message: %s" % (url, e.msg), continue_with_no_prompt=continue_with_no_prompt)
                    return ""
            soup = BeautifulSoup(driver.page_source, "html.parser")
            html_contents = soup.find("html").text
            successfully_scraped_url = html_contents != ""

        # Unknown scraping module given
        else:
            raise_error("Unknown scraping module '%s'." % config_data["scraping_module"])

        # Extract card name from scraped HTML
        if successfully_scraped_url:
            try:
                card_name_comment = soup.find(string=lambda text: isinstance(text, Comment) and text == "CARD NAME")

                # Card name comment exists
                if card_name_comment:
                    # card_name = card_name_comment.next.strip().lower() # Note: Old implementation. Fails when card name comment contains a script with the "thecardname" variable such as for Dig Up the Body.
                    card_name = card_name_comment.parent.text.strip().lower()
                
                # No card name comment exists
                else:
                    # Flip cards like those from Strixhaven (https://mythicspoiler.com/stx/) don't have the card name comment, but do have the card name elsewhere buried in a 'script' object.
                    script_objs = soup.find("script")
                    if script_objs:
                        for script_obj in script_objs:
                            if "var thecardname" in script_obj.string:
                                card_name = [substr.strip() for substr in re.split("var thecardname|=|\"|;", script_obj) if substr.strip()][0]
                                break

                    # Unexpected HTML format for Mythic Spoiler card
                    if not card_name:
                        if not suppress_nonessential_errors:
                            raise_error("Unable to scrape card name for Mythic Spoiler URL: '%s'." % url, continue_with_no_prompt=continue_with_no_prompt)
                        return ""
            except:
                if not suppress_nonessential_errors:
                    raise_error("Unexpected error when scraping card name for Mythic Spoiler URL: '%s'." % url, continue_with_no_prompt=continue_with_no_prompt)
                return ""

        else:
            if not suppress_nonessential_errors:
                raise_error("Unable to scrape URL '%s'." % url, continue_with_no_prompt=continue_with_no_prompt, launch_debugger=True)
            return ""

    # Get the card name from in-between the first forward slash (second for Magic Spoiler) and question mark
    else:
        question_mark_index = url.rfind("?")
        if url_card_website == "magicspoiler":
            card_name_index = url.rfind("/", 0, url.rfind("/")) + 1
        else:
            card_name_index = url.rfind("/") + 1
        if question_mark_index > 0:
            card_name = url[card_name_index:question_mark_index]
        else:
            card_name = url[card_name_index:]
        if url_card_website == "magicspoiler":
            card_name = card_name[:-1]
        card_name = card_name.replace("-", " ")

    # Return the card name
    return card_name.title()


# Returns "fresh" (ie. unbookmarked) version of URL provided
def get_fresh_url(url):
    # Load bookmark data if not yet loaded
    if not bookmark_data_str:
        load_bookmark_data_str()

    # Construct initial fresh URL using index of question mark in URL if it exists
    question_mark_index = url.rfind("?")
    if question_mark_index > 0:
        fresh_url = url[:question_mark_index]
    else:
        fresh_url = url

    # Continue incrementing URL number until find an unused/unbookmarked "fresh" URL
    while ("\"%s\"" % fresh_url) in bookmark_data_str:
        question_mark_index = fresh_url.rfind("?")
        if question_mark_index > 0:
            card_num_str = fresh_url[question_mark_index + 1:]
            if len(card_num_str) == 0:
                card_num = 0
            else:
                card_num = int(card_num_str)
            fresh_url = "%s?%s" % (fresh_url[:question_mark_index], card_num + 1)
        else:
            fresh_url = fresh_url + "?"
    
    # Return fresh URL found
    return fresh_url


# Extract parameters from command line input. Parameters are expected to match 'open_mtg_tabs' parameters.
# Note that filepaths need to use forwards slashes to enable exec of 'open_mtg_tabs' to work later. Thus all filepaths are modified to use forward slashes.
def extract_params():
    # Initialize variables
    params = {}
    param_list = inspect.getfullargspec(open_mtg_tabs).args
    defaults = inspect.getfullargspec(open_mtg_tabs).defaults
    url_files, url_files_str = get_url_files(return_string_too=True)
    new_url_files_str = ""
    for line in re.split("\n", url_files_str):
        new_url_files_str += "\t\t%s\n" % line
    url_files_str = new_url_files_str
    url_file_params = ["urls", "excluded_cards"]

    # Command line parameters were supplied
    if len(script_args) > 1:
        # Odd number of command line parameters
        if len(script_args[1:]) % 2:
            raise_error("Missing parameter or parameter value")

        # Loop over each pair of command line parameters
        for i in range(math.floor(len(script_args[1:]) / 2)):
            # Initialize local variables
            arg_1 = script_args[1:][i*2]
            arg_2 = script_args[1:][i*2 + 1]

            # Parameter is not a regular flag to denote it being a parameter name
            if not is_reg_flag(arg_1):
                raise_error("Expected following value to be a parameter name: '%s'" % arg_1)

            # Set parameter to value supplied
            elif get_flag(arg_1) in param_list:
                param = get_flag(arg_1)
                if arg_2.lower() in BOOL_VALS:
                    param_value = bool(arg_2)
                elif arg_2.isdigit():
                    param_value = int(arg_2)
                else:
                    param_value = arg_2

                    # Support passing in Commander name
                    if not os.path.exists(arg_2):
                        for commander_name, url_filepath in url_files:
                            if arg_2.lower() == commander_name.lower():
                                param_value = url_filepath.replace(os.sep, "/")
                                break
                    
                params[param] = param_value

            # Parameter is not one of the parameters of 'open_mtg_tabs' nor is it a function in this module
            else:
                raise_error("Unsupported parameter: '%s'" % get_flag(arg_1))

    # If no parameters were passed, prompt user if want to use default values or supply them now
    if len(params) == 0:
        should_prompt_for_params = ask_yes_no_question("No parameters were passed. Do you wish to supply them now?\nDefaults will be used otherwise.")
        if should_prompt_for_params:
            print("Select parameters (press enter to use default):")
            for param in param_list:
                if param in url_file_params:
                    selected_option = input("\t%s (default=%s):\n%s\t\t " % (param, defaults[param_list.index(param)], url_files_str))
                else:
                    selected_option = input("\t%s (default=%s): " % (param, defaults[param_list.index(param)]))
                if len(selected_option) > 0:
                    if selected_option.lower() in BOOL_VALS:
                        param_value = bool(selected_option)
                    elif selected_option.isdigit():
                        if param in url_file_params:
                            param_value = url_files[int(selected_option)-1][1].replace(os.sep, "/")
                        else:
                            param_value = int(selected_option)
                    else:
                        if os.path.isfile(selected_option):
                            param_value = selected_option.replace(os.sep, "/")
                        else:
                            param_value = selected_option
                    params[param] = param_value
            print()

    # Return parameters extracted
    return params


# Opens a list of URLs in last used Chrome window
def open_mtg_tabs(urls="urls.txt", excluded_cards="excluded_urls.txt", chunk_size=10, open_fresh_urls=False, color_identity=None):
    # Load config data if haven't already
    if not config_data:
        load_config_data()

    # Initialize variables
    tabs_opened = 0
    tabs_processed = 0
    if type(urls) == str: # Convert URLs to list if passed in as a string (including as a filename or just listed in a string)
        if os.path.exists(urls):
            urls = get_urls(urls)
        urls = [url for url in re.split(",|\s", urls) if len(url) > 0]
    if type(urls) not in [list]:
        raise_error("Unexpected type '%s' for 'urls'" % type(urls).__name__)
    if type(excluded_cards) == str and os.path.exists(excluded_cards):
        excluded_cards = get_excluded_cards(excluded_cards)
    if type(excluded_cards) not in [list, set]:
        raise_error("Unexpected type '%s' for 'excluded_cards'" % type(excluded_cards).__name__)
    total_tabs_to_process = len(urls)
    if color_identity:
        color_identity = ColorIdentity(color_identity)

    # Print out that opening tabs
    if chunk_size:
        print("Processing %s tabs in chunks of %s..." % (total_tabs_to_process, chunk_size))
    else:
        print("Processing %s tabs..." % total_tabs_to_process)

    # Iterate over URLs
    for url in urls:
        # Card is not in the excluded cards list and is within color identity if specified
        card_name = get_card_name(url)
        if card_name not in excluded_cards and (not color_identity or color_identity == "WUBRG" or get_color_identity(card_name) <= color_identity):

            # Open URL (fresh if specified)
            if open_fresh_urls:
                fresh_url = get_fresh_url(url)
                url_to_open = fresh_url
            else:
                url_to_open = url
            webbrowser.get(chrome_path).open(url_to_open)
            tabs_opened += 1
            tabs_processed += 1
            print("*", end="", flush=True)

            # Pause if reached the end of a chunk
            if chunk_size and tabs_opened % chunk_size == 0 and tabs_processed < len(urls):
                # input("PAUSED (%s of %s processed so far): Opening tabs in chunks of %s. Press enter to open next chunk.\n" % (tabs_processed, total_tabs_to_process, chunk_size))
                # input("PAUSED [%s/%s]: Opening tabs in chunks of %s. Press enter to open next chunk.\n" % (tabs_processed, total_tabs_to_process, chunk_size))
                input("\n[%s/%s] PAUSED: Opening tabs in chunks of %s. Press enter to open next chunk." % (tabs_processed, total_tabs_to_process, chunk_size))
        
        # Still count the tab as processed even if don't open it
        else:
            tabs_processed += 1
            print(".", end="", flush=True)

    # Print out that finished opening tabs and pause for user input to exit function
    print("\nFinished opening %s of %s tabs." % (tabs_opened, total_tabs_to_process))
    pause_before_exiting()




# MAIN
def main():
    try:
        handle_super_flags()
        load_config_data()
        handle_function_call()
        params = extract_params()
        populate_commander_url_files(suppress_prints=True)
        open_mtg_tab_exec_str = get_open_mtg_tabs_exec_str(params)
        exec(open_mtg_tab_exec_str)
    
    # Handle tool crashing
    except (Exception, KeyboardInterrupt) as e:
        # Print out error as it would look on a crash
        error_lines = traceback.format_exception(type(e), e, sys.exc_info()[2])
        for line in error_lines:
            sys.stderr.write(line)

        # Stop debugger here if in debug mode
        if debug_mode == True:
            pdb.set_trace()

        # Pause before exiting
        pause_before_exiting()


# Only launch 'main' if executed from command line
if __name__ == '__main__':
    main()

