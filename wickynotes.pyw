#!/usr/bin/env python

# try, python2 imports, then try python3 imports #tkftw
from __future__ import print_function
import sqlite3
try:
    from Tkinter import *
    from ttk import *
    from tkMessageBox import *
except ImportError:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.messagebox import *


class NoteWindow:
    # Jobs
    ## This is going to be the GUI object for each note, it will display the
    ## note and all the widgets needed.  We will call backend app functions
    ## when we need to read/write something at an app level

    def create_note(self, named_note, event):
    # GUI:
        print("GUI: Create Note")
        print(self.title + ": Wants to recreate a note named: ", end='')
        print(named_note)
        print("Calling NoteManger to recreate this note")
    # Backend:
        recreate_note(named_note)

    def master_close(self, event=''):
        # IN-PROGRESS
        print("Attempt to kill the master window")

    def master_note(self, event=''):
        # Debug output and and variable setup
        print("Master Note")

        note_list = []
        master_text = 'All Notes\n\n'

        # Get all the note names for later display as note text
        for note in list(self.new_note_list()):
            master_text = master_text + note + '\n'

        # GUI, draw window
        master = NoteWindow(note_list, 'Master', master_text, 'Green')
        master.note_color.config(state='disabled')
        master.new_note.config(state='disabled')
        master.map_note.config(state='disabled')
        master.note_payload.tag_configure('bold', font='helvetica 10 bold')
        master.note_payload.tag_add('bold', '3.0', 'end')  # tag all the text
        return master

    def click_linked(self, event=''):
        # GUI, get the clicked word by extending selection
        word_start = self.note_payload.index('current wordstart')
        word_end = self.note_payload.index('current wordend')
        word = self.note_payload.get(word_start, word_end)
        print(self.title + ": User clicked " + word)

        # Check for a match regardless of case or space in the name
        for key in list(self.new_note_list()):
            if word.upper() in key.upper().split(" "):
                word = key
                break

        # GUI, lift, if already running.  If not call backend to make it again.
        if note_window_map[word] is not None:
            print (word + ": exists")
            print(word + ": lifted")
            note_window_map[word].window.lift()
        else:
            print (word + ": is closed, Recreating")
            self.create_note(word, event)

        self.refresh_note(list(note_window_map.keys()))

    def click_htext(self, event=''):
        # TEST/DEBUG function
        if self.title == 'Master':
            return
        else:
            print(self.title + " htext")
            self.refresh_note(list(self.new_note_list()))

    def click_newnote(self, event=''):
        # DEBUG, output who is requesting the note
        print(self.title + ": Requested new note")

        # GUI, grab title from selection, put it in head and body, white color
        if self.note_payload.tag_ranges('sel'):
            # New note set from selection
            note_data = [
                self.note_payload.get('sel.first', 'sel.last'),
                self.note_payload.get('sel.first', 'sel.last'),
                'White', 1
            ]
            print(self.title + ": Creating Note, " + note_data[0])
        else:
            # New note set to these defaults
            note_data = ['Note Title', 'Note Title', 'White', 1]
            print(self.title + ": no text highlighted.  Creating default note")

        # Backend, make the note as specified
        create_new_note(note_data)
        print(self.title + ": Note Created")
        self.refresh_note(list(self.new_note_list()))

    def note_close(self):
        # GUI, Master is special case, its not in the DB so just destroy it.
        if self.title == 'Master':
            self.window.destroy()
            return

        # Debug: We will be saving the note contents on exit, update db unless
        #        title is blank, then delete the note outright
        old_note_name = self.title
        new_note_name = self.note_payload.get('1.0', '1.end')

        window_count = 0  # if > 1 close window, if == 1 quit app

        # possible for user to change the name to the same name as a
        # note that exists already. We need to block this
        for key in list(self.new_note_list()):
            print(new_note_name + ' : ' + key)
            if note_window_map[key] is not None:
                window_count = window_count + 1
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
        if new_note_name != '':              # Backend, title exist. Save
            update_note(note_data)
            print(self.title + ": Saved")
        else:                                  # Backend, title is blank. Del
            delete_note(note_data)
            print(self.title + ": Deleted")

        print("Window count is : " + str(window_count))
        if window_count != 1:
            self.window.destroy()  # Destroy a window
        else:
            self.window.quit()  # Quit app

    def set_sticky(self):
        # GUI, whatever we get passed (0 or 1) flip it
        if self.StayOnTop == 0:
            self.StayOnTop = 1
            self.window.wm_attributes('-topmost', True)
        else:
            self.StayOnTop = 0
            self.window.wm_attributes('-topmost', False)

    def init_colors(self, note_bg):
        # sets initial value of the variable used for the Combobox
        # iterates through entries counting, when we get to the right
        # number for example 3rd on list is Yellow, return 2
        i = 0
        for color in self.note_color.cget('values'):
            if color != note_bg:
                i = i + 1
            else:
                return(i)

    def colors(self, event=''):
        # Set the Text background color to one of the colors listed in Combobox
        self.note_payload.config(bg=self.note_color.get())

    def refresh_note(self, note_titles=['To Do']):
        # Header
        self.note_payload.tag_configure('header',
                                        font='helvetica 12 underline bold')
        self.note_payload.tag_add('header', '1.0', '1.end')
        self.note_payload.tag_bind('header', '<Button-1>', self.click_htext)

        # regular text!
        self.note_payload.tag_configure('normal',
                                        font='helvetica 10')

        # setup the tag, and clear out whatever we already have
        self.note_payload.tag_configure('bold', font='helvetica 10 bold')
        self.note_payload.tag_remove('bold', '2.0', 'end')
        self.note_payload.tag_add('normal', '2.0', 'end')

        for title in note_titles:
            start = 2.0  # Line 1 is a header, skip it
            while 1:
                word_start = self.note_payload.search(
                    title,
                    start,
                    stopindex='end',
                    nocase=True
                )
                # find char number for the line, if line 2 then 2.x
                word_end = word_start.split(".")
                if len(word_end) > 1:
                    tmp = word_end[0] + '.' + str(int(word_end[1]) + len(title))
                    word_end = tmp
                if not word_start:
                    break  # This will happen eventually, breaking the loop
                self.note_payload.tag_remove('normal', word_start, word_end)
                self.note_payload.tag_add('bold', word_start, word_end)
                start = word_start + "+1c"

        # Flag that we have done our thing, so we get notified if anything
        # happens again, that means we have to scan again.
        self.note_payload.edit_modified(False)

    def new_note_list(self):
        note_titles = []
        connection = sqlite3.connect("notes.db")
        cursor = connection.cursor()
        for results_line in cursor.execute(
            """SELECT title, note, color, visible FROM notes"""
        ):  # << Sad beans
            note_titles.append(results_line[0])  # names of notes to highlight
        connection.close()
        #print(note_titles)
        return note_titles

    def __init__(self, note_names, note_title, note_text='', note_bg=''):
        # Make a window with the title provided when instance was created.
        self.note_names = note_names
        self.master = ""
        self.ComboVar = ""
        self.StayOnTop = 0
        self.title = note_title

        self.window = Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.note_close)
        self.window.title(note_title)
        self.window.resizable(1, 1)
        self.window.minsize(400, 240)
        self.window.geometry('405x300')

        self.window.bind('<FocusIn>',
             lambda event: self.refresh_note(self.new_note_list())
        )
        self.window.bind('<Enter>',
            lambda event: self.refresh_note(self.new_note_list())
        )

        # Components
        ## Header Options
        self.note_color = Combobox(
            self.window,
            values=('Yellow', 'Pink', 'Cyan', 'White', 'Red'),
            state='readonly',
            textvariable=self.ComboVar
            )
        self.note_color.bind('<<ComboboxSelected>>', self.colors)
        self.ComboVar = self.init_colors(note_bg)
        self.note_color.current(self.ComboVar)

        self.on_top = Checkbutton(
            self.window,
            text="On Top",
            variable=self.StayOnTop,
            command=self.set_sticky
            )

        self.new_note = Button(
            self.window,
            text="New Note",
            underline=0,
            command=self.click_newnote
            )

        self.map_note = Button(
            self.window,
            text="All Notes",
            underline=0,
            command=self.master_note
            )

        ## Main window
        self.note_payload = Text(
            master=self.window,
            width=60,
            height=17,
            wrap='word',
            state='normal'
            )
        self.note_payload.config(bg=note_bg)
        self.note_payload.insert("end", note_text)

        self.note_payload.tag_bind('bold', '<Button-1>', self.click_linked)
        #self.refresh_note(list(note_window_map.keys()))
        self.note_payload.bind('<<Modified>>',
                lambda event: self.refresh_note(self.new_note_list())
                )
        self.note_payload.edit_modified(False)

        # Key Bindings
        self.window.bind_all('<Alt-n>', self.click_newnote)
        self.window.bind_all('<Alt-a>', self.master_note)

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
# v0.1  - Prototype: highlight code not working perfectly
# v0.2  - Prototype: PEP8 compliance and fixes to highlighting code
# v0.3  - Refactor: preperation for single class rebuild.
#       - Refactor: imports are cleaner, namespace is tidy.
#
# v0.4  - Rewrite: Single class, some functions outside the class for db access
#       - Rewrite: Comments updated to reflect recent changes
#       - Rewrite: Intial window is real, not a throwaway window, prevents ttk
#       -          themechange error output on startup
#       - ReWrite: Regular and bold font are same font family


def delete_note(note_data, filename="notes.db"):
    # Scenario: User has deleted all the text in a note and closes the note.
    #           We treat this as a delete.  We are going to let the GUI window
    #           that called us clean up itself, this function will clean up
    #           the database and objects associated with the note.
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()
    old_note_name = note_data[3]
    old_note_name = [old_note_name]
    cursor.execute("""DELETE FROM notes WHERE title = ?""", old_note_name)
    connection.commit()
    connection.close()
    print("Removing note DB and from list of running notes")
    del note_window_map[str(note_data[3])]


def update_note(note_data, filename="notes.db"):

    # Scenario: user clicked changed the name of the note they where looking at
    #           manage situation if it already exists.
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()
    cursor.execute(
     """UPDATE notes SET title = ?, note = ?, color = ? WHERE title = ?""",
      note_data
    )
    connection.commit()
    connection.close()

    note_window_map[str(note_data[3])] = None  # blank it?
    del note_window_map[str(note_data[3])]  # destroy it
    print("Removed note from list of running notes")
    note_window_map[str(note_data[0])] = None  # add another


def recreate_note(named_note, filename='notes.db'):
    # Scenario: User clicked a linked note name, if it exist, lift, if not
    #           go to the DB, get it and pass it to the create note function

    connection = sqlite3.connect(filename)
    cursor = connection.cursor()

    named_note = [named_note]  # we need to be a list, otherwise
                               # our note is treated as N, O, T, E

    cursor.execute(
        """SELECT title, note, color FROM notes WHERE title = ?""",
        named_note
    )
    note = cursor.fetchone()

    # Just in case something went wrong with the SQL
    if note is None:
        print("Note name " + named_note[0] + " not found attempting search")

    # lets try find that note anyway, if we get a partial match
    for note in list(note_window_map.keys()):
        if len(note.split(" ")) > 1:    # If stored title has a space in it
            if named_note[0] in note:   # compare it with the passed value
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
        print("Note name " + named_note[0] + " not found can't recreate")
        return

    # Assuming we got a match: and its running bail out
    if note_window_map[named_note[0]] is not None:
        print(named_note[0] + " is already running, Ignoring Request")
        return

    # Assuming we got a match: and it not runining recreate it
    note_window_map[named_note[0]] = NoteWindow(
            list(note_window_map.keys()),
            note[0],  # Key + Title
            note[1],  # note/text/payload
            note[2]   # color
    )
    note_window_map[named_note[0]].window.lift()
    note_window_map[named_note[0]].note_payload.focus()


def create_new_note(note_data, filename='notes.db'):
    # if the requested not already exists, bail out nicely
    if note_data[0] in list(note_window_map.keys()):
        print(note_data[0] + ": already exists, lifting")
        note_window_map[note_data[0]].window.lift()
        return

    # We will be passed a list with 4 values in note_data
    # Pull this out as title, text, color, visible
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO notes VALUES(?, ?, ?, ?)""", note_data)
    connection.commit()

    # Backend, add to map while also creating the GUI
    note_window_map[note_data[0]] = ''
    note_window_map[note_data[0]] = NoteWindow(
            list(note_window_map.keys()),
            note_data[0],  # Key + Title
            note_data[1],  # note/text/payload
            note_data[2],  # color
        )


def create_all_notes(filename='notes.db'):
    # Scenario: should only be called when the app start and in theory if we
    #           add the ability to change file/noteboot in future.  Get all
    note_titles = []
    note_definitions = []

    connection = sqlite3.connect(filename)
    cursor = connection.cursor()
    for results_line in cursor.execute(
        """SELECT title, note, color, visible FROM notes"""
    ):
        note_titles.append(results_line[0])    # used for keys
        note_definitions.append(results_line)  # to create the actual note
    connection.close()

    # Initalize our dictionary with the note names as keys
    dict_of_notes = dict.fromkeys(note_titles, '')

    # Assign created object for window x,
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

# ----------------------------------------------------------------------------
# Main application
# ----------------------------------------------------------------------------

filename = 'notes.db'
print("Note Manager: Creating notes and map")
note_window_map = create_all_notes(filename)
print("Note Manager: Notes and mapping, Created")

# Display Warning
showinfo(title="v0.4", message="Re-written")

# MAINLOOP against whatever note is currently index 0 in the dictionary
note_window_map[list(note_window_map.keys())[0]].window.mainloop()

# When the last note is closed do the following
print("Note Manager: Exiting")
