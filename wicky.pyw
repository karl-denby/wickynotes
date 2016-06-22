#!/usr/bin/env python
from __future__ import print_function
import sqlite3
try:  # python2 imports
    import tkinter as Tkinter
    import tkinter.ttk as ttk
    import tkinter.messagebox as tkMessageBox
except ImportError:  # python3 imports
    import Tkinter
    import ttk
    import tkMessageBox


class NoteWindow:
    # Jobs
    ## This is going to be the GUI element for each note
    ## responsible for display and input of data, then
    ## calling the appropriate backend process when we
    ## need to read/write something at an app level

    def create_note(self, named_note, event):
    # GUI:
        print("GUI: Create Note")
        print(self.title + ": Wants to recreate a note named: ", end='')
        print(named_note)
        print("Calling NoteManger to recreate this note")
    # Backend:
        server.recreate_note(named_note)

    def master_note(self, event=''):
        # GUI
        print("Master Note")

        note_list = []
        master_text = 'All Notes\n\n'
        #for note in server.note_window_map.keys():
        for note in list(server.note_window_map.keys()):
            master_text = master_text + note + '\n'

        #GUI, draw window
        master = NoteWindow(note_list, 'Master', master_text, 'Green')
        master.note_color.config(state='disabled')
        master.new_note.config(state='disabled')
        master.map_note.config(state='disabled')
        master.note_payload.tag_configure('bold', font='helvetica 10 bold')
        master.note_payload.tag_add('bold', '3.0', 'end')

        return master

    def click_linked(self, event=''):
        # GUI, get the clicked word by extending selection
        w_start = self.note_payload.index('current wordstart')
        w_end = self.note_payload.index('current wordend')
        word = self.note_payload.get(w_start, w_end)
        print(self.title + ": User clicked " + word)

        # Check for a match regardless of case or space in the name
        for key in list(server.note_window_map.keys()):
            if word.upper() in key.upper().split(" "):
                word = key
                break

        print(server.note_window_map[word])

        # GUI, lift, if already running.  Backend create if not.
        if server.note_window_map[word] is not None:
            print (word + ": exists")
            print(word + ": lifted")
            server.note_window_map[word].window.lift()
        else:
            print (word + ": is closed, Recreating")
            self.create_note(word, event)

    def click_htext(self, event=''):
        # This is kind of our test function at the minute!
        # not sure about what we want in the Master note so
        # ignore it for now
        if self.title == 'Master':
            return

        # We are just going to run a refresh if not the Master
        self.refresh_note()

    def click_newnote(self, event=''):
        # GUI
        print(self.title + ": Requested new note")

        # GUI, grab title from selection, put it in head and body, white color
        if self.note_payload.tag_ranges('sel'):
            # New note variable, from selection
            note_data = [
                self.note_payload.get('sel.first', 'sel.last'),
                self.note_payload.get('sel.first', 'sel.last'),
                'White',
                1
            ]
            print(self.title + ": Creating Note, " + note_data[0])

        else:
            # New note variable, from defaults
            note_data = ['Note Title', 'Note Title', 'White', 1]
            print(self.title + ": no text highlighted.  Creating default note")

        # Backend, make the note as specified
        server.create_new_note(note_data)
        print(self.title + ": Note Created")

    def note_close(self):
        # GUI, Master is special case, not in DB so just destroy it.
        if self.title == 'Master':
            self.window.destroy()
            return

        # Debug: We will be saving the note contents on exit
        #        simply update the database
        #          unless new title is blank, then delete it
        old_note_name = self.title
        new_note_name = self.note_payload.get('1.0', '1.end')

        window_count = 0
        # possible for user to change the name to the same name as a
        # note that exists. We need to block this
        for key in list(server.note_window_map.keys()):
            print(new_note_name + ' : ' + key)
            if server.note_window_map[key] is not None:
                window_count = window_count + 1  # count for quit later
            if new_note_name.upper() == key.upper():
                print("found existing note, with same name")
                new_note_name = old_note_name
                self.note_payload.delete('1.0', '1.end')
                self.note_payload.insert('1.end', old_note_name)

        note_contents = self.note_payload.get('1.0', 'end')
        note_data = [
            new_note_name,
            note_contents,
            self.note_color.get(),
            old_note_name
        ]
        if new_note_name != '':              # Backend, title not blank. Save
            server.update_note(note_data)
            print(self.title + ": Saved")
        else:                                  # Backend, title is blank. Del.
            server.delete_note(note_data)
            print(self.title + ": Deleted")

        print("Window count is : " + str(window_count))
        if window_count != 1:
            self.window.destroy()  # Destroy if multiple windows open
        else:
            self.window.quit()  # Quit if we are the last note

    def set_sticky(self):
        # GUI, whatever we get passed (0 or 1) flip it
        if self.StayOnTop == 0:
            self.StayOnTop = 1
            print(self.title + ": Always On Top, Enabled")
            self.window.wm_attributes('-topmost', True)
        else:
            print(self.title + ": Always On Top, Disabled")
            self.StayOnTop = 0
            self.window.wm_attributes('-topmost', False)

    def init_colors(self, note_bg):
        # sets initial value of the variable used for the Combobox
        # iterates through entries counting, when we get to the right
        # number for example 3rd on list is Yellow, so we hit 2 and
        # return that, so the ComboVar is set correctly for this note
        i = 0
        for color in self.note_color.cget('values'):
            if color != note_bg:
                i = i + 1
            else:
                return(i)

    def colors(self, event=''):
        # Set the Text bg to one of the colors listed in our Combobox
        self.note_payload.config(bg=self.note_color.get())
        print(self.title + ": Color set as", self.note_color.get())

    def refresh_note(self, value=None):
        # Header
        self.note_payload.tag_configure('header',
                                        font='helvetica 12 underline bold')
        self.note_payload.tag_add('header', '1.0', '1.end')

        # Links
        note_titles = self.note_names
        #print(self.note_names)

        self.note_payload.tag_configure('bold', font='helvetica 10 bold')
        self.note_payload.tag_remove('bold', '2.0', 'end')

        for title in note_titles:
#            print(title)
            start = 2.0
            while 1:
                word_start = self.note_payload.search(
                    title, start, stopindex='end', nocase=True
                )
#                print(word_start)
                word_end = word_start.split(".")
                if len(word_end) > 1:
                    word_end = word_end[0] + '.' + str(int(word_end[1]) + len(title))
#                    print (word_end)
                if not word_start:
                    break
                self.note_payload.tag_add('bold', word_start, word_end)
                start = word_start + "+1c"

        self.note_payload.edit_modified(False)

    def __init__(self, note_names, note_title, note_text='', note_bg=''):
        # Make a window with the title provided when instance was created.
        self.note_names = note_names
        self.master = ""
        self.ComboVar = ""
        self.StayOnTop = 0
        self.title = note_title
        self.window = Tkinter.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.note_close)
        self.window.title(note_title)
        self.window.resizable(1, 1)
        self.window.minsize(400, 240)
        #self.window.geometry('405x300')

        # Components
        ## Header Options
        self.note_color = ttk.Combobox(
            self.window,
            values=('Yellow', 'Pink', 'Cyan', 'White', 'Red'),
            state='readonly',
            textvariable=self.ComboVar
            )
        self.note_color.bind('<<ComboboxSelected>>', self.colors)
        self.ComboVar = self.init_colors(note_bg)
        self.note_color.current(self.ComboVar)

        self.on_top = Tkinter.Checkbutton(
            self.window,
            text="On Top",
            variable=self.StayOnTop,
            command=self.set_sticky
            )

        self.new_note = ttk.Button(
            self.window,
            text="New Note",
            underline=0,
            command=self.click_newnote
            )

        self.map_note = ttk.Button(
            self.window,
            text="All Notes",
            underline=0,
            command=self.master_note
            )

        ## Main window
        self.note_payload = Tkinter.Text(
            master=self.window,
            width=60,
            height=17,
            wrap='word',
            state='normal'
            )
        self.note_payload.config(bg=note_bg)
        self.note_payload.insert("end", note_text)

        self.note_payload.tag_bind('bold', '<Button-1>', self.click_linked)
        self.refresh_note()
        self.note_payload.bind('<<Modified>>', self.refresh_note)
        self.note_payload.edit_modified(False)

        # Key Bindings
        self.window.bind_all('<Alt-n>', self.click_newnote)
        self.window.bind_all('<Alt-a>', self.master_note)

        # The Grid
        #self.window.rowconfigure(0, weight=)
        #self.window.columnconfigure(0, weight=1)

        self.window.rowconfigure(0, weight=0)
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=0)
        self.window.columnconfigure(2, weight=0)
        self.window.columnconfigure(3, weight=0)

        # Placement  in grid
        self.window.grid()
        self.note_color.grid(row=0, column=0)
        self.on_top.grid(row=0, column=1)
        self.new_note.grid(row=0, column=2)
        self.map_note.grid(row=0, column=3)
        self.note_payload.grid(row=1, column=0, columnspan=4, sticky="nsew")

        # Lift window
        self.window.lift()

# NoteDB ------
# v0.0.19 - text has to resize to window for platform compatibility
#         - this makes a mess of the grid
# v0.1.00 - release


class NoteManager:
    # Jobs:
    #  Manage files - initial open, updates
    #  Manage note windows - initial open, raise/lower, close/reopen

    def delete_note(self, note_data, filename="notes.db"):
        connection = sqlite3.connect("notes.db")
        cursor = connection.cursor()
        old_note_name = note_data[3]
        old_note_name = [old_note_name]
        cursor.execute("""DELETE FROM notes WHERE title = ?""", old_note_name)
        connection.commit()
        connection.close()
        print("Removing note DB and from list of running notes")
        # we delete, this notes entry, its not running, move this to SQL?
        del self.note_window_map[str(note_data[3])]

    def update_note(self, note_data, filename="notes.db"):
        # Scenario: user clicked new note, then changed name to some note that
        #           already exists.  We could overwrite old note (nope data
        #            loss is bad) we can ignore and drop them back to their
        #            note, maybe somehow changing the name?
        print(self.note_window_map[note_data[3]])

        connection = sqlite3.connect(filename)
        cursor = connection.cursor()
        cursor.execute(
         """UPDATE notes SET title = ?, note = ?, color = ? WHERE title = ?""",
          note_data
        )
        connection.commit()
        connection.close()

        self.note_window_map[str(note_data[3])] = None  # No Obj = not running?
        print("Removed note from list of running notes")

    def recreate_note(self, named_note, filename='notes.db'):
    # whatever name we are passed, check we don't have an object
    # already, then create object and assign note to it

        #check if exists already, we don't want 2 of the same notes on screen
        print("DEBUG: pre validation named_note is " + named_note)

        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        print("DEBUG: named_note is " + named_note)
        named_note = [named_note]  # we need to be a list, otherwise
                                   # our note is treated as N, O, T, E

        cursor.execute(
            """SELECT title, note, color FROM notes WHERE title = ?""",
            named_note
        )
        note = cursor.fetchone()

        # Just in case something went wrong
        if note is None:
            print("Note name " + named_note[0] + " not found in attempting to find a match")

        # lets try find that note anyway
        for note in self.note_window_map.keys():
            if len(note.split(" ")) > 1:  # If stored title has a space in it
                if named_note[0] in note:  # compare it with the passed value
                    print("Found note named, '" + note + "' recreating this")
                    named_note[0] = note
                    break

        cursor.execute(
            """SELECT title, note, color FROM notes WHERE title = ?""",
            named_note
        )
        note = cursor.fetchone()
        connection.close()

        # Just in case something went wrong again, bail out nicely!
        if note is None:
            print("Note name " + named_note[0] + " not found, attempting to find a match")
            return

        # Now we have some certainty what the user wants, lets figure out if its
        # already running, if it is bail out, otherwise we will create it.
        if self.note_window_map[named_note[0]] is not None:
            print(named_note[0] + " is already running, Ignoring Request")
            return

        # this will make the window and assign it to the dictionary
        self.note_window_map[named_note[0]] = NoteWindow(
                list(self.note_window_map.keys()),
                note[0],  # Key + Title
                note[1],  # note/text/payload
                note[2]   # color
        )
        self.note_window_map[named_note[0]].window.lift()
        self.note_window_map[named_note[0]].note_payload.focus()

    def create_new_note(self, note_data, filename='notes.db'):
        # if the requested not already exists, bail out nicely
        if note_data[0] in list(self.note_window_map.keys()):
            print(note_data[0] + ": already exists, lifting")
            self.note_window_map[note_data[0]].window.lift()
            return

        # We will be passed a list with 4 values in note_data
        # Pull this out as title, text, color, visible
        connection = sqlite3.connect("notes.db")
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO notes VALUES(?, ?, ?, ?)""", note_data)
        connection.commit()

        # Backend, add to map while also creating the GUI
        self.note_window_map[note_data[0]] = ''
        self.note_window_map[note_data[0]] = NoteWindow(
                list(self.note_window_map.keys()),
                note_data[0],  # Key + Title
                note_data[1],  # note/text/payload
                note_data[2],  # color
            )

    def create_all_notes(self, filename='notes.db'):
        note_titles = []
        note_definitions = []

        connection = sqlite3.connect(filename)
        cursor = connection.cursor()
        for results_line in cursor.execute(
            """SELECT title, note, color, visible FROM notes"""
        ):
            note_titles.append(results_line[0])   # used for keys
            note_definitions.append(results_line)  # to create the actual note
        connection.close()

        # Initalize our dictionary with the note names as keys
        dict_of_notes = dict.fromkeys(note_titles, '')

        # Assign created object for windows x,
        # to the value for key x in the dictionary
        for note in note_definitions:
            if note[3] != 0:  # note should be visible
                dict_of_notes[note[0]] = NoteWindow(
                    note_titles,
                    note[0],  # Key + Title
                    note[1],  # note/text/payload
                    note[2]   # color
                )
        return dict_of_notes  # all done

    def __init__(self, filename='notes.db'):
        print("Note Manager: Started")
        print("Note Manager: Creating notes and map")
        self.note_window_map = self.create_all_notes(filename)
        print("Note Manager: Notes and mapping, Created")

# Note Manager
notebook = 'notes.db'
server = NoteManager(notebook)

# Display Warning
tkMessageBox.showinfo(title="v0.0.19", message="Fix before Release")

# Mk Win, start loop, kill that window.
hidden = Tkinter.Tk()
hidden.destroy()
hidden.mainloop()
print("Note Manager: Exiting")
