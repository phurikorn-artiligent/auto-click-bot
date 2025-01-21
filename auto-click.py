import customtkinter as ctk
import pyautogui
import keyboard
import time
from tkinter import Listbox

class AutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automation App")
        self.actions = []  # Combined list of all actions
        self.start_hotkey = 'shift'
        self.is_enabled = ctk.BooleanVar(value=True)  # Variable to track checkbox state
        self.create_widgets()
        self.listen_to_hotkey()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="Automation App", font=("Helvetica", 16)).pack(pady=10)

        self.position_listbox = Listbox(self.main_frame, height=8, width=100)
        self.position_listbox.pack(pady=5)

        self.add_position_button = ctk.CTkButton(self.main_frame, text="Add Cursor Action", command=self.add_position)
        self.add_position_button.pack(side="left", padx=5)

        self.add_hotkey_button = ctk.CTkButton(self.main_frame, text="Add Hotkey Action", command=self.add_hotkey_action)
        self.add_hotkey_button.pack(side="left", padx=5)

        self.remove_position_button = ctk.CTkButton(self.main_frame, text="Remove Selected", command=self.remove_position)
        self.remove_position_button.pack(side="left", padx=5)

        self.edit_position_button = ctk.CTkButton(self.main_frame, text="Edit Selected", command=self.edit_position)
        self.edit_position_button.pack(side="left", padx=5)

        ctk.CTkLabel(self.main_frame, text="Default Delay (seconds):").pack(pady=5)
        self.delay_entry = ctk.CTkEntry(self.main_frame)
        self.delay_entry.insert(0, "1.0")
        self.delay_entry.pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="Start Hotkey:").pack(pady=5)
        self.hotkey_entry = ctk.CTkEntry(self.main_frame)
        self.hotkey_entry.insert(0, "shift")
        self.hotkey_entry.pack(pady=5)

        self.set_hotkey_button = ctk.CTkButton(self.main_frame, text="Set New Hotkey", command=self.set_hotkey)
        self.set_hotkey_button.pack(pady=5)

        # Add CheckBox to enable/disable the program
        self.enable_checkbox = ctk.CTkCheckBox(self.main_frame, text="Enable Program", variable=self.is_enabled)
        self.enable_checkbox.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_frame, text="", fg_color="blue")
        self.status_label.pack(pady=5)

    def add_position(self):
        self.countdown(3)

    def countdown(self, count):
        if count > 0:
            self.status_label.configure(text=f"Move the cursor to the desired position, starting in {count} seconds...")
            self.root.after(1000, self.countdown, count-1)
        else:
            self.status_label.configure(text="Saving position...")
            self.root.update_idletasks()
            position = pyautogui.position()
            delay = float(self.delay_entry.get())
            action_sequence = self.ask_action_sequence(cursor_actions=True)
            self.actions.append(('cursor', position, delay, action_sequence))
            self.position_listbox.insert(ctk.END, f"Cursor Action: Position: {position}, Delay: {delay}s, Actions: {action_sequence}")
            self.status_label.configure(text=f"Position {position} added with actions {action_sequence}.")

    def add_hotkey_action(self):
        action_sequence = self.ask_action_sequence(cursor_actions=False)
        self.actions.append(('hotkey', action_sequence))
        self.position_listbox.insert(ctk.END, f"Hotkey Action: Actions: {action_sequence}")
        self.status_label.configure(text=f"Hotkey actions {action_sequence} added.")

    def remove_position(self):
        selected_indices = self.position_listbox.curselection()
        for index in reversed(selected_indices):
            del self.actions[index]
            self.position_listbox.delete(index)
        self.status_label.configure(text="Selected actions removed.")

    def edit_position(self):
        selected_indices = self.position_listbox.curselection()
        if not selected_indices:
            self.status_label.configure(text="No action selected to edit.")
            return

        index = selected_indices[0]
        action_type, *action_data = self.actions[index]

        if action_type == 'cursor':
            position, delay, actions = action_data
            self.edit_action_window(index, position, delay, actions, cursor_actions=True)
        elif action_type == 'hotkey':
            actions = action_data[0]
            self.edit_action_window(index, None, None, actions, cursor_actions=False)

    def edit_action_window(self, index, position, delay, actions, cursor_actions):
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Edit Action")

        if cursor_actions:
            ctk.CTkLabel(edit_window, text=f"Edit Cursor Action at {position}").pack(pady=5)
            delay_entry = ctk.CTkEntry(edit_window)
            delay_entry.insert(0, str(delay))
            delay_entry.pack(pady=5)
        else:
            ctk.CTkLabel(edit_window, text="Edit Hotkey Action").pack(pady=5)

        actions_listbox = Listbox(edit_window, selectmode="multiple")
        actions_listbox.pack(pady=5)

        available_actions = ["Click", "Double Click", "Triple Click"] if cursor_actions else ["Copy", "Paste", "Enter", "Find"]
        for action in available_actions:
            actions_listbox.insert(ctk.END, action)

        for action in actions:
            idx = available_actions.index(action)
            actions_listbox.selection_set(idx)

        def on_save():
            new_actions = [actions_listbox.get(i) for i in actions_listbox.curselection()]
            if cursor_actions:
                new_delay = float(delay_entry.get())
                self.actions[index] = ('cursor', position, new_delay, new_actions)
                self.position_listbox.delete(index)
                self.position_listbox.insert(index, f"Cursor Action: Position: {position}, Delay: {new_delay}s, Actions: {new_actions}")
            else:
                self.actions[index] = ('hotkey', new_actions)
                self.position_listbox.delete(index)
                self.position_listbox.insert(index, f"Hotkey Action: Actions: {new_actions}")

            edit_window.destroy()
            self.status_label.configure(text="Action edited successfully.")

        ctk.CTkButton(edit_window, text="Save", command=on_save).pack(pady=10)
        edit_window.grab_set()
        self.root.wait_window(edit_window)

    def ask_action_sequence(self, cursor_actions=True):
        action_window = ctk.CTkToplevel(self.root)
        action_window.title("Select Actions")
        ctk.CTkLabel(action_window, text="Select Actions for this Position (in order):").pack(pady=5)
        actions_listbox = Listbox(action_window, selectmode="extended")
        actions_listbox.pack(pady=5)
        
        if cursor_actions:
            actions = ["Click", "Double Click", "Triple Click"]
        else:
            actions = ["Copy", "Paste", "Enter", "Find"]
        
        for action in actions:
            actions_listbox.insert(ctk.END, action)

        selected_actions_listbox = Listbox(action_window, height=5)
        selected_actions_listbox.pack(pady=5)

        def update_selected_actions():
            selected_actions = [actions_listbox.get(i) for i in actions_listbox.curselection()]
            for action in selected_actions:
                selected_actions_listbox.insert(ctk.END, action)

        ctk.CTkButton(action_window, text="Add", command=update_selected_actions).pack(pady=5)

        def move_up():
            selected_indices = selected_actions_listbox.curselection()
            for index in selected_indices:
                if index > 0:
                    item = selected_actions_listbox.get(index)
                    selected_actions_listbox.delete(index)
                    selected_actions_listbox.insert(index - 1, item)
                    selected_actions_listbox.selection_set(index - 1)

        def move_down():
            selected_indices = selected_actions_listbox.curselection()
            for index in reversed(selected_indices):
                if index < selected_actions_listbox.size() - 1:
                    item = selected_actions_listbox.get(index)
                    selected_actions_listbox.delete(index)
                    selected_actions_listbox.insert(index + 1, item)
                    selected_actions_listbox.selection_set(index + 1)

        ctk.CTkButton(action_window, text="Move Up", command=move_up).pack(pady=5)
        ctk.CTkButton(action_window, text="Move Down", command=move_down).pack(pady=5)

        selected_actions = []

        def on_ok():
            nonlocal selected_actions
            selected_actions = [selected_actions_listbox.get(i) for i in range(selected_actions_listbox.size())]
            action_window.destroy()

        ctk.CTkButton(action_window, text="OK", command=on_ok).pack(pady=10)
        action_window.grab_set()
        self.root.wait_window(action_window)

        return selected_actions

    def perform_action(self):
        if not self.is_enabled.get():
            self.status_label.configure(text="Program is disabled.")
            return

        for action in self.actions:
            if action[0] == 'cursor':
                _, position, delay, actions = action
                pyautogui.moveTo(position)
                time.sleep(delay)  # Ensure delay after moving
                for act in actions:
                    if act.startswith("Click"):
                        parts = act.split()
                        count = int(parts[1]) if len(parts) > 1 else 1
                        pyautogui.click(clicks=count)
                    elif act == "Double Click":
                        pyautogui.doubleClick()
                    elif act == "Triple Click":
                        pyautogui.click(clicks=3)
            elif action[0] == 'hotkey':
                _, actions = action
                for act in actions:
                    if act == "Copy":
                        pyautogui.hotkey("ctrl", "c")
                    elif act == "Paste":
                        pyautogui.hotkey("ctrl", "v")
                    elif act == "Enter":
                        pyautogui.press('enter')
                    elif act == "Find":
                        pyautogui.hotkey("ctrl", "f")

    def set_hotkey(self):
        self.status_label.configure(text="Press the new hotkey...")
        self.root.update_idletasks()
        new_hotkey = keyboard.read_hotkey(suppress=True)
        self.hotkey_entry.delete(0, ctk.END)
        self.hotkey_entry.insert(0, new_hotkey)
        self.start_hotkey = new_hotkey
        keyboard.remove_all_hotkeys()
        self.listen_to_hotkey()
        self.status_label.configure(text=f"Hotkey set to: {new_hotkey}")

    def listen_to_hotkey(self):
        keyboard.add_hotkey(self.start_hotkey, self.perform_action)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    app = AutomationApp(root)
    root.mainloop()