import tkinter as tk
from tkinter import ttk
from config import DBI
import sql
class demo(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationID=3
        self.pack(pady=20)
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        headers = cols.split('\t')
        ttreeCols=tuple([i for i in range(1,len(headers)+1)])
        print(len(headers))
        print(headers)
        print(ttreeCols)
        self.tv = ttk.Treeview(self, columns=ttreeCols, show='headings', height=8,width=30)
        self.tv.pack(side=tk.LEFT)
        iter=1
        for header in headers:
            self.tv.heading(iter,text=header)
            iter+=1
        #self.tv.heading(1, text="name")
        #self.tv.heading(2, text="eid")
        #self.tv.heading(3, text="Salary")

        sb = tk.Scrollbar(self, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tv.config(yscrollcommand=sb.set)
        sb.config(command=self.tv.yview)
        self.sqlToTTree()
        self.insertDummyCols()
        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")
        getdotTxt = tk.Button(parent,
            text='Generate New Report',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        #getdotTxt.bind('<Button-1>',self.createTextFile)
        getdotTxt.pack()
    def sqlToTTree(self):
        devices = self.fetchall(sql.Report.deviceInfo,self.donationID)
        drive = [1]
        report = []
        for device in devices:
            dlist = list(device)
            try:
                dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
            except:
                pass
            finally:
                report.append(tuple(drive + dlist))
                drive[0]+=1
        self.report=tuple(report)
    def insertDummyCols(self):
        tv=self.tv
        for row in self.report:
            self.tv.insert(parent='',index=row[0]-1,iid=row[0]-1,values=row)
        # tv.insert(parent='', index=0, iid=0, values=("vineet", "e11", 1000000.00))
        # tv.insert(parent='', index=1, iid=1, values=("anil", "e12", 120000.00))
        # tv.insert(parent='', index=2, iid=2, values=("ankit", "e13", 41000.00))
        # tv.insert(parent='', index=3, iid=3, values=("Shanti", "e14", 22000.00))
        # tv.insert(parent='', index=4, iid=4, values=("vineet", "e11", 1000000.00))
        # tv.insert(parent='', index=5, iid=5, values=("anil", "e12", 120000.00))
        # tv.insert(parent='', index=6, iid=6, values=("ankit", "e13", 41000.00))
        # tv.insert(parent='', index=7, iid=7, values=("Shanti", "e14", 22000.00))
        # tv.insert(parent='', index=8, iid=8, values=("vineet", "e11", 1000000.00))
        # tv.insert(parent='', index=9, iid=9, values=("anil", "e12", 120000.00))
        # tv.insert(parent='', index=10, iid=10, values=("ankit", "e13", 41000.00))
        # tv.insert(parent='', index=11, iid=11, values=("Shanti", "e14", 22000.00))

if __name__ == '__main__':
    root = tk.Tk()
    root.title("PythonGuides")
    demo(root,ini_section='local_appendage')
    root.mainloop()
