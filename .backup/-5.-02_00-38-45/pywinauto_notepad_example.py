# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"Run some automations to test things"

__revision__ = "$Revision: 214 $"

import time

from pywinauto import application
from pywinauto import tests
from pywinauto.findbestmatch import MatchError
from pywinauto import findwindows


#application.set_timing(3, .5, 10, .5, .4, .2, .2, .1, .2, .5)

"Run a quick test on Notepad"

app = application.Application()
app.start_(ur"notepad.exe")

app['Notepad'].Wait('ready')

# type some text
app['Notepad']['Edit'].SetEditText(u"Привет от Gemini и Анюты! Мы автоматизируем этот Блокнот с помощью pywinauto!\r\nЭто так круто!")

# Save the file
app['Notepad'].MenuSelect("File->SaveAs")

# The Save As dialog might have different names depending on Windows version/language
# Let's try to be robust, pywinauto allows regex for titles
save_as_dialog = None
try:
    # Wait for the "Save As" dialog to appear. Title can vary by language.
    save_as_dialog = app.window(title_re=".*Save As.*|.*Сохранение.*")
    save_as_dialog.Wait('ready', timeout=10, retry_interval=0.5)
    print("Save As dialog found.")

    # Set the filename. The control for filename can vary.
    # Common is an Edit control, sometimes Edit1 or identified by a label.
    filename_input = None
    try:
        # Try common control ID 'Edit1'
        filename_input = save_as_dialog.Edit1
        print("Found filename input as Edit1.")
    except findwindows.ElementNotFoundError:
        print("Edit1 not found for filename. Trying generic Edit control.")
        try:
            # Try the first available Edit control. This is a bit of a guess.
            # A more robust method would be to use print_control_identifiers() on the dialog
            # or use a tool like SWAPY to find the exact control.
            filename_input = save_as_dialog.child_window(control_type="Edit", found_index=0)
            print("Found generic Edit control for filename.")
        except findwindows.ElementNotFoundError:
            print("Generic Edit control not found for filename.")
            # If the above fails, it might be a ComboBox for the filename
            try:
                filename_input = save_as_dialog.child_window(class_name="ComboBoxEx32")
                print("Found ComboBoxEx32 for filename.")
            except findwindows.ElementNotFoundError:
                print("ComboBoxEx32 not found for filename. Trying ComboBox.")
                try:
                    filename_input = save_as_dialog.ComboBox
                    print("Found ComboBox for filename.")
                except findwindows.ElementNotFoundError:
                    print("ERROR: Could not find a suitable control for filename input.")
                    raise # Re-raise the error if no suitable control is found

    if filename_input:
        filename_input.SetText("test_pywinauto.txt")
        print(f"Set filename to 'test_pywinauto.txt'")
    else:
        print("ERROR: Filename input control not identified.")
        raise Exception("Filename input control not identified")


    # Click the Save button. Title can vary by language.
    save_button = None
    try:
        save_button = save_as_dialog.child_window(title_re="Save|Сохранить", control_type="Button")
        print("Found Save button.")
        save_button.Click()
        print("Clicked Save button.")
    except findwindows.ElementNotFoundError:
        print("ERROR: Save button not found.")
        raise # Re-raise the error if save button is not found

    print("File should be saved as test_pywinauto.txt")
    time.sleep(1) # Give a moment for the save operation

except Exception as e:
    print(f"An error occurred during the save operation: {e}")
    # If save fails, try to close Notepad without saving to prevent hanging
    try:
        print("Attempting to close Notepad without saving due to previous error...")
        app['Notepad'].MenuSelect("File->Exit")
        confirm_dialog = app.window(title_re=".*Notepad.*|.*Блокнот.*")
        if confirm_dialog.Exists(timeout=2):
            try:
                # Try to click "Don't Save" or "Нет"
                dont_save_button = confirm_dialog.child_window(title_re="Don't Save|Не сохранять", control_type="Button")
                dont_save_button.Click()
                print("Clicked 'Don't Save'.")
            except Exception as e_dont_save:
                print(f"Could not click 'Don't Save' button: {e_dont_save}. Trying to close dialog.")
                confirm_dialog.Close() # Fallback to just closing the dialog
    except Exception as e_close_fail:
        print(f"Failed to close Notepad after save error: {e_close_fail}")
    raise # Re-raise the original error from the save operation

# Close Notepad
# Check if the main Notepad window still exists before trying to close it.
# The 'Save As' dialog might have closed it, or it might have been closed if an error occurred.
try:
    notepad_main_window = app.window(title="Notepad") # Assuming English title
    if notepad_main_window.Exists(timeout=2):
        print("Notepad window still exists. Attempting to close.")
        notepad_main_window.Close() # Standard close command
        print("Notepad closed.")
    else:
        # If "Notepad" title isn't found, try the original app['Notepad'] reference
        # This handles cases where the title might have changed or is localized
        if app['Notepad'].Exists(timeout=1):
             app['Notepad'].Close()
             print("Notepad (app['Notepad'] reference) closed.")
        else:
            print("Notepad window no longer exists or was already closed.")
except Exception as e:
    print(f"An error occurred while trying to close Notepad: {e}")

print("Script finished.")
