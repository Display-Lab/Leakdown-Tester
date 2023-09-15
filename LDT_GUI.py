import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import PhotoImage
import sys
import os
import subprocess
import threading

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

# # # Main UI window # # #
def create_main_window():
    global icon1024_path, icon128_path
    root = tk.Tk()
    root.title("Leakdown Tester GUI")
    root.geometry("1240x800")
    
    ## Widget styling global options
    style = ttk.Style()
    style.configure("main.TLabel",
        foreground = "#9b9a9c",
        background = "#480e7b",
        font=("Helvetica", 16)
    )
    style.configure("main.TButton",
        #padding=    (2,8),
        relief=     'raised'
    )
    style.configure('main.TCheckbutton',
        font=('Helvetica', 14)
    )
    style.configure('=disabled.TButton',
        background = 'black',
        foreground = 'white',
        relief=     'raised'
        )

    # Call photoimage from root, avoids tkinter garbage collection errors
    icon1024 = PhotoImage(file=icon1024_path)
    lin_icon = icon1024.subsample(32)

    # Platform specific icon setting; WIP
    if sys.platform == 'darwin':
        root.iconbitmap('Assets/icon_16x16.png')
    elif sys.platform == 'linux':
        root.iconbitmap(lin_icon)
    elif sys.platform == 'windows':
        root.iconbitmap('Assets/LeakdownTester.ico')
    

    # Create left-side main UI panel
    left_frame = ttk.Frame(root)
    left_frame.pack(pady=20, side=tk.LEFT)

    # Create right side configuration settings panel
    right_frame = ttk.Frame(root)
    right_frame.pack(pady=10, side=tk.RIGHT)    
    
    # # # # Left frame UI elements # # # # # # # # # # # # # # # # # # # #
    # LDT icon label
    icon128 = PhotoImage(file=icon128_path, master=left_frame)
    icon_label = ttk.Label(left_frame, image=icon128)
    icon_label.image=icon128
    
    # Test configuration buttons
    configure_general_button = ttk.Button(left_frame,
        text="Configure General Settings", 
        command=lambda: configure_test(right_frame, root, configure_general_button), 
        style='main.TButton')
    
    configure_csv_button = ttk.Button(left_frame,
        text="Configure CSV Test",
        command=lambda: configure_csv(right_frame, root, configure_csv_button),
        style='main.TButton')

    configure_persona_button = ttk.Button(left_frame,
        text="Configure Persona Test",
        command=lambda: configure_persona(right_frame, root, configure_persona_button),
        style='main.TButton')

    configure_causal_button = ttk.Button(left_frame,
        text="Configure Causal Pathway Test",
        command=lambda: configure_causal(right_frame, root, configure_causal_button),
        style='main.TButton')
    
    configure_github_button = ttk.Button(left_frame,
        text="Configure Custom GitHub Test",
        command=lambda: configure_github(right_frame, root, configure_github_button),
        style='main.TButton')

    # Dropdown menu to select test behavior type to run
    test_type_label = ttk.Label(left_frame, text="Test Type to Run:", style='main.TLabel')
    test_types = ["CSV", "Persona", "Causal Pathway", "Custom Github Content", "Custom JSON Payload"]
    test_type_var = tk.StringVar(root)
    test_type_var.set(test_types[1])  # Default selection is all persona test
    test_type_dropdown = tk.OptionMenu(left_frame, test_type_var, *test_types)

    # Button to run LDT test
    run_button = ttk.Button(left_frame, text="Run Test", command=lambda: run_test(test_type_var.get(), None, run_button))

    # Button to clear text from window
    clear_button = ttk.Button(left_frame, text='Clear window', command=lambda: log_text.delete("1.0", "end"))
    

    ## Pack widgets in order and configure spacing
    icon_label.pack(anchor = tk.N)
    configure_general_button.pack(pady=15)
    ttk.Separator(left_frame, orient="horizontal").pack(fill='x', pady=8)

    configure_csv_button.pack(fill=tk.X)
    configure_persona_button.pack(fill=tk.X)
    configure_causal_button.pack(fill=tk.X)
    configure_github_button.pack(fill=tk.X)

    ttk.Separator(left_frame, orient="horizontal").pack(fill='x', pady=8)
    test_type_label.pack()
    test_type_dropdown.pack(pady=3)
    ttk.Separator(left_frame, orient="horizontal").pack(fill='x', pady=8)    
    run_button.pack(pady=2)
    clear_button.pack(pady=2)
    
    
    # # # # # # # # # # # # # 
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

        sys.stdout = StdoutRedirector(log_text)     # redirect output
        sys.stderr = StdoutRedirector(log_text)     # redirect errors
    redirect_output(log_text)

    # Confirm when user attempts to close the program
    def on_closing():
        if messagebox.askokcancel("Quit", "Close the GUI?"):
            root.destroy()
            sys.exit(0)
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Set the close button event handler
    
    # Start Tkinter main loop
    root.mainloop()



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Right-side panel configuration settings

### Create general test configuration options
def configure_test(frame, root, this_button):
    this_button.configure(style='disabled.TButton')       # Disable config button while menu is open
    clean_slate(frame)

    ## Dropdown menu for selecting API target
    ttk.Label(frame, text="API Target:", style='main.TLabel').pack(pady=3)   # Label and packing
    targets = ['Local', 'Heroku', 'Cloud']
    target_var = tk.StringVar(root)
    target_var.set(targets[0])  # Set default test to Local API target
    target_dropdown = ttk.OptionMenu(frame, target_var, *targets).pack(ipadx=4, ipady=5)    # Option select + pack
    
    ttk.Separator(frame, orient="horizontal").pack(fill='x', pady=8)


    ## Spinbox for setting number of tests to run
    ttk.Label(frame, text="Tests requested:", style='main.TLabel').pack(pady=2)
    tests_asked = tk.IntVar(value=num_tests)
    test_num_spinbox = ttk.Spinbox(frame, from_=1, to=1000, textvariable=tests_asked)
    test_num_spinbox.pack()


    ## Spinbox for setting number of threads to run tests on
    ttk.Label(frame, text="Threads to open:", style='main.TLabel').pack(pady=2)
    threads_asked = tk.IntVar(value=num_threads)
    thread_spinbox = ttk.Spinbox(frame, from_=1, to=100, textvariable=threads_asked)
    thread_spinbox.pack()

    ttk.Separator(frame, orient="horizontal").pack(fill='x', pady=18)


    ## Checkbox for showing detailed API response
    response_var = tk.BooleanVar(root, value=respond)
    response_checkbox = ttk.Checkbutton(frame,
    text=       "Show detailed API response?",
    variable=   response_var,
    style=      'main.TCheckbutton'
    )
    response_checkbox.pack(anchor=tk.W, padx=5, pady=2)
    
    ## Checkbox for enabling debug mode
    debug_var = tk.BooleanVar(root, value=debug)
    debug_checkbox = ttk.Checkbutton(frame,
    text=       "Run in debug mode?",
    variable=   debug_var,
    style=      "main.TCheckbutton"
    )
    debug_checkbox.pack(anchor=tk.W, padx=5, pady=2)

    # Create save button to store settings to pass to run_test
    def save_general_config():
        global target, num_tests, num_threads, respond, debug
        target =        str(target_var.get())
        target =        target.lower()
        num_tests =     int(test_num_spinbox.get())
        num_threads =   int(thread_spinbox.get())
        respond =       response_var.get()
        debug =         debug_var.get()
        print("General configurations saved")
        clean_slate(frame)
        this_button.configure(style='main.TButton')       # revert button state

    ttk.Button(frame, text="Save Configuration", command=save_general_config).pack(anchor=tk.S, pady=20)



### Create CSV test configuration options
def configure_csv(frame, root, this_button):
    this_button.configure(style='disabled.TButton')   # Disable config button while menu is open
    clean_slate(frame)

    # Spinbox for setting initial CSV row to read
    ri_set_label = ttk.Label(frame, text="First row read:", style='main.TLabel').pack()
    ri_dummy = tk.IntVar(value=initial_row)
    ri_set_spinbox = ttk.Spinbox(frame, from_=0, to=500, textvariable=ri_dummy)
    ri_set_spinbox.pack()
    
    # Spinbox for setting final CSV row to read
    rf_set_label = ttk.Label(frame, text="Last row read:", style='main.TLabel').pack()
    rf_dummy = tk.IntVar(value=final_row)
    rf_set_spinbox = ttk.Spinbox(frame, from_=1, to=500, textvariable=rf_dummy)
    rf_set_spinbox.pack()

    # Create file browser window to choose CSV filepath
    def open_file_browser():
        global csv_filepath
        pathing = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if pathing:
            csv_filepath = f"{pathing}"             # Update filepath
            print("CSV Filepath:", csv_filepath)    # Print path to verify

    ttk.Button(frame, text="Select CSV File", command=open_file_browser).pack(pady=10)


    # Create save button to store settings to pass to run_test
    def save_csv_config():
        global initial_row, final_row
        initial_row = int(ri_set_spinbox.get())  # Get the value from the Spinbox
        final_row = int(rf_set_spinbox.get())    # Get the value from the Spinbox
        print("CSV configurations saved")
        clean_slate(frame)
        this_button.configure(style='main.TButton')       # revert button state

    ttk.Button(frame, text="Save Configuration", command=save_csv_config).pack(anchor=tk.S, pady=12)



### Create persona test configuration options
def configure_persona(frame, root, this_button):
    this_button.configure(style='disabled.TButton')   # Disable config button while menu is open
    clean_slate(frame)

    # Dropdown menu for selecting persona to test
    ttk.Label(frame, text="Persona to test:", style='main.TLabel').pack(pady=4)
    test_persona = ['All', 'Alice', 'Bob', 'Chikondi', 'Deepa', 'Eugene', 'Fahad', 'Gaile']
    test_persona_var = tk.StringVar(root)
    test_persona_var.set(test_persona[0])  # Set default test to test all personas
    test_persona_dropdown = ttk.OptionMenu(frame, test_persona_var, *test_persona)
    test_persona_dropdown.pack(ipadx=4, ipady=2, pady=6)
        
    # Checkbox for verifying output against vignette
    verify_var = tk.BooleanVar(root, value=verify_persona)
    verify_checkbox = ttk.Checkbutton(frame,
    text=       "Verify output against vignette?",
    variable=   verify_var,
    style=      'main.TCheckbutton'
    )
    verify_checkbox.pack(anchor=tk.W, padx=5, pady=20)

    # Create save button to store settings to pass to run_test
    def save_pers_config():
        global persona, verify_persona
        persona = str(test_persona_var.get())
        persona = persona.lower()
        verify_persona = bool(verify_var.get())
        print("Persona configurations saved")
        clean_slate(frame)
        this_button.configure(style='main.TButton')       # revert button state

    ttk.Button(frame, text="Save Configuration", command=save_pers_config).pack(anchor=tk.S, pady=20)



## Create causal pathway configuration options
def configure_causal(frame, root, this_button):
    this_button.configure(style='disabled.TButton')   # Disable config button while menu is open
    clean_slate(frame)

    # Dropdown menu for selecting persona to test
    ttk.Label(frame, text="Causal Pathway to test:", style='main.TLabel').pack(pady=4)
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
    test_cp_dropdown = ttk.OptionMenu(frame, test_cp_var, *test_cp)
    test_cp_dropdown.pack(pady=4)
        
    # Checkbox for verifying output against vignette data
    verify_var = tk.BooleanVar(root, value=verify_cp)
    verify_checkbox = ttk.Checkbutton(frame,
    text=       "Automatically verify output?",
    variable=   verify_var,
    style=      'main.TCheckbutton'
    )
    verify_checkbox.pack(anchor=tk.W, padx=5, pady=20)

    # Create save button to store settings to pass to run_test
    def save_cp_config():
        global causal_path, verify_cp
        causal_path = str(test_cp_var.get())
        causal_path = causal_path.lower()
        causal_path = causal_path.replace(' ', '_')
        verify_cp = bool(verify_var.get())
        print("Causal pathway configurations saved")
        clean_slate(frame)
        this_button.configure(style='main.TButton')       # revert button state

    ttk.Button(frame, text="Save Configuration", command=save_cp_config).pack(anchor=tk.S, pady=20)



## Create custom github content configuration options
def configure_github(frame, root, this_button):
    this_button.configure(style='disabled.TButton')   # Disable config button while menu is open
    clean_slate(frame)

    # GitHub link entry field
    ttk.Label(frame, text="Paste GitHub link below:", style='main.TLabel').pack(pady=10)
    github_link_entry = ttk.Entry(frame)
    github_link_entry.pack(pady=10)

    # Button to save configuration
    def save_git_config():
        global git_link
        git_link = github_link_entry.get()
        print("GitHub Link: ", github_link)  # Readback for user verification
        clean_slate(frame)
        this_button.configure(style='main.TButton')       # revert button state

    ttk.Button(frame, text="Save Configuration", command=save_git_config).pack(anchor=tk.S, pady=20)


# Clear any configuration widgets from a frame
def clean_slate(frame):
    for widget in frame.winfo_children():
        widget.destroy()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## Test running control logic, interface GUI with CLI
def run_test(selected_test_type, indicator, this_button):
    this_button.config(state=tk.DISABLED)    # Disable run button while already running a test
    this_button.configure(style='disabled.TButton')

    print(f"Running Leakdown Test from Graphical Interface")
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
    

    # Make subprocess-only function for running in parallel thread
    def run_in_thread(full_command, indicator, this_button):
        try:
            #indicator.start([10])
            output = subprocess.check_output(full_command, stderr=subprocess.STDOUT, text=True)
            print(output)

        except subprocess.CalledProcessError as e:
            print("Error:", e.output)
        
        finally:
            #indicator.stop()
            this_button.config(state=tk.NORMAL)
    
    # Run subprocess in thread
    test_thread = threading.Thread(target=run_in_thread(cmd, indicator, this_button))
    test_thread.start()


if __name__ == "__main__":
    create_main_window()
    exit(0)
