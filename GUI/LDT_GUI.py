import tkinter as tk
import sys
import subprocess

def create_main_window():
    root = tk.Tk()
    root.title("Leakdown Tester GUI")
    
    ### GUI Elements ###
    ## Configure left-side UI panel:
    config_frame = tk.Frame(root)
    config_frame.pack(pady=10, side=tk.LEFT)

    ## Dropdown menu for selecting API target
    target_label = tk.Label(config_frame, text="API Target:")
    target_label.pack()

    targets = ['Local', 'Heroku', 'GCP']
    target_var = tk.StringVar(root)
    target_var.set(targets[0])  # Set default test to Local API target
    target_dropdown = tk.OptionMenu(config_frame, target_var, *targets)
    target_dropdown.pack()

    ## Dropdown menu for setting test number
    test_num_label = tk.Label(config_frame, text="Tests to run:")
    test_num_label.pack()
    test_num_entry = tk.Entry(config_frame)
    test_num_entry.pack()
    
    ## Dropdown menu for setting thread count
    thread_label = tk.Label(config_frame, text="Threads to open:")
    thread_label.pack()
    thread_entry = tk.Entry(config_frame)
    thread_entry.pack()

    ## Dropdown menu to select test behavior type
    test_type_label = tk.Label(config_frame, text="Test Category:")
    test_type_label.pack()
    
    test_types = ["CSV", "Persona", "Causal Pathway", "Custom Github Content"]
    test_type_var = tk.StringVar(root)
    test_type_var.set(test_types[0])  # Default selection
    test_type_dropdown = tk.OptionMenu(config_frame, test_type_var, *test_types, command=update_ui)
    test_type_dropdown.pack()

    ## Button to run configured LDT test
    run_button = tk.Button(root, text="Run Test", command=lambda: run_test(test_type_var.get()))
    run_button.pack(side=tk.LEFT)  # Place the button at the bottom
    
    # Log display section:
    log_text = tk.Text(root, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True)

    # Redirect print and log statements (stdout, stderr) to the Text widget:
    def redirect_output(output_widget):
        class StdoutRedirector:
            def __init__(self, widget):
                self.widget = widget

            def write(self, text):
                self.widget.insert(tk.END, text)

        sys.stdout = StdoutRedirector(log_text)
        sys.stderr = StdoutRedirector(log_text)

    redirect_output(log_text)

    # Placeholder for test-specific configuration widgets
    test_config_widgets = []


    root.mainloop()  # Starts tkinter main loop

def update_ui(selected_test_type):
    # Destroy existing test-specific configuration widgets
    for widget in test_config_widgets:
        widget.destroy()
    
    # Create and display test-specific configuration widgets based on the selected test type
    if selected_test_type == "CSV":
        # Create and display CSV-specific widgets
        initial_row_label = tk.Label(config_frame, text="Initial Row:")
        initial_row_label.pack()
        initial_row_entry = tk.Entry(config_frame)
        initial_row_entry.pack()
        final_row_label = tk.Label(config_frame, text="Final Row:")
        final_row_label.pack()
        final_row_entry = tk.Entry(config_frame)
        final_row_entry.pack()
        csv_path_label = tk.Label(config_frame, text="CSV Path:")
        csv_path_label.pack()
        csv_path_entry = tk.Entry(config_frame)
        csv_path_entry.pack()
        test_config_widgets.extend([initial_row_label, initial_row_entry, final_row_label, final_row_entry, csv_path_label, csv_path_entry])
    elif selected_test_type == "Persona":
        # Create and display Persona-specific widgets
        single_all_label = tk.Label(config_frame, text="Single or All:")
        single_all_label.pack()
        single_all_var = tk.StringVar(root)
        single_all_var.set("Single")  # Default selection
        single_all_dropdown = tk.OptionMenu(config_frame, single_all_var, "Single", "All")
        single_all_dropdown.pack()
        if single_all_var.get() == "Single":
            # Create and display persona options based on single selection
            # Replace these with your actual persona options
            persona_options_label = tk.Label(config_frame, text="Select Persona:")
            persona_options_label.pack()
            persona_options_var = tk.StringVar(root)
            persona_options_var.set("Persona 1")  # Default selection
            persona_options_dropdown = tk.OptionMenu(config_frame, persona_options_var, "Persona 1", "Persona 2", "Persona 3")
            persona_options_dropdown.pack()
        test_config_widgets.extend([single_all_label, single_all_dropdown, persona_options_label, persona_options_dropdown])
    elif selected_test_type == "Causal Pathway":
        # Create and display Causal Pathway-specific widgets
        all_cp_label = tk.Label(config_frame, text="All Causal Pathways:")
        all_cp_label.pack()
        all_cp_var = tk.StringVar(root)
        all_cp_var.set("Yes")  # Default selection
        all_cp_dropdown = tk.OptionMenu(config_frame, all_cp_var, "Yes", "No")
        all_cp_dropdown.pack()
        if all_cp_var.get() == "No":
            # Create and display options for running a single CP
            # Replace these with your actual CP options
            single_cp_label = tk.Label(config_frame, text="Select Causal Pathway:")
            single_cp_label.pack()
            single_cp_var = tk.StringVar(root)
            single_cp_var.set("CP 1")  # Default selection
            single_cp_dropdown = tk.OptionMenu(config_frame, single_cp_var, "CP 1", "CP 2", "CP 3")
            single_cp_dropdown.pack()
        test_config_widgets.extend([all_cp_label, all_cp_dropdown, single_cp_label, single_cp_dropdown])

def run_test(selected_test_type):
    # Define the command to run LDT.py based on the selected test type
    full_command = ["python3.11", 'LDT.py', ]   # Set up initial command to run LDT

    if selected_test_type == "CSV":
        cmd = ["python", "LDT.py", "--csv"]
    elif selected_test_type == "Persona":
        cmd = ["python", "LDT.py", "--persona"]
    elif selected_test_type == "Causal Pathway":
        cmd = ["python", "LDT.py", "--causal"]
    elif selected_test_type == "Custom Github Content":
        cmd = ["python", "LDT.py", "--github"]
    else:
        print("Invalid test type selected.")
        return
    
    try:
        # Run the command and capture the output
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        print(output)
    except subprocess.CalledProcessError as e:
        print("Error:", e.output)

if __name__ == "__main__":
    create_main_window()