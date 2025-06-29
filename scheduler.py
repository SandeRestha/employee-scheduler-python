import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import random
import csv
from collections import defaultdict
import threading

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
        # Set the overall appearance and color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = root
        self.root.title("Employee Shift Scheduler")
        self.root.geometry("850x850")
        
        # Configure the grid to make column 0 and row 0 expand, centering the main_frame
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Set a softer background color for the main window
        self.root.configure(fg_color="#E8E8E8")
        
        self.employees = [] # List to store employee data: [(name, {day: {shift: priority}})]

        # Main frame to contain all UI elements, now using grid for centering
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        
        # Configure the main_frame's grid to center its contents
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0) # input_frame
        self.main_frame.grid_rowconfigure(1, weight=0) # button_frame
        
        self.build_input_frame()
        self.build_button_frame()
        
        # defaultdict for storing the final schedule: schedule[day][shift] = [employee1, employee2, ...]
        self.schedule = defaultdict(lambda: defaultdict(list))
        
        # defaultdict to keep track of total workdays assigned to each employee
        self.workdays = defaultdict(int)

        self.progress_label = None # Initialize progress label as None

    def build_input_frame(self):
        """
        Sets up the GUI components for collecting employee names and shift preferences.
        Includes input fields, dropdowns for days and shifts, and buttons for actions.
        Aesthetics: Applied consistent corner_radius, adjusted colors and spacing for a cleaner look.
        """
        frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#F8F8F8")
        frame.pack(fill="x", pady=15, padx=15)

        # Employee Name Input
        top_row = ctk.CTkFrame(frame, fg_color="transparent")
        top_row.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(top_row, text="Name:", width=100, font=("Helvetica", 13, "bold")).pack(side="left", padx=(0, 10))
        self.name_entry = ctk.CTkEntry(top_row, corner_radius=8, font=("Helvetica", 12))
        self.name_entry.pack(side="left", fill="x", expand=True)

        # Dictionary to store references to priority StringVar objects for each shift per day
        self.shift_priority_vars = defaultdict(dict) 

        # Frame to hold the main content: left column for day/shift/priority, right for legend
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", expand=True, pady=(10, 20))

        # Container for preference input rows (no scrolling)
        self.preference_input_container = ctk.CTkFrame(content_frame, corner_radius=15, fg_color="#F0F0F0")
        self.preference_input_container.pack(side="left", fill="x", padx=(15, 15), pady=15)

        # Headers for Day, Morning, Afternoon, Evening (with priorities)
        headers = ctk.CTkFrame(self.preference_input_container, fg_color="transparent")
        headers.pack(fill="x", pady=(8, 5))
        ctk.CTkLabel(headers, text="Day", width=80, anchor="w", font=("Helvetica", 12, "bold")).pack(side="left", padx=(10,5))
        ctk.CTkLabel(headers, text="Morning", width=110, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=(15,15))
        ctk.CTkLabel(headers, text="Afternoon", width=110, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=(15,15))
        ctk.CTkLabel(headers, text="Evening", width=110, anchor="center", font=("Helvetica", 12, "bold")).pack(side="left", padx=(15,15))

        # Right column for Priority Legend
        right_column = ctk.CTkFrame(content_frame, corner_radius=15, fg_color="#F0F0F0")
        right_column.pack(side="right", padx=20, anchor="n", pady=15)
        ctk.CTkLabel(right_column, text="Priority Legend", font=("Helvetica", 14, "bold"), anchor="center").pack(pady=10)
        ctk.CTkLabel(right_column, text="1 - Highest Preference", font=("Helvetica", 12), wraplength=150).pack(anchor="w", padx=25, pady=4)
        ctk.CTkLabel(right_column, text="2 - Medium Preference", font=("Helvetica", 12), wraplength=150).pack(anchor="w", padx=25, pady=4)
        ctk.CTkLabel(right_column, text="3 - Lowest Preference\n(Assigned if no other option)", font=("Helvetica", 12), justify="left", wraplength=150).pack(anchor="w", padx=25, pady=4)


        for day in DAYS:
            row = ctk.CTkFrame(self.preference_input_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=day, width=80, anchor="w", font=("Helvetica", 12)).pack(side="left", padx=(10, 5))

            for shift in SHIFTS:
                priority = ctk.StringVar(value="1")
                dropdown = ctk.CTkOptionMenu(row, variable=priority, values=["1", "2", "3"], 
                                             fg_color="white", button_color="#6495ED",
                                             button_hover_color="#5580C2",
                                             text_color="black", 
                                             width=110, corner_radius=8, font=("Helvetica", 12))
                dropdown.pack(side="left", padx=(15, 15))
                self.shift_priority_vars[day][shift] = priority

        # Frame for Add and Edit/Remove Employee buttons
        employee_button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        employee_button_frame.pack(pady=15)
        
        # Add Employee button
        ctk.CTkButton(employee_button_frame, text="ADD EMPLOYEE", command=self.add_employee, font=("Helvetica", 13, "bold"), 
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(side="left", padx=5)
        
        # Edit/Remove Employees button
        ctk.CTkButton(employee_button_frame, text="EDIT/REMOVE EMPLOYEES", command=self.edit_employees, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(side="left", padx=5)

    def build_button_frame(self):
        """
        Creates the horizontal frame for the main action buttons.
        """
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Generate Schedule button
        ctk.CTkButton(button_frame, text="GENERATE SCHEDULE", command=self.run_generate_schedule_thread, font=("Arial", 14, "bold"),
                      fg_color="#3683D9", hover_color="#2A6BAB",
                      corner_radius=10, height=40).pack(side="left", padx=10)
        
        # View Current Schedule button
        ctk.CTkButton(button_frame, text="VIEW CURRENT SCHEDULE", command=self.show_schedule, font=("Arial", 14, "bold"),
                      fg_color="#3683D9", hover_color="#2A6BAB",
                      corner_radius=10, height=40).pack(side="left", padx=10)
        
        # Export Schedule button
        ctk.CTkButton(button_frame, text="EXPORT SCHEDULE", command=self.export_schedule, font=("Arial", 14, "bold"),
                      fg_color="#3683D9", hover_color="#2A6BAB",
                      corner_radius=10, height=40).pack(side="left", padx=10)

        # Reset All Data button
        ctk.CTkButton(button_frame, text="RESET ALL DATA", command=self.reset_all_data, font=("Arial", 14, "bold"),
                      fg_color="#DC143C", hover_color="#B22222",
                      corner_radius=10, height=40).pack(side="left", padx=10)

    def add_employee(self):
        """
        Collects employee name and preferences from the UI and adds them to the employees list.
        Performs basic validation (e.g., name is required, no duplicates) and provides user feedback.
        """
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("INPUT ERROR", "Employee name is required.")
            return
        
        if any(emp_name.lower() == name.lower() for emp_name, _ in self.employees):
            messagebox.showerror("DUPLICATE ERROR", f"Employee '{name}' already exists. Please use a unique name.")
            return

        prefs = {day: {shift: self.shift_priority_vars[day][shift].get() for shift in SHIFTS} for day in DAYS}
        self.employees.append((name, prefs))
        
        self.name_entry.delete(0, 'end')
        
        # Reset priority dropdowns to default values (1) for next employee input
        for day in DAYS:
            for shift in SHIFTS:
                self.shift_priority_vars[day][shift].set("1")
                
        messagebox.showinfo("SUCCESS", f"Employee '{name}' added successfully.")

    def show_progress_label(self):
        """Displays a temporary label to indicate that the schedule is generating."""
        if not self.progress_label:
            self.progress_label = ctk.CTkLabel(self.main_frame, text="GENERATING SCHEDULE...", 
                                               font=("Arial", 16, "bold"), text_color="#2A6BAB")
            self.progress_label.pack(pady=20)
            self.root.update_idletasks()  # Force the UI to update immediately

    def hide_progress_label(self):
        """Hides the progress label."""
        if self.progress_label:
            self.progress_label.destroy()
            self.progress_label = None

    def run_generate_schedule_thread(self):
        """
        Starts the schedule generation in a separate thread to prevent the UI from freezing.
        """
        if not self.employees:
            messagebox.showwarning("NO EMPLOYEES", "Please add employees before generating a schedule.")
            return

        self.show_progress_label()
        
        # Start the generation process in a new thread
        thread = threading.Thread(target=self._generate_schedule_worker)
        thread.start()

    def _generate_schedule_worker(self):
        """
        Worker function for the thread to generate the schedule.
        This function contains the core scheduling logic.
        """
        # Call the original generate_schedule logic
        self.generate_schedule_logic()
        
        # Use root.after to safely update the UI from the thread
        self.root.after(100, self.hide_progress_label)
        self.root.after(200, self.show_schedule)
        self.root.after(300, lambda: messagebox.showinfo("SCHEDULE GENERATED", "The weekly schedule has been generated successfully!"))

    def generate_schedule_logic(self):
        """
        Contains the core logic for assigning employees to shifts.
        This method is called by the threading worker.
        """
        self.schedule.clear()
        self.workdays.clear()
        
        for day in DAYS:
            for shift in SHIFTS:
                self.schedule[day][shift] = []

        day_indices = {day: i for i, day in enumerate(DAYS)}
        final_unresolved_employees = set()

        # Phase 1: Assign based on employees' highest daily priorities.
        for day in DAYS:
            assigned_on_current_day_pass1 = set()
            employees_sorted_by_best_daily_priority = []
            for name, prefs in self.employees:
                min_priority_for_day = min(int(prefs[day][s]) for s in SHIFTS)
                employees_sorted_by_best_daily_priority.append((min_priority_for_day, name, prefs))
            
            employees_sorted_by_best_daily_priority.sort()

            for min_prio, name, prefs in employees_sorted_by_best_daily_priority:
                if self.workdays[name] >= self.MAX_WORKDAYS_PER_WEEK or name in assigned_on_current_day_pass1:
                    continue

                sorted_shifts_for_employee_on_day = sorted(SHIFTS, key=lambda s: int(prefs[day][s]))
                
                assigned_this_employee_for_day = False
                for target_shift in sorted_shifts_for_employee_on_day:
                    if len(self.schedule[day][target_shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                        self.schedule[day][target_shift].append(name)
                        self.workdays[name] += 1
                        assigned_on_current_day_pass1.add(name)
                        assigned_this_employee_for_day = True
                        break

        # Phase 2: Resolve remaining employees by attempting assignments on unassigned days.
        for name, prefs in self.employees:
            while self.workdays[name] < self.MAX_WORKDAYS_PER_WEEK:
                assigned_in_this_loop_pass2 = False
                
                available_days_for_employee = []
                for day_to_check in DAYS:
                    if not any(name in self.schedule[day_to_check][s] for s in SHIFTS):
                        available_days_for_employee.append(day_to_check)
                
                if not available_days_for_employee:
                    break 

                available_days_for_employee.sort(key=lambda d: min(int(prefs[d][s]) for s in SHIFTS))

                for target_day in available_days_for_employee:
                    sorted_shifts_for_target_day = sorted(SHIFTS, key=lambda s: int(prefs[target_day][s]))
                    for target_shift in sorted_shifts_for_target_day:
                        if len(self.schedule[target_day][target_shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                            self.schedule[target_day][target_shift].append(name)
                            self.workdays[name] += 1
                            assigned_in_this_loop_pass2 = True
                            break
                    if assigned_in_this_loop_pass2:
                        break
                
                if assigned_in_this_loop_pass2:
                    continue

                # Attempt to assign to the *next consecutive day*
                assigned_on_next_day = False
                for original_day_candidate in available_days_for_employee:
                    current_day_idx = day_indices[original_day_candidate]
                    next_day_idx = (current_day_idx + 1) % len(DAYS)
                    next_day = DAYS[next_day_idx]

                    if not any(name in self.schedule[next_day][s] for s in SHIFTS):
                        sorted_shifts_for_next_day = sorted(SHIFTS, key=lambda s: int(prefs[next_day][s]))
                        for next_day_shift in sorted_shifts_for_next_day:
                            if len(self.schedule[next_day][next_day_shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                                self.schedule[next_day][next_day_shift].append(name)
                                self.workdays[name] += 1
                                assigned_on_next_day = True
                                assigned_in_this_loop_pass2 = True
                                break
                    if assigned_on_next_day:
                        break
                
                if not assigned_in_this_loop_pass2:
                    final_unresolved_employees.add(name)
                    break

        # Phase 3: Fill Any Remaining Empty Slots Randomly.
        for day in DAYS:
            for shift in SHIFTS:
                while len(self.schedule[day][shift]) < self.MAX_EMPLOYEES_PER_SHIFT:
                    eligible_candidates_for_random_fill = []
                    for emp_name, _ in self.employees:
                        if self.workdays[emp_name] < self.MAX_WORKDAYS_PER_WEEK and \
                           emp_name not in self.schedule[day][shift] and \
                           emp_name not in final_unresolved_employees and \
                           not any(emp_name in self.schedule[day][s] for s in SHIFTS if s != shift):
                            eligible_candidates_for_random_fill.append(emp_name)

                    if eligible_candidates_for_random_fill:
                        chosen = random.choice(eligible_candidates_for_random_fill)
                        self.schedule[day][shift].append(chosen)
                        self.workdays[chosen] += 1
                    else:
                        break

        # Provide feedback to the user about the scheduling outcome.
        if final_unresolved_employees:
            unique_unresolved = ", ".join(sorted(list(final_unresolved_employees)))
            messagebox.showwarning("PARTIAL SCHEDULE",
                                   f"The following employees could not be fully scheduled due to persistent conflicts or reaching max workdays:\n"
                                   f"{unique_unresolved}\n\n"
                                   f"Consider adjusting their preferences, adding more employees, or modifying the max shift limit.")

    def show_schedule(self):
        """
        Creates a new top-level window to display the generated weekly schedule.
        The schedule is presented in a grid format with days as columns and shifts as rows.
        Aesthetics: Enhanced fonts, padding, and slightly different background for the schedule popup.
        """
        top = ctk.CTkToplevel(self.root)
        top.title("WEEKLY SCHEDULE")
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.geometry("1000x500")
        top.configure(fg_color="#F8F8F8")

        # Configure grid column and row weights for better resizing behavior
        top.grid_columnconfigure(0, weight=0)
        for i in range(1, len(DAYS) + 1):
            top.grid_columnconfigure(i, weight=1)
        for j in range(1, len(SHIFTS) + 1):
            top.grid_rowconfigure(j, weight=1)

        # Top-left empty cell for alignment
        ctk.CTkLabel(top, text="", width=10).grid(row=0, column=0) 

        # Create day headers
        for i, day in enumerate(DAYS):
            ctk.CTkLabel(top, text=day, font=("Segoe UI", 14, "bold")).grid(row=0, column=i+1, padx=8, pady=8, sticky="nsew")

        # Create shift headers and populate schedule cells
        for j, shift in enumerate(SHIFTS):
            ctk.CTkLabel(top, text=shift, font=("Arial", 14, "bold")).grid(row=j+1, column=0, padx=8, pady=8, sticky="nsew")
            for i, day in enumerate(DAYS):
                emp_list = "\n".join(self.schedule[day][shift]) 
                label = ctk.CTkLabel(top, text=emp_list, 
                                     padx=15, pady=10,
                                     wraplength=130, justify="center",
                                     fg_color="white", corner_radius=8, text_color="black",
                                     font=("Helvetica", 11))
                label.grid(row=j+1, column=i+1, padx=5, pady=5, sticky="nsew")
                
        # Add a close button at the bottom of the schedule window
        ctk.CTkButton(top, text="CLOSE", command=top.destroy, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#4682B4", hover_color="#36648B").grid(row=len(SHIFTS)+1, column=0, columnspan=len(DAYS)+1, pady=15)

        top.resizable(True, True)

    def export_schedule(self):
        """
        Exports the current weekly schedule to a CSV (Comma Separated Values) file.
        Allows the user to choose the file location and name.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Day", "Shift", "Employees"])
                
                for day in DAYS:
                    for shift in SHIFTS:
                        writer.writerow([day, shift, ", ".join(self.schedule[day][shift])])
            messagebox.showinfo("EXPORT SUCCESSFUL", f"Schedule successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("EXPORT ERROR", f"Failed to export schedule: {e}")

    def edit_employees(self):
        """
        Opens a new window to select an employee for editing or removal.
        """
        top = ctk.CTkToplevel(self.root)
        top.title("EDIT/REMOVE EMPLOYEES")
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.geometry("400x150")
        top.configure(fg_color="#F8F8F8")

        if not self.employees:
            ctk.CTkLabel(top, text="NO EMPLOYEES TO EDIT.", font=("Helvetica", 12, "bold")).pack(padx=10, pady=20)
            ctk.CTkButton(top, text="CLOSE", command=top.destroy, font=("Arial", 12, "bold"),
                          corner_radius=10, fg_color="#4682B4", hover_color="#36648B").pack(pady=10)
            return

        ctk.CTkLabel(top, text="SELECT AN EMPLOYEE:", font=("Helvetica", 12)).pack(pady=(15, 5))
        employee_names = [name for name, _ in self.employees]
        
        selected_name = ctk.StringVar(value=employee_names[0])
        dropdown = ctk.CTkOptionMenu(top, variable=selected_name, values=employee_names,
                                     fg_color="white", button_color="#6495ED",
                                     button_hover_color="#5580C2", text_color="black",
                                     corner_radius=8, font=("Helvetica", 12))
        dropdown.pack(pady=10)

        def open_edit_name_window():
            """Opens the window to edit the name for the selected employee."""
            name_to_edit = selected_name.get()
            top.destroy() # Close the selection window
            self.edit_employee_name(name_to_edit)

        def remove_employee_action():
            """Removes the selected employee from the list."""
            name_to_remove = selected_name.get()
            if messagebox.askyesno("CONFIRM REMOVAL", f"Are you sure you want to remove '{name_to_remove}'?"):
                self.employees = [emp for emp in self.employees if emp[0] != name_to_remove]
                messagebox.showinfo("REMOVED", f"Employee '{name_to_remove}' has been removed.")
                top.destroy()

        button_frame = ctk.CTkFrame(top, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="EDIT NAME", command=open_edit_name_window, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#3683D9", hover_color="#2A6BAB").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="REMOVE EMPLOYEE", command=remove_employee_action, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#DC143C", hover_color="#B22222").pack(side="left", padx=5)

    def edit_employee_name(self, employee_name):
        """
        Creates a new window to edit the name of a specific employee.
        """
        top = ctk.CTkToplevel(self.root)
        top.title(f"EDIT NAME: {employee_name.upper()}")
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.geometry("400x150")
        top.configure(fg_color="#F8F8F8")
        
        # Name editing section
        name_frame = ctk.CTkFrame(top, fg_color="transparent")
        name_frame.pack(pady=20)
        ctk.CTkLabel(name_frame, text="New Name:", font=("Helvetica", 13, "bold")).pack(side="left", padx=(0, 10))
        new_name_entry = ctk.CTkEntry(name_frame, corner_radius=8, font=("Helvetica", 12))
        new_name_entry.insert(0, employee_name)
        new_name_entry.pack(side="left")

        def save_name_change():
            """Saves the edited name."""
            new_name = new_name_entry.get().strip()
            if not new_name:
                messagebox.showerror("INPUT ERROR", "Name cannot be empty.")
                return

            # Check for duplicate name, excluding the original employee
            if new_name.lower() != employee_name.lower() and any(emp_name.lower() == new_name.lower() for emp_name, _ in self.employees):
                messagebox.showerror("DUPLICATE ERROR", f"Employee '{new_name}' already exists.")
                return

            # Find the employee and update their name in the main list
            for i, (name, prefs) in enumerate(self.employees):
                if name == employee_name:
                    self.employees[i] = (new_name, prefs)
                    break
            
            messagebox.showinfo("SUCCESS", f"Employee name changed from '{employee_name}' to '{new_name}'.")
            top.destroy()

        button_frame = ctk.CTkFrame(top, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="SAVE CHANGES", command=save_name_change, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#3CB371", hover_color="#2E8B57").pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="CANCEL", command=top.destroy, font=("Arial", 13, "bold"),
                      corner_radius=10, fg_color="#DC143C", hover_color="#B22222").pack(side="left", padx=10)

    def reset_all_data(self):
        """
        Resets all employee and schedule data after a user confirmation.
        """
        if messagebox.askyesno("CONFIRM RESET", "ARE YOU SURE YOU WANT TO RESET ALL EMPLOYEE DATA AND CLEAR THE SCHEDULE? THIS ACTION CANNOT BE UNDONE."):
            self.employees = []
            self.schedule.clear()
            self.workdays.clear()
            messagebox.showinfo("DATA RESET", "ALL EMPLOYEE DATA AND THE CURRENT SCHEDULE HAVE BEEN CLEARED.")
            # Clear the name entry and reset priorities
            self.name_entry.delete(0, 'end')
            for day in DAYS:
                for shift in SHIFTS:
                    self.shift_priority_vars[day][shift].set("1")


if __name__ == "__main__":
    # Create the main Tkinter root window and start the application
    root = ctk.CTk()
    app = SchedulerApp(root)
    root.mainloop()