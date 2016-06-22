# wickynotes

__"Wicky Notes"__ is a sticky notes app with "wiki" features.

Any note title will show up as a link in other notes. For example if you have a note called "To Do" and another note called "Groceries" when you write groceries on your to do list, it will become a link to the groceries note automatically. You can use this to go to that note even if it is closed.

__Change a note:__
Simply change the note as you wish, the first line of your note will become the new title. When you close the note it will be saved.

__Delete a note:__
Simply open the note, delete the contents (including title) and close the note. Its gone from that point forward.

__About:__
I wrote this as I was learning python and Tk.  Tk as that ships with python and is available just about everywhere that python is. It uses a simple sqlite3 file for storage. Theoretically you could place this app on cloud storage and use it from any PC (Windows/Linux/Mac/BSD). If you can reach the script and the notes.db file, it will work.

__History:__
* 28/3/2015: v0.1 Prototype, mostly functional, tested on Windows 8.1 and Arch Linux under MATE and Gnome3.
* 30/3/2015: v0.2 Dynamic links working now, previous code required restarts. Some code has been changed to comply with PEP8.
* 1/4/2015: v0.3 Final prototype, everything works as it should, code has been cleaned up in some areas. Next version will be written from the ground up using lessons learned from this prototype stage. But you can use this version all day without issue.
* 4/4/2015: v0.4 Single class, some functions outside the class for db access.  Comments updated to reflect recent changes. Initial window is real, not a throwaway window, prevents ttk themechange error output on start up
