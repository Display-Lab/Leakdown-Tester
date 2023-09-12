import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import PhotoImage
import sys
import os
import subprocess


## Initialize test config vars in global scope
global target, num_tests, num_threads, respond, debug, csv_filepath, initial_row, final_row, persona, causal_path, verify_persona, verify_cp, git_link
target =            'local'
num_tests =         1
num_threads =       1
respond =           False
debug =             False

csv_filepath =      None
initial_row =       0
final_row =         12

persona =           None
verify_persona =    False

causal_path =       None
verify_cp =         False

git_link =          None

## Image pathing and setup
this_dir = os.path.dirname(__file__)
icon1024_path = os.path.join(this_dir, "Assets/icon_1024x1024.png")
icon128_path = os.path.join(this_dir, "Assets/icon_128x128.png")

### Main UI window ###
def create_main_window():
    global icon1024_path, icon128_path
    root = tk.Tk()
    root.title("Leakdown Tester GUI")
    
    ## Widget styling global options
    style = ttk.Style()
    style.configure("label1",
                foreground="9b9a9c",
                backgroud ="480e7b",
                font=("consolas", 12)
                )
    # Call photoimage from inside main, avoids tkinter garbage collection errors
    icon1024 = PhotoImage(file=icon1024_path)
    lin_icon = icon1024.subsample(32)

    if sys.platform == 'darwin':
        root.iconbitmap('Assets/icon_32x32.png')
    elif sys.platform == 'linux':
        root.iconbitmap(lin_icon)
    elif sys.platform == 'windows':
        root.iconbitmap('Assets/LeakdownTester.ico')
    

    # Create left-side main UI panel
    left_frame = tk.Frame(root)
    left_frame.pack(pady=10, side=tk.LEFT)

    # Create right side configuration settings panel
    right_frame = tk.Frame(root)
    right_frame.pack(pady=10, side=tk.RIGHT)    
    
    # # # # Left frame UI elements # # # # # # # # # 
    # LDT icon label
    icon128 = PhotoImage(file=icon128_path, master=left_frame)
    icon_label = tk.Label(left_frame, image=icon128)
    icon_label.image=icon128
    icon_label.pack(side='top')

    # Test configuration buttons
    configure_general_button = tk.Button(left_frame, text="Configure General Settings",
                                        command=lambda: configure_test(right_frame, root))
    configure_general_button.pack()

    configure_csv_button = tk.Button(left_frame, text="Configure CSV Test", command=lambda: configure_csv(right_frame, root))
    configure_csv_button.pack()

    configure_persona_button = tk.Button(left_frame, text="Configure Persona Test", command=lambda: configure_persona(right_frame, root))
    configure_persona_button.pack()

    configure_causal_button = tk.Button(left_frame, text="Configure Causal Pathway Test", command=lambda: configure_causal(right_frame, root))
    configure_causal_button.pack()

    configure_github_button = tk.Button(left_frame, text="Configure Custom GitHub Test", command=lambda: configure_github(right_frame, root))
    configure_github_button.pack()

    # Dropdown menu to select test behavior type to run
    test_type_label = tk.Label(left_frame, text="Test Type to Run:")
    test_type_label.pack()
    test_types = ["CSV", "Persona", "Causal Pathway", "Custom Github Content", "Custom JSON Payload"]
    test_type_var = tk.StringVar(root)
    test_type_var.set(test_types[4])  # Default selection is Postwoman
    test_type_dropdown = tk.OptionMenu(left_frame, test_type_var, *test_types)
    test_type_dropdown.pack()

    # Button to run LDT test
    run_button = tk.Button(left_frame, text="Run Test", command=lambda: run_test(test_type_var.get()))
    run_button.pack()

    # Button to clear text from window
    clear_button = tk.Button(left_frame, text='Clear window', command=lambda: log_text.delete("1.0", "end"))
    clear_button.pack()

    # Log display section:
    log_text = tk.Text(root, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True)

    # Redirect print and log statements (stdout, stderr) to log_text widget
    def redirect_output(output_widget):
        class StdoutRedirector:
            def __init__(self, widget):
                self.widget = widget

            def write(self, text):
                self.widget.insert(tk.END, text)

        sys.stdout = StdoutRedirector(log_text)
        sys.stderr = StdoutRedirector(log_text)

    redirect_output(log_text)


    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)  # Set the close button event handler
    root.mainloop()  # Starts tkinter main loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

### Create general test configuration options
def configure_test(frame, root):

    # Clear any previous configuration widgets from the config frame
    for widget in frame.winfo_children():
        widget.destroy()

    ## Dropdown menu for selecting API target
    target_label = tk.Label(frame, text="API Target:")
    target_label.pack()
    targets = ['Local', 'Heroku', 'Cloud']
    target_var = tk.StringVar(root)
    target_var.set(targets[0])  # Set default test to Local API target
    target_dropdown = tk.OptionMenu(frame, target_var, *targets)
    target_dropdown.pack()

    ## Spinbox for setting number of tests to run
    test_num_label = tk.Label(frame, text="Tests requested:")
    test_num_label.pack()
    test_num_spinbox = tk.Spinbox(frame, from_=1, to=1000)
    test_num_spinbox.pack()

    ## Spinbox for setting number of threads to run tests on
    thread_label = tk.Label(frame, text="Threads to open:")
    thread_label.pack()
    thread_spinbox = tk.Spinbox(frame, from_=1, to=100)
    thread_spinbox.pack()

    ## Dropdown menu for enabling detailed response
    respond_label = tk.Label(frame, text="Show detailed API response?")
    respond_label.pack()
    respond_opt = [False, True]
    response_var = tk.BooleanVar(root)
    response_var.set(respond_opt[0])
    response_dropdown = tk.OptionMenu(frame, response_var, *respond_opt)
    response_dropdown.pack()

    ## Dropdown menu for enabling debug mode
    debug_label = tk.Label(frame, text="Run in debug mode?")
    debug_label.pack()
    debug_opt = [False, True]
    debug_var = tk.BooleanVar(root)
    debug_var.set(debug_opt[0])
    debug_dropdown = tk.OptionMenu(frame, debug_var, *debug_opt)
    debug_dropdown.pack()

    # Create save button to store settings to pass to run_test
    def save_general_config():
        global target, num_tests, num_threads, respond, debug
        target =        str(target_var.get())
        target =        target.lower()
        num_tests =     int(test_num_spinbox.get())
        num_threads =   int(thread_spinbox.get())
        respond =       response_var.get()
        debug =         debug_var.get()
        
        # Remove configuration widgets
        for widget in frame.winfo_children():
            widget.destroy()

    save_button = tk.Button(frame, text="Save Configuration", command=save_general_config)
    save_button.pack()


### Create CSV test configuration options
def configure_csv(frame, root):

    # Clear any previous configuration widgets from the config frame
    for widget in frame.winfo_children():
        widget.destroy()


    # Spinbox for setting initial CSV row to read
    ri_set_label = tk.Label(frame, text="First row read:")
    ri_set_label.pack()
    ri_set_spinbox = tk.Spinbox(frame, from_=0, to=500, value=initial_row)
    ri_set_spinbox.pack()
    
    # Spinbox for setting final CSV row to read
    rf_set_label = tk.Label(frame, text="Last row read:")
    rf_set_label.pack()
    rf_set_spinbox = tk.Spinbox(frame, from_=1, to=500, value=final_row)
    rf_set_spinbox.pack()

    # Create file browser window to choose CSV filepath
    def open_file_browser():
        global csv_filepath
        pathing = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if pathing:
            csv_filepath = f"{pathing}"             # Update filepath
            print("CSV Filepath:", csv_filepath)    # Print path to verify

    browse_button = tk.Button(frame, text="Select CSV File", command=open_file_browser)
    browse_button.pack()


    # Create save button to store settings to pass to run_test
    def save_csv_config():
        global initial_row, final_row
        initial_row = int(ri_set_spinbox.get())  # Get the value from the Spinbox
        final_row = int(rf_set_spinbox.get())    # Get the value from the Spinbox
        
        # Remove configuration widgets
        for widget in frame.winfo_children():
            widget.destroy()

    save_button = tk.Button(frame, text="Save Configuration", command=save_csv_config)
    save_button.pack()



### Create persona test configuration options
def configure_persona(frame, root):

    # Clear any previous configuration widgets from the config frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Dropdown menu for selecting persona to test
    test_type_label = tk.Label(frame, text="Persona to test:")
    test_type_label.pack()
    test_persona = ['All', 'Alice', 'Bob', 'Chikondi', 'Deepa', 'Eugene', 'Fahad', 'Gaile']
    test_persona_var = tk.StringVar(root)
    test_persona_var.set(test_persona[0])  # Set default test to test all personas
    test_persona_dropdown = tk.OptionMenu(frame, test_persona_var, *test_persona)
    test_persona_dropdown.pack()
        
    # Dropdown for verifying output against vignette data
    verify_label = tk.Label(frame, text="Verify output against vignette data?")
    verify_label.pack()
    verify_opt = [False, True]
    verify_var = tk.BooleanVar(root)
    verify_var.set(verify_opt[0])
    verify_dropdown = tk.OptionMenu(frame, verify_var, *verify_opt)
    verify_dropdown.pack()

    # Create save button to store settings to pass to run_test
    def save_pers_config():
        global persona, verify_persona
        persona = str(test_persona_var.get())
        persona = persona.lower()
        verify_persona = bool(verify_var.get())
        
        # Remove configuration widgets
        for widget in frame.winfo_children():
            widget.destroy()

    save_button = tk.Button(frame, text="Save Configuration", command=save_pers_config)
    save_button.pack()



## Create causal pathway configuration options
def configure_causal(frame, root):
    # Clear any previous configuration widgets from the config frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Dropdown menu for selecting persona to test
    test_type_label = tk.Label(frame, text="Causal Pathway to test:")
    test_type_label.pack()
    test_cp = ['All',
    "Goal Approach",
    "Goal Gain",
    "Goal Loss",
    "Improving",
    "Social Approach",
    "Social Better",
    "Social Gain",
    "Social Loss",
    "Social Worse",
    "Worsening"
]
    test_cp_var = tk.StringVar(root)
    test_cp_var.set(test_cp[0])  # Set default test to test all cps
    test_cp_dropdown = tk.OptionMenu(frame, test_cp_var, *test_cp)
    test_cp_dropdown.pack()
        
    # Dropdown for verifying output against vignette data
    verify_label = tk.Label(frame, text="Automatically verify output?")
    verify_label.pack()
    verify_opt = [False, True]
    verify_var = tk.BooleanVar(root)
    verify_var.set(verify_opt[0])
    verify_dropdown = tk.OptionMenu(frame, verify_var, *verify_opt)
    verify_dropdown.pack()

    # Create save button to store settings to pass to run_test
    def save_cp_config():
        global causal_path, verify_cp
        causal_path = str(test_cp_var.get())
        causal_path = causal_path.lower()
        causal_path = causal_path.replace(' ', '_')
        verify_cp = bool(verify_var.get())
        
        # Remove configuration widgets
        for widget in frame.winfo_children():
            widget.destroy()

    save_button = tk.Button(frame, text="Save Configuration", command=save_cp_config)
    save_button.pack()


## Create custom github content configuration options
def configure_github(frame, root):
    # Clear any previous configuration widgets from the config frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Label for the GitHub link entry
    github_link_label = tk.Label(frame, text="Paste GitHub link below:")
    github_link_label.pack()

    # Entry field for the GitHub link
    github_link_entry = tk.Entry(frame)
    github_link_entry.pack()

    # Button to save configuration
    def save_git_config():
        global git_link
        git_link = github_link_entry.get()
        print("GitHub Link:", github_link)  # Readback for user verification

        # Remove configuration widgets
        for widget in frame.winfo_children():
            widget.destroy()

    save_button = tk.Button(frame, text="Save Configuration", command=save_git_config)
    save_button.pack()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## Test running control logic, interface GUI with CLI
def run_test(selected_test_type):
    cmd = ["python", 'LDT.py']   # Set up initial command to run LDT
    cmd.extend(['--target', str(target)])
    cmd.extend(['--tests', str(num_tests)])
    cmd.extend(['--threads', str(num_threads)])
    if debug:
        cmd.extend(['--debug'])
    if respond:
        cmd.extend(['--respond'])

    if selected_test_type == "Custom JSON Content":
        cmd.extend(['--postwoman'])

    elif selected_test_type == "CSV":
        cmd.extend(['--RI', str(initial_row), '--RF', str(final_row)])
        if csv_filepath is not None:
            cmd.extend(['--csv', csv_filepath])

    elif selected_test_type == "Persona":
        if persona == 'all':
            cmd.append('--allPersonas')
        else:
            cmd.extend(['--persona', persona])
        if verify_persona:
            cmd.append('--vignVerify')
    
    elif selected_test_type == "Causal Pathway":
        if causal_path == 'All':
            cmd.append('--allCPs')
        else:
            cmd.extend(['--CP', causal_path])
        if verify_cp:
            cmd.append('--cpVerify')
        
    elif selected_test_type == "Custom Github Content":
        cmd.extend(['--useGit', git_link])
    

    try:
        # Run the command and capture the output
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        print(output)
    except subprocess.CalledProcessError as e:
        print("Error:", e.output)


if __name__ == "__main__":
    create_main_window()
    exit(0)
