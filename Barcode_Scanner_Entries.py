import tkinter as tk
from config import DBI
import datetime
from os import system
from datetime import datetime,timedelta
from dataclasses import dataclass,field,fields
import time

THRESHOLD=100 #MAKE THRESHOLD SMALLER OR LARGER TO ADJUST BARCODE MODE

class Entry_Form(tk.Frame):
    def __init__(self,parent,ROW,Entry_Vals,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent,*args)
        # note that we're ignoring the pks list with the [:-1] below
        #      that we're using the Entry_Vals object to determine the fields in the Entry Form
        self.Entry_Vals_Fields = fields(Entry_Vals)# [:-1]
        self.EV_field_names = [Entry_Vals_Field.name for Entry_Vals_Field in self.Entry_Vals_Fields]
        self.row_count=len(self.EV_field_names)
        if 'TO_GENERATE' in kwargs:
            switch = kwargs['TO_GENERATE']
        else:
            switch = None
        if not switch or switch == 'ENTRIES ONLY':
            for key in self.EV_field_names:
                setattr(self,key,tk.Entry(parent,fg='black',bg='white',width=25))
        elif switch == 'ENTRIES AND VARIABLES':
            for key in self.EV_field_names:
                # use the below code to assign stringvars also to the entries
                string_var=None
                string_var=tk.StringVar(parent)
                setattr(self,key,tk.Entry(parent,fg='black',bg='white',width=25,textvariable=string_var))
                setattr(self,key+'_var',string_var)
        elif switch == 'VARIABLES ONLY':
            for key in self.EV_field_names:
                string_var=None
                string_var=tk.StringVar(parent)
                setattr(self,key,string_var)
        if switch != 'VARIABLES ONLY':
            self._grid(ROW,switch)
    def _grid(self,ROW,switch,LABEL_COLUMN=0,ENTRY_COLUMN=1):
        for key in self.EV_field_names:
            tk.Label(self.parent,text=key.replace("_"," ")+":").grid(row=ROW,column=LABEL_COLUMN)
            getattr(self,key).grid(row=ROW,column=ENTRY_COLUMN)
            ROW+=1
        return self
    def get_rowcount(self):
        return self.row_count
    def get_entry_fields(self):
        return self.Entry_Vals_Fields
    def get_entryfield_names(self):
        return self.EV_field_names

# this object will be used to enable toggling between keyboard and barcode scanner modes of input
class BarcodeScannerMode(Entry_Form):
    #note: this class is not finished. It still needs help
    # tasks: need to add consideration of backspace key to ignore it
    # right now, backspace key causes two characters erasures when scanner mode engaged
    # also, need to set threshold
    def __init__(self,parent,ROW,Entry_Vals,*args,**kwargs):
        self.parent=parent
        # this button toggles between Keyboard mode and Scanner mode.
        self.Button = tk.Button(parent,
            text='Scanner Mode',
            width = 15,
            height = 2,
            bg = "BLACK",
            fg = "WHITE",
        )
        self.Button.bind('<Button-1>',self.bind_or_unbind)
        self.Button.grid(row=ROW,column=1)
        ROW+=1
        Entry_Form.__init__(self,parent,ROW,Entry_Vals,*args,**kwargs)
        # Entry_Form adds to self the attributes: self.row_count, self.EV_field_names,...
        self.grid(row=ROW,columnspan=2,rowspan=self.row_count)
        self.Pressed = dict()
        self.initialize_bindings()
    def initialize_bindings(self):
        try:
            for name in self.EV_field_names:
                getattr(self,name).bind("<KeyPress>",self.keydown)
                getattr(self,name).bind("<KeyRelease>",self.keyup)
                self.Pressed[getattr(self,name)]=dict()
                setattr(self,name+'_keys',dict())
        except AttributeError as err:
            print(err)
            print('You need to run this method after initializing Entry_Form.')
    def bind_or_unbind(self,event):
        # if the button says keyboard mode, then start scanner mode
        # and rename the button
        if self.Button['text'] == 'Keyboard Mode':
            for name in self.EV_field_names:
                getattr(self,name).bind("<KeyPress>",self.keydown)
                getattr(self,name).bind("<KeyRelease>",self.keyup)
            self.Button['text'] = 'Scanner Mode'
        elif self.Button['text'] == 'Scanner Mode':
            for name in self.EV_field_names:
                getattr(self,name).bind("<KeyPress>",self.human_keydown)
                getattr(self,name).bind("<KeyRelease>",self.human_keyup)
            self.Button['text'] = 'Keyboard Mode'
    def keydown(self,e):
        try:
            if self.Pressed[e.widget][e.char]:
                e.widget.delete(len(e.widget.get())-1,tk.END)
            else:
                self.Pressed[e.widget][e.char]=datetime.now()
        except KeyError:
                self.Pressed[e.widget][e.char]=datetime.now()
        return self
    def human_keydown(self,e):
        return self
    def keyup(self,e):
        # if the key is held down for too long,
        # i.e. as long as a keyboard keypress by a human takes,
        # then delete the last.
        #tasks: need to add consideration of backspace key to ignore it
        NOW=datetime.now()
        try:
            WHEN_PRESSED=self.Pressed[e.widget][e.char]
            if WHEN_PRESSED:
                if (NOW - WHEN_PRESSED).microseconds > THRESHOLD:
                    e.widget.delete(len(e.widget.get())-1,tk.END)
                self.Pressed[e.widget][e.char]=None
            else:
                for widget in self.Pressed.keys():
                    try:
                        WHEN_PRESSED=self.Pressed[widget][e.char]
                        if WHEN_PRESSED:
                            if (NOW - WHEN_PRESSED).microseconds > THRESHOLD:
                                widget.delete(len(widget.get())-1,tk.END)
                            self.Pressed[widget][e.char]=None
                    except KeyError:
                         self.Pressed[widget][e.char]=None
        except KeyError:
            for widget in self.Pressed.keys():
                try:
                    WHEN_PRESSED=self.Pressed[widget][e.char]
                    if WHEN_PRESSED:
                        if (NOW - WHEN_PRESSED).microseconds > THRESHOLD:
                            widget.delete(len(widget.get())-1,tk.END)
                        self.Pressed[widget][e.char]=None
                except KeyError:
                     self.Pressed[widget][e.char]=None

    def human_keyup(self,e):
        return self


# this class here determines the entries part of the gui.
# you can add another label and entry row
# by merely editing this class and adding another row there
@dataclass(order=True,frozen=True)
class Entry_Vals_Main:
    pc_id: str = None
    pc_sn: str = None
    hd_id: str = None
    hd_sn: str = None
    asset_tag: str = None
if __name__ == "__main__":
    #when you run the script, actually only this stuff below runs. Everything above was definitions. Within definitions you instantiate other things you've defined,
    #but its all just definitions! Up until the stuff below.
    #this first line is basic for all tkinter GUI creation. this "root" becomes "parent" in the classes defined above.
    root = tk.Tk()
    #here we set the top banner of the app. We can also mess with the geometry, etc. of the GUI by other root.[some stuff]
    root.title("Barcodes")
    #here we instantiate the SNPK class (which itself instantiates the other classes and so on, so forth)
    #ini_section is the section that has the DB info in the .ini file
    app = BarcodeScannerMode(root,0,Entry_Vals_Main)
    #this just runs the GUI. And we're off!
    app.mainloop()
# class DD_Form(tk.Frame):
#     def __init__(self,parent,ROW,Entry_Vals,*args,**kwargs):
#         self.parent=parent
#         tk.Frame.__init__(self,parent,Entry_Vals,*args)
#         # note that we're ignoring the pks list with the [:-1] below
#         #      that we're using the Entry_Vals object to determine the fields in the Entry Form
#         self.Entry_Vals_Fields = fields(Entry_Vals)# [:-1]
#         self.EV_field_names = [Entry_Vals_Field.name for Entry_Vals_Field in self.Entry_Vals_Fields]
#         self.row_count=len(self.EV_field_names)
#         for key in self.EV_field_names:
#             string_var=None
#             string_var=tk.StringVar(parent)
#             setattr(self,key,string_var)
#         self._grid(ROW,switch)
#     def get_rowcount(self):
#         return self.row_count
#     def get_entry_fields(self):
#         return self.Entry_Vals_Fields
#     def get_entryfield_names(self):
#         return self.EV_field_names
