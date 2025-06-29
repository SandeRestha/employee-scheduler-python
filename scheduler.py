import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import random
import csv
from collections import defaultdict

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHIFTS = ["Morning", "Afternoon", "Evening"]

class SchedulerApp:
    MAX_EMPLOYEES_PER_SHIFT = 2 # Max employees allowed per shift for any given shift on any day
    MAX_WORKDAYS_PER_WEEK = 5 # Max days an employee can work in a week

    def __init__(self, root):
        """
        Initializes the Employee Shift Scheduler application.
        Sets up the main window, appearance mode, and core data structures.
        Aesthetics: Sets root window background and overall theme.
        """
        ctk.set_appearance_mode("light") # Set the overall appearance to light mode
        ctk.set_default_color_theme("blue") # Set the default color theme
        
        self.root = root
        self.root.title("Employee Shift Scheduler") # Set the window title
        self.root.geometry("850x850") # Adjusted initial window size to make the gap less in the middle
        
        # Aesthetic change: Set a softer background color for the main window
        self.root.configure(fg_color="#E8E8E8") # Light grey background for the root window
        
        self.employees = [] # List to store employee data: [(name, {day: {shift: priority}})]

        # Main frame to contain all UI elements
        # Aesthetic: Added padding to push content away from window edges
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(padx=30, pady=30, fill="both", expand=True) # Increased padding

        self.build_input_frame()  # Call method to set up the employee input UI
        
        # defaultdict for storing the final schedule: schedule[day][shift] = [employee1, employee2, ...]
        self.schedule = defaultdict(lambda: defaultdict(list))
        
        # defaultdict to keep track of total workdays assigned to each employee
        self.workdays = defaultdict(int)

    def build_input_frame(self):
        """
        Sets up the GUI components for collecting employee names and shift preferences.
        Includes input fields, dropdowns for days and shifts, and buttons for actions.
        Aesthetics: Applied consistent corner_radius, adjusted colors and spacing for a cleaner look.
        """
        frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#F8F8F8") # Slightly lighter frame background
        frame.pack(fill="x", pady=15, padx=15) # Increased padding for the main input frame

        # Employee Name Input
        top_row = ctk.CTkFrame(frame, fg_color="transparent") # Transparent to blend with parent frame
        top_row.pack(fill="x", pady=10, padx=10) # Added padding
        ctk.CTkLabel(top_row, text="Name:", width=100, font=("Helvetica", 13, "bold")).pack(side="left", padx=(0, 10)) # Increased font size, added padx
        self.name_entry = ctk.CTkEntry(top_row, corner_radius=8, font=("Helvetica", 12)) # Consistent corner_radius, font
        self.name_entry.pack(side="left", fill="x", expand=True)

        # Dictionary to store references to priority StringVar objects for each shift per day
        # Structure: self.shift_priority_vars[day][shift] = StringVar_object
        self.shift_priority_vars = defaultdict(dict) 

        # Frame to hold the main content: left column for day/shift/priority, right for legend
        content_frame = ctk.CTkFrame(frame, fg_color="transparent") # Transparent to blend
        # Increased pady on content_frame to ensure space at the bottom for rounded corners
        content_frame.pack(fill="x", expand=True, pady=(10, 20)) # Increased bottom pady here

        # Container for preference input rows (no scrolling)
        # Increased corner_radius and explicit padding to ensure rounded corners are visible
        self.preference_input_container = ctk.CTkFrame(content_frame, corner_radius=15, fg_color="#F0F0F0") # Main grey background for preferences
        self.preference_input_container.pack(side="left", fill="x", padx=(15, 15), pady=15) # Increased padx and pady here

        # Headers for Day, Morning, Afternoon, Evening (with priorities)
        headers = ctk.CTkFrame(self.preference_input_container, fg_color="transparent") # Transparent header frame
        headers.pack(fill="x", pady=(8, 5)) # Increased pady for header spacing
        ctk.CTkLabel(headers, text="Day", width=80, anchor="w", font=("Helvetica", 12, "bold")).pack(side="left", padx=(10,5)) # Adjusted padx
        # Adjusted width and padx for increased gaps and centering
        ctk.CTkLabel(headers, text="Morning Priority", width=110, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=(15,15)) # Increased left and right padx
        ctk.CTkLabel(headers, text="Afternoon Priority", width=110, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=(15,15)) # Increased left and right padx
        ctk.CTkLabel(headers, text="Evening Priority", width=110, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=(15,15)) # Increased left and right padx


        # Right column for Priority Legend
        # Increased corner_radius and explicit padding to ensure rounded corners are visible
        right_column = ctk.CTkFrame(content_frame, corner_radius=15, fg_color="#F0F0F0") # Consistent background color
        right_column.pack(side="right", padx=20, anchor="n", pady=15) # Increased padx for more width
        # Aesthetic fix: Increased font size for title
        ctk.CTkLabel(right_column, text="Priority Legend", font=("Helvetica", 14, "bold"), anchor="center").pack(pady=10) 
        # Aesthetic fix: Increased font size, adjusted padx and pady for entries, increased wraplength
        ctk.CTkLabel(right_column, text="1 - Highest Preference", font=("Helvetica", 12), wraplength=150).pack(anchor="w", padx=25, pady=4) 
        ctk.CTkLabel(right_column, text="2 - Medium Preference", font=("Helvetica", 12), wraplength=150).pack(anchor="w", padx=25, pady=4)
        # Aesthetic fix: Corrected typo (from "1" to "3") and added explicit newline and justify for multi-line entry, increased wraplength
        ctk.CTkLabel(right_column, text="3 - Lowest Preference\n(Assigned if no other option)", font=("Helvetica", 12), justify="left", wraplength=150).pack(anchor="w", padx=25, pady=4)


        for day in DAYS:
            row = ctk.CTkFrame(self.preference_input_container, fg_color="transparent") # Transparent row frames
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=day, width=80, anchor="w", font=("Helvetica", 12)).pack(side="left", padx=(10, 5)) # Adjusted padx, font size

            for shift in SHIFTS:
                priority = ctk.StringVar(value="1") # Default priority to 1 for each shift
                dropdown = ctk.CTkOptionMenu(row, variable=priority, values=["1", "2", "3"], 
                                             fg_color="white", button_color="#6495ED", # DodgerBlue (slightly softer blue)
                                             button_hover_color="#5580C2", # Darker DodgerBlue for hover
                                             text_color="black", 
                                             width=110, corner_radius=8, font=("Helvetica", 12)) # Consistent corner_radius, font
                # Adjusted padx for increased gaps between priority dropdowns to align with headers
                dropdown.pack(side="left", padx=(15, 15)) # Increased padx for spacing
                self.shift_priority_vars[day][shift] = priority # Store StringVar in nested dict

        # Buttons for Add Employee and Edit/Remove Employees
        # Aesthetic: Consistent corner_radius and slightly adjusted colors for general buttons
        ctk.CTkButton(frame, text="Add Employee", command=self.add_employee, font=("Helvetica", 13, "bold"), 
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(pady=15) # SteelBlue
        ctk.CTkButton(frame, text="Edit/Remove Employees", command=self.edit_employees, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(pady=(0, 15))

        # Buttons for Generate Schedule and Export Schedule
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent") # Transparent button frame to blend
        button_frame.pack(pady=10)
        # Apply custom "shader" colors to "Generate Schedule" button
        ctk.CTkButton(button_frame, text="Generate Schedule", command=self.generate_schedule, font=("Arial", 14, "bold"),
                      fg_color="#3683D9",  # A slightly darker blue
                      hover_color="#2A6BAB", # A darker blue for hover
                      corner_radius=10, height=40).pack(pady=(0, 10)) # Consistent corner_radius, increased height
        # Apply custom "shader" colors to "Export Schedule" button
        ctk.CTkButton(button_frame, text="Export Schedule", command=self.export_schedule, font=("Arial", 14, "bold"),
                      fg_color="#3683D9",  # A slightly darker blue
                      hover_color="#2A6BAB", # A darker blue for hover
                      corner_radius=10, height=40).pack(pady=(10, 0)) # Consistent corner_radius, increased height

    def add_employee(self):
        """
        Collects employee name and preferences from the UI and adds them to the employees list.
        Performs basic validation (e.g., name is required, no duplicates) and provides user feedback.
        """
        name = self.name_entry.get().strip() # Get and strip whitespace from the name
        if not name:
            messagebox.showerror("Input Error", "Employee name is required.")
            return
        
        # Check for duplicate employee names (case-insensitive)
        if any(emp_name.lower() == name.lower() for emp_name, _ in self.employees):
            messagebox.showerror("Duplicate Error", f"Employee '{name}' already exists. Please use a unique name.")
            return

        # Collect preferences for all days and all shifts per day
        # The structure of prefs will be: {day: {shift: priority_string}}
        prefs = {day: {shift: self.shift_priority_vars[day][shift].get() for shift in SHIFTS} for day in DAYS}
        self.employees.append((name, prefs)) # Add the new employee to the list
        
        self.name_entry.delete(0, 'end') # Clear the name entry field
        
        # Reset priority dropdowns to default values (1) for next employee input
        for day in DAYS:
            for shift in SHIFTS:
                self.shift_priority_vars[day][shift].set("1")
            
        messagebox.showinfo("Success", f"Employee '{name}' added successfully.")

    def generate_schedule(self):
        """
        Assigns employees to shifts for the week based on their per-shift preferences and availability.
        This algorithm attempts to fulfill high-priority requests first, then resolves conflicts
        by looking for alternative shifts on the same day, then the next day, and finally
        fills any remaining slots randomly.
        """
        if not self.employees:
            messagebox.showwarning("No Employees", "Please add employees before generating a schedule.")
            return

        self.schedule.clear() # Clear any previous schedule
        self.workdays.clear() # Reset workday counts for all employees
        
        # Initialize the schedule structure with empty lists for each day and shift
        for day in DAYS:
            for shift in SHIFTS:
                self.schedule[day][shift] = []

        # Create a mapping for day names to their indices for easy "next day" calculation
        day_indices = {day: i for i, day in enumerate(DAYS)}

        # Set to keep track of employees who could not be fully scheduled after all attempts
        # This will be used for final feedback to the user.
        final_unresolved_employees = set()

        # Phase 1: Assign based on employees' highest daily priorities.
        # This pass aims to fulfill the most important preferences first.
        # It iterates through each day and attempts to place employees based on their
        # best (lowest numerical) priority for any shift on that specific day.
        for day in DAYS:
            # Keep track of which employees have been assigned a shift on *this specific day*
            # to prevent multiple assignments on the same day.
            assigned_on_current_day_pass1 = set()
            
            # Create a list of employees sorted by their *best* priority for any shift on the current day.
            # This ensures employees with strong preferences for this day are considered first.
            employees_sorted_by_best_daily_priority = []
            for name, prefs in self.employees:
                # Find the lowest priority number (e.g., 1 for highest preference) this employee has for any shift on this day.
                min_priority_for_day = min(int(prefs[day][s]) for s in SHIFTS)
                employees_sorted_by_best_daily_priority.append((min_priority_for_day, name, prefs))
            
            # Sort the list so employees with priority '1' on this day come first, then '2', etc.
            employees_sorted_by_best_daily_priority.sort()

            for min_prio, name, prefs in employees_sorted_by_best_daily_priority:
                # Skip if employee has already reached max weekly shifts or is already assigned today.
                if self.workdays[name] >= self.MAX_WORKDAYS_PER_WEEK or name in assigned_on_current_day_pass1:
                    continue

                # Sort shifts for the current employee on the current day by their priority (1, 2, 3)
                # This ensures we try their most preferred shift for this day first.
                sorted_shifts_for_employee_on_day = sorted(SHIFTS, key=lambda s: int(prefs[day][s]))
                
                assigned_this_employee_for_day = False
                for target_shift in sorted_shifts_for_employee_on_day:
                    # Check if the target shift has capacity.
                    if len(self.schedule[day][target_shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                        self.schedule[day][target_shift].append(name) # Assign employee to the shift
                        self.workdays[name] += 1 # Increment their weekly workday count
                        assigned_on_current_day_pass1.add(name) # Mark as assigned for this day
                        assigned_this_employee_for_day = True
                        break # Employee assigned for this day, move to the next employee in the loop

        # Phase 2: Resolve remaining employees by attempting assignments on unassigned days,
        # including "next day" resolution if a preferred day is full.
        # This handles employees who still have fewer than MAX_WORKDAYS_PER_WEEK.
        for name, prefs in self.employees:
            # Continue trying to assign until employee reaches max shifts or no more options.
            while self.workdays[name] < self.MAX_WORKDAYS_PER_WEEK:
                assigned_in_this_loop_pass2 = False
                
                # Identify days where this employee is NOT currently assigned.
                available_days_for_employee = []
                for day_to_check in DAYS:
                    # Check if the employee is *not* assigned to any shift on `day_to_check`.
                    if not any(name in self.schedule[day_to_check][s] for s in SHIFTS):
                        available_days_for_employee.append(day_to_check)
                
                if not available_days_for_employee:
                    # No more available days for this employee to be assigned.
                    break 

                # Sort these available days by the employee's *best* priority for any shift on that day.
                # This makes us try to fill their highest-priority unassigned days first.
                available_days_for_employee.sort(key=lambda d: min(int(prefs[d][s]) for s in SHIFTS))

                # First, try to assign to one of the employee's preferred shifts on an `available_day_for_employee`.
                for target_day in available_days_for_employee:
                    # Sort shifts for `target_day` based on `name`'s preferences (priorities).
                    sorted_shifts_for_target_day = sorted(SHIFTS, key=lambda s: int(prefs[target_day][s]))
                    for target_shift in sorted_shifts_for_target_day:
                        if len(self.schedule[target_day][target_shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                            self.schedule[target_day][target_shift].append(name)
                            self.workdays[name] += 1
                            assigned_in_this_loop_pass2 = True
                            break # Employee assigned for this workday, break from shift loop
                    if assigned_in_this_loop_pass2:
                        break # Employee assigned for this target day, break from day loop
                
                if assigned_in_this_loop_pass2:
                    continue # Successfully assigned, continue to next iteration of while loop for this employee

                # If still not assigned after trying all available preferred days directly,
                # then attempt to assign to the *next consecutive day* if possible.
                assigned_on_next_day = False
                for original_day_candidate in available_days_for_employee: # Iterate through days where they originally had an unmet need
                    current_day_idx = day_indices[original_day_candidate]
                    next_day_idx = (current_day_idx + 1) % len(DAYS) # Calculate next calendar day
                    next_day = DAYS[next_day_idx]

                    # Check if employee is not already assigned on this `next_day`.
                    if not any(name in self.schedule[next_day][s] for s in SHIFTS):
                        # Sort shifts for `next_day` based on `name`'s preferences.
                        sorted_shifts_for_next_day = sorted(SHIFTS, key=lambda s: int(prefs[next_day][s]))
                        for next_day_shift in sorted_shifts_for_next_day:
                            # Check capacity for the next day's shift.
                            if len(self.schedule[next_day][next_day_shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                                self.schedule[next_day][next_day_shift].append(name)
                                self.workdays[name] += 1
                                assigned_on_next_day = True
                                assigned_in_this_loop_pass2 = True # Mark as assigned for this pass
                                break # Employee assigned on next day, break from shift loop
                    if assigned_on_next_day:
                        break # Employee placed on next day, break from original_day_candidate loop
                
                if not assigned_in_this_loop_pass2:
                    # If the employee could not be placed even after trying next day,
                    # add them to the final unresolved set and break from their while loop.
                    final_unresolved_employees.add(name)
                    break 

        # Phase 3: Fill Any Remaining Empty Slots Randomly.
        # This ensures that all shifts are filled up to `MAX_EMPLOYEES_PER_SHIFT` if there are
        # eligible employees who still haven't reached their weekly work limit.
        for day in DAYS:
            for shift in SHIFTS:
                while len(self.schedule[day][shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                    # Identify eligible candidates for this random fill:
                    # 1. Not yet at their `MAX_WORKDAYS_PER_WEEK`.
                    # 2. Not already assigned to this *specific shift* on this day.
                    # 3. Not in the `final_unresolved_employees` set (meaning they are problematic/cannot be placed).
                    # 4. Not already assigned to *any* other shift on *this day*.
                    
                    eligible_candidates_for_random_fill = []
                    for emp_name, _ in self.employees:
                        if self.workdays[emp_name] < self.MAX_WORKDAYS_PER_WEEK and \
                           emp_name not in self.schedule[day][shift] and \
                           emp_name not in final_unresolved_employees and \
                           not any(emp_name in self.schedule[day][s] for s in SHIFTS if s != shift):
                            eligible_candidates_for_random_fill.append(emp_name)

                    if eligible_candidates_for_random_fill:
                        chosen = random.choice(eligible_candidates_for_random_fill)
                        self.schedule[day][shift].append(chosen) # Assign randomly chosen employee
                        self.workdays[chosen] += 1 # Increment their workday count
                    else:
                        break # No more eligible candidates to fill this specific slot, move to the next.

        # Provide feedback to the user about the scheduling outcome.
        if final_unresolved_employees:
            unique_unresolved = ", ".join(sorted(list(final_unresolved_employees)))
            messagebox.showwarning("Partial Schedule",
                                   f"The following employees could not be fully scheduled due to persistent conflicts or reaching max workdays:\n"
                                   f"{unique_unresolved}\n\n"
                                   f"Consider adjusting their preferences, adding more employees, or modifying the max shift limit.")
        else:
            messagebox.showinfo("Schedule Generated", "The weekly schedule has been generated successfully!")

        self.show_schedule() # Display the generated schedule in a new window

    def show_schedule(self):
        """
        Creates a new top-level window to display the generated weekly schedule.
        The schedule is presented in a grid format with days as columns and shifts as rows.
        Aesthetics: Enhanced fonts, padding, and slightly different background for the schedule popup.
        """
        top = ctk.CTkToplevel(self.root) # Create a new top-level window
        top.title("Weekly Schedule") # Set the title of the new window
        top.transient(self.root) # Make the new window transient for the main window (stays on top)
        top.grab_set() # Make it modal: blocks interaction with the main window until closed
        top.lift() # Bring the window to the front
        top.geometry("1000x500") # Set a larger default size for the schedule window
        top.configure(fg_color="#F8F8F8") # Light grey background for the popup

        # Configure grid column and row weights for better resizing behavior
        top.grid_columnconfigure(0, weight=0) # Column for shift names (fixed size)
        for i in range(1, len(DAYS) + 1):
            top.grid_columnconfigure(i, weight=1) # Columns for days (expandable)
        for j in range(1, len(SHIFTS) + 1):
            top.grid_rowconfigure(j, weight=1) # Rows for shifts (expandable)

        # Top-left empty cell for alignment
        ctk.CTkLabel(top, text="", width=10).grid(row=0, column=0) 

        # Create day headers
        for i, day in enumerate(DAYS):
            ctk.CTkLabel(top, text=day, font=("Segoe UI", 14, "bold")).grid(row=0, column=i+1, padx=8, pady=8, sticky="nsew") # Increased font and padding

        # Create shift headers and populate schedule cells
        for j, shift in enumerate(SHIFTS):
            ctk.CTkLabel(top, text=shift, font=("Arial", 14, "bold")).grid(row=j+1, column=0, padx=8, pady=8, sticky="nsew") # Increased font and padding
            for i, day in enumerate(DAYS):
                # Modified to join names with a newline character for vertical display
                emp_list = "\n".join(self.schedule[day][shift]) 
                label = ctk.CTkLabel(top, text=emp_list, 
                                     padx=15, pady=10, # Increased internal padding for cell content
                                     wraplength=130, justify="center", # Increased wraplength as names are on separate lines
                                     fg_color="white", corner_radius=8, text_color="black",
                                     font=("Helvetica", 11)) # Font size remains the same
                label.grid(row=j+1, column=i+1, padx=5, pady=5, sticky="nsew") # Adjusted padx, pady for cells
                
                # The "hover for full" binding is removed as names are now on separate lines

        # Add a close button at the bottom of the schedule window
        ctk.CTkButton(top, text="Close", command=top.destroy, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").grid(row=len(SHIFTS)+1, column=0, columnspan=len(DAYS)+1, pady=15)

        top.resizable(True, True) # Allow the schedule window to be resizable

    def export_schedule(self):
        """
        Exports the current weekly schedule to a CSV (Comma Separated Values) file.
        Allows the user to choose the file location and name.
        """
        # Open a file dialog for saving the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path: # If the user cancels the dialog, do nothing
            return
        
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file: # Open file in write mode
                writer = csv.writer(file) # Create a CSV writer object
                writer.writerow(["Day", "Shift", "Employees"]) # Write the header row
                
                # Write each assigned shift to the CSV file
                for day in DAYS:
                    for shift in SHIFTS:
                        writer.writerow([day, shift, ", ".join(self.schedule[day][shift])])
            messagebox.showinfo("Export Successful", f"Schedule successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export schedule: {e}")

    def edit_employees(self):
        """
        Opens a new window allowing the user to select and remove employees from the list.
        Aesthetics: Consistent styling for the popup window, buttons, and dropdown.
        """
        top = ctk.CTkToplevel(self.root) # Create a new top-level window
        top.title("Edit/Remove Employees")
        top.transient(self.root) # Make it transient for the main window
        top.grab_set() # Make it modal: blocks interaction with the main window until closed
        top.lift() # Bring to front
        top.geometry("300x250") # Set initial size, slightly larger to accommodate close button better
        top.configure(fg_color="#F8F8F8") # Consistent background for popup

        if not self.employees:
            ctk.CTkLabel(top, text="No employees to edit.", font=("Helvetica", 12, "bold")).pack(padx=10, pady=20)
            ctk.CTkButton(top, text="Close", command=top.destroy, font=("Arial", 12, "bold"),
                          corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(pady=10)
            return

        ctk.CTkLabel(top, text="Select an employee to remove:", font=("Helvetica", 12)).pack(pady=(15, 5)) # Increased padding
        employee_names = [name for name, _ in self.employees]
        
        # Check again if employee_names might be empty (e.g., if the last employee was removed right before this opens)
        if not employee_names:
            ctk.CTkLabel(top, text="No employees left to remove.", font=("Helvetica", 12, "bold")).pack(padx=10, pady=20)
            ctk.CTkButton(top, text="Close", command=top.destroy, font=("Arial", 12, "bold"),
                          corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(pady=10)
            return

        # Create a StringVar to hold the selected employee name for removal
        selected_name = ctk.StringVar(value=employee_names[0]) # Default to the first employee
        dropdown = ctk.CTkOptionMenu(top, variable=selected_name, values=employee_names,
                                     fg_color="white", button_color="#6495ED", # DodgerBlue
                                     button_hover_color="#5580C2", text_color="black", 
                                     corner_radius=8, font=("Helvetica", 12)) # Consistent styling
        dropdown.pack(pady=10)

        def remove_employee_action():
            """Internal function to handle the removal of a selected employee."""
            name_to_remove = selected_name.get()
            original_len = len(self.employees)
            # Filter out the employee to be removed
            self.employees = [emp for emp in self.employees if emp[0] != name_to_remove]
            
            if len(self.employees) < original_len: # Check if an employee was actually removed
                messagebox.showinfo("Removed", f"Employee '{name_to_remove}' has been removed.")
            else:
                messagebox.showwarning("Not Found", f"Employee '{name_to_remove}' was not found in the list.")
            
            # Update the dropdown list after removal
            new_employee_names = [name for name, _ in self.employees]
            if new_employee_names:
                dropdown.configure(values=new_employee_names) # Update dropdown options
                selected_name.set(new_employee_names[0]) # Set default to first new employee
            else:
                dropdown.configure(values=["No employees"]) # No employees left
                selected_name.set("No employees")
                dropdown.configure(state="disabled") # Disable the dropdown if empty
                messagebox.showinfo("Info", "All employees have been removed. Closing window.")
                top.destroy() # Close the edit window if no employees are left

        ctk.CTkButton(top, text="Remove Selected", command=remove_employee_action, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#DC143C", hover_color="#B22222").pack(pady=15) # Crimson for remove button
        ctk.CTkButton(top, text="Close", command=top.destroy, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(pady=5)


if __name__ == "__main__":
    # Create the main Tkinter root window and start the application
    root = ctk.CTk()
    app = SchedulerApp(root)
    root.mainloop()
