import tkinter as tk
from tkinter import ttk
from config import DBI
from donationBanner import *
from dataclasses import dataclass,fields,field
from collections import namedtuple
from Barcode_Scanner_Entries import *
from Google_Sheets_Interface import *

# note:
# You can insert just an asset tag and it will go into the beta.donatedgoods table
# having PC ID NULL and HD ID NULL. It will not be in the reports though in their
# current iteration.

@dataclass(order=True,frozen=True)
class NonBarcode_Vals:
    donation_id: int = None
    staff_name: str = "staff:"
    type_name: str = "device type:"
    quality_name: str = "quality:"
    # pks : list[int] =field(default_factory=list)

# this class here determines the entries part of the gui.
# you can add another label and entry row
# by editing this class and adding another row here you can (need to debug) add
# another entry (or subtract one) from the array below.
@dataclass(order=True,frozen=True)
class Barcode_Vals:
    pc_id: str = None
    pc_sn: str = None
    hd_id: str = None
    hd_sn: str = None
    asset_tag: str = None

@dataclass(frozen=True)
class Full_Form:
    pc_id: str = None
    pc_sn: str = None
    hd_id: str = None
    hd_sn: str = None
    asset_tag: str = None
    donation_id: int = None
    staff_name: str = "staff:"
    type_name: str = "device type:"
    quality_name: str = "quality:"

# id, p_id,hd_id,donation_id;
# this is the order of keys that comes outta the insert device query
# whenever you hit insert.
# note that from dg you can derive the others by querying the db
@dataclass(frozen=True)
class Table_Keys:
    dg: str = None
    pcs: str = None
    hds: str = None
    donations: str = None

@dataclass(frozen=True)
class UpdateSql:
    msg : str = None
    args : tuple[str] = field(default_factory=tuple)

class InsertDeviceType(tk.Frame,DBI):
    # this class is the new device type pop up
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.dtdd = kwargs['DTDD']
        self.typeVar = kwargs['typeVar']
        self.type = tk.Entry(parent,fg='black',bg='white',width=25)
        self.insertTypeButton = tk.Button(parent,
            text='insert',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertTypeButton.bind('<Button-1>',self.insertType)
        self.typeLabel=tk.Label(parent,text="new type:").grid(row=0,column=0)
        self.type.grid(row=0,column=1)
        self.insertTypeButton.grid(row=1,column=1)
    def insertType(self,event):
        self.insertToDB(DeviceInfo.insertNewDeviceType,self.type.get())
        self.refreshDTOptionMenu()
        self.parent.destroy()
    def refreshDTOptionMenu(self):
        self.dtdd['menu'].delete(0,'end')
        deviceTypes = self.fetchall(DeviceInfo.getDeviceTypes)
        for type in deviceTypes:
            self.dtdd['menu'].add_command(label=type[0],
                command=tk._setit(self.typeVar,type[0]))
class InsertDrives(tk.Frame,DBI):
    def __init__(self,parent,Barcode_Vals,*args,**kwargs):
        self.parent = parent
        self.ini_section=kwargs['ini_section']
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self)
        self.donationID = kwargs['donationID']
        self.google_sheets=UpdateSheets(self,
                            donation_id=self.donationID.get(),
                            ini_section=self.ini_section)
        self.lastDevice=kwargs['lastDevice_info']
        self.lastDevice_nonBarCode=kwargs['lastDevice_nonBarCode']
        self.sheet_id = kwargs['sheet_id_var']
        deviceTypes = self.fetchall("SELECT deviceType FROM beta.deviceTypes;")
        dtypes =[type[0] for type in deviceTypes]
        self.typeName = tk.StringVar(parent,value="device type:")
        self.typeDD = tk.OptionMenu(parent,self.typeName,"device type:",*dtypes)
        deviceQualities = self.fetchall("SELECT q.quality FROM beta.qualities q;")
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        getStaff = \
        """
        SELECT name
        FROM beta.staff
        WHERE active=TRUE;
        """
        stafflist = self.fetchall(getStaff)
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        ROW=0
        tk.OptionMenu(parent,self.staffName,"staff:",*snames).grid(row=ROW,column=0)
        self.entries=BarcodeScannerMode(parent,ROW,Barcode_Vals)
        row_count = self.entries.get_rowcount()
        self.entries.grid(row=ROW,columnspan=2,rowspan=row_count)
        ROW+=row_count
        ROW+=1
        self.qualityDD.grid(row=ROW,column=0)
        self.typeDD.grid(row=ROW,column=1)
        ROW+=1
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).grid(row=ROW,column=0)
        self.insertDeviceButton = tk.Button(parent,
            text='insert',
            width = 10,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDeviceButton.bind('<Button-1>',self.insertDevice)
        self.insertHDButton = tk.Button(parent,
            text='another HD',
            width = 10,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertHDButton.bind('<Button-1>',self.insert_HD)
        self.insertDeviceTypeButton = tk.Button(parent,
            text='new Type',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDeviceTypeButton.bind('<Button-1>',self.NewDTPopUp)
        ROW+=1
        self.insertDeviceTypeButton.grid(row=ROW,column=0)
        self.insertDeviceButton.grid(row=ROW,column=1)
        self.insertHDButton.grid(row=ROW,column=2)
        ROW+=1
        tk.Label(parent,text="last entries:").grid(row=ROW,column=0) #consider including a columnspan
        tk.Label(parent,text="Computer").grid(row=ROW,column=1)
        tk.Label(parent,text="HD").grid(row=ROW,column=2)
        ROW+=1
        tk.Label(parent,textvariable=self.lastDevice.pc_id).grid(row=ROW,column=1)
        tk.Label(parent,textvariable=self.lastDevice.hd_id).grid(row=ROW,column=2)
        ROW+=1
        tk.Label(parent,textvariable=self.lastDevice.pc_sn).grid(row=ROW,column=1)
        tk.Label(parent,textvariable=self.lastDevice.hd_sn).grid(row=ROW,column=2)
    def NewDTPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        InsertDeviceType(popUp,ini_section=self.ini_section,
            DTDD =self.typeDD,typeVar=self.typeName)
    def get_vals_from_form(self):
        # this method still needs to be cleaned up and generalized in order to
        # use the Barcode Scanner Entries general concept of entries
        donationID = self.donationID.get()
        if len(donationID) == 0:
            self.err.set("Please select a donation.")
            return self

        staff = self.staffName.get()
        if staff == "staff:":
            self.err.set('please select staff member')
            return self

        type = self.typeName.get()
        if type == "device type:":
            self.err.set('please select (or insert) device type')
            return self

        quality = self.qualityName.get()
        if quality == "quality:":
            quality = None
            #consider forcing a quality choice here as done above with staff and type.
        if self.entries.pc_id.index("end") < 2:
            pc_id = None
        else:
            pc_id = self.entries.pc_id.get()
            if not (pc_id[:2] == 'MD' or pc_id[:2] == 'md'):
                self.err.set('please provide a pid that begins with "MD"')
                return self
            if pc_id[-1] == " " or pc_id[-1] == "\`":
                self.err.set('please remove trailing space or tick from pid.')
                return self

        if self.entries.pc_sn.index("end") < 2:
            pc_sn = None
        else:
            pc_sn = self.entries.pc_sn.get()
            if pc_id is None:
                self.err.set("Please provide a PC ID with Computer SN or clear Computer Serial Entry.")
                return self
            if pc_sn[0] == " " or pc_sn[0] == "\`" or pc_sn[-1] == " " or pc_sn[-1] =="\`":
                self.err.set('please provide a valid device serial or clear the form. Check for an extra space at the end of the entry or something..')
                return self
        if self.entries.hd_id.index("end") < 2:
            hd_id=None
        else:
            hd_id = self.entries.hd_id.get()
            if hd_id[0] == " " or hd_id[0]== "\`" or hd_id[-1] == " " or hd_id[-1]== "\`":
                self.err.set('please provide a valid hard drive id or clear the entry')
                return self
        if self.entries.hd_sn.index("end") < 2:
            hd_sn = None
        else:
            hd_sn = self.entries.hd_sn.get()
            if hd_id is None:
                self.err.set("Please provide a HD ID with Hard Drive or clear Hard Drive Serial Entry.")
                return self
            if hd_sn[0] == " " or hd_sn[0]== "\`" or hd_sn[-1] == " " or hd_sn[-1]== "\`":
                self.err.set('please provide a valid hard drive serial or clear the entry. Check the beginning and end of the serial number for an extra space or something.')
                return self

        if self.entries.asset_tag.index("end") != 0:
            asset_tag = self.entries.asset_tag.get()
            if asset_tag[0] == " " or asset_tag[0] =="\`" or asset_tag[-1] == " " or asset_tag[-1]== "\`":
                self.err.set('Please provide a valid asset tag. Check the beginning and end of the serial number for an extra space or something.')
                return self
        else:
            asset_tag = None
        return (donationID,asset_tag,pc_id,pc_sn,hd_id,hd_sn,staff,type,quality)
    def insert_device_sql(self,submitted_form):
        insertDevice = \
        """
        DROP TABLE IF EXISTS user_inputs;
        CREATE TEMP TABLE user_inputs(
            type_id integer,
            pc_sn VARCHAR(20),
            hd_sn VARCHAR(20),
            pc_id VARCHAR(20),
            hd_id VARCHAR(20),
            asset_tag VARCHAR(255),
            quality_id integer,
            staff_id integer,
            intake_date timestamp,
            donation_id integer,
            pc_table_id INTEGER,
            hd_table_id INTEGER
            );
        INSERT INTO user_inputs(
            donation_id,
            asset_tag,
            pc_id,
            pc_sn,
            hd_id,
            hd_sn,
            staff_id,
            type_id,
            quality_id,
            intake_date
	    )
        VALUES (
            %s,
            %s,
            TRIM(LOWER(%s)),
            TRIM(LOWER(%s)),
            TRIM(LOWER(%s)),
            TRIM(LOWER(%s)),
            (SELECT s.staff_id FROM beta.staff s WHERE s.name =%s),
            (SELECT dt.type_id FROM beta.deviceTypes dt WHERE dt.deviceType = %s),
            (SELECT quality_id from beta.qualities where quality = %s),
            NOW()
        );
        with device_info as ({}), harddrive_info as ({})
        UPDATE user_inputs
            SET pc_table_id = (select pc_table_id from device_info),
                hd_table_id = (select hd_table_id from harddrive_info);
        select pc_table_id,hd_table_id from user_inputs;
        INSERT INTO beta.donatedgoods(donation_id,pc_id,hd_id,intakedate,assettag,staff_id)
            SELECT donation_id,pc_table_id,hd_table_id,intake_date,asset_tag,staff_id
            FROM user_inputs
        RETURNING id,donation_id;
        """
            #note that I'm leaving blank from the update the SN
            # so that we can just scan the pid to add an additional HD
            #also note that when there is a harddrive conflict
            #the hdsn isnt updated
        if submitted_form.pc_id is not None:
            #recall that above we confirmed that
            #the computer serial number cannot be entered without a PC ID
            #however, a PC ID can be entered without a PC SN
            computer_insert = \
            """
            INSERT INTO beta.computers(pid,sn,type_id,quality_id)
                SELECT pc_id,pc_sn,type_id, quality_id
                    FROM user_inputs
            ON CONFLICT (pid) DO UPDATE
                SET quality_id = beta.computers.quality_id
            RETURNING pc_id as pc_table_id
            """
        else:
            #  the ::int casts the NULL value to an integer,
            #  necessary to do, otherwise postgres tries to insert the string "null"
            #  into an integer column and sends back a fail message
            computer_insert = "SELECT NULL::int AS pc_table_id"
        if submitted_form.hd_id is not None:
            #recall that above we confirmed that
            #the hard drive serial number cannot be entered without a HD ID
            #however, a HD ID can be entered without a HD SN
            hd_insert = \
            """
            INSERT INTO beta.harddrives(hdpid,hdsn)
                SELECT hd_id,hd_sn
                    FROM user_inputs
            ON CONFLICT (hdpid) DO UPDATE
                SET hdsn = beta.harddrives.hdsn
            RETURNING hd_id as hd_table_id
            """
        else:
            hd_insert = "SELECT NULL::int as hd_table_id"
        return insertDevice.format(computer_insert,hd_insert)
    def insertDevice_hotkey(self):
        self.insertDevice(None)
    def insertDevice(self,event):
        args = self.get_vals_from_form()
        submitted_headers= NonBarcode_Vals(args[0],args[6],args[7],args[8])
        submitted_form=Barcode_Vals(args[2],args[3],args[4],args[5],args[1])
        try:
            out=self.fetchone(self.insert_device_sql(submitted_form),*args)
            try:
                self.lastDevice.table_keys = Table_Keys(*out)
                self.conn.commit()
                self.google_sheets.donation_id=out[1]
                self.google_sheets.overWrite_sanitization()
                #note: next line is breaking.
                self.update_last_device_log(out,submitted_form,submitted_headers)
                self.clear_form()
                self.entries.pc_id.focus()
                self.err.set("success!")
            except:
                self.err.set('That PC ID or HD ID entered has been entered before. Try another.')
            finally:
                pass
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
            print(error)
        finally:
            return self
    def insert_HD(self,event):
        args = self.get_vals_from_form()
        submitted_headers= NonBarcode_Vals(args[0],args[6],args[7],args[8])
        submitted_form=Barcode_Vals(args[2],args[3],args[4],args[5],args[1])
        try:
            out=self.fetchone(self.insert_device_sql(submitted_form),*args)
            try:
                self.lastDevice.table_keys = Table_Keys(*out)
                self.conn.commit()
                self.google_sheets.donation_id=out[1]
                self.google_sheets.overWrite_sanitization()
                #note: next line is breaking.
                self.update_last_device_log(out,submitted_form,submitted_headers)
                self.clear_HD_form()
                self.entries.pc_id.focus()
                self.err.set("success!")
            except:
                self.err.set('That PC ID or HD ID entered has been entered before. Try another.')
            finally:
                pass
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
            print(error)
        finally:
            return self
    def update_gsheet(self,row):
        append_to_sheet(self.sheet_id.get(),[row])
    def update_last_device_log(self,ids,submitted_form,submitted_headers):
        for key in self.lastDevice.get_entryfield_names():
            getattr(self.lastDevice,key).set(getattr(submitted_form,key))
        Entry_Vals_Fields = fields(submitted_headers)
        EV_field_names = [Entry_Vals_Field.name for Entry_Vals_Field in Entry_Vals_Fields]
        for key in EV_field_names:
            getattr(self.lastDevice_nonBarCode,key).set(getattr(submitted_headers,key))
        #self.lastDevice.pks=ids
        return self
    def clear_form(self):
        for key in self.entries.get_entryfield_names():
            getattr(self.entries,key).delete(0,'end')
        return self
    def clear_HD_form(self):
        # Needs to be generalized.
        for key in self.entries.get_entryfield_names():
            if key != 'pc_id' and key != 'pc_sn':
                getattr(self.entries,key).delete(0,'end')
        return self

class Review(InsertDrives):
    def __init__(self,parent,Barcode_Vals,*args,**kwargs):
        self.parent = parent
        self.ini_section=kwargs['ini_section']
        self.donationID=kwargs['donationID']
        self.dg_id=None
        self.google_sheets=UpdateSheets(self,
                            donation_id=self.donationID.get(),
                            ini_section=self.ini_section)
        InsertDrives.__init__(self,self.parent,Barcode_Vals,
            ini_section=kwargs['ini_section'],
            donationID=kwargs['donationID'],
            sheet_id_var=kwargs['sheet_id_var'],
            lastDevice_info=kwargs['lastDevice_info'],
            lastDevice_nonBarCode=kwargs['lastDevice_nonBarCode'])
        self.insertDeviceButton['text']='Update'
        self.entries.pc_id['bg']='gray'
        self.entries.hd_id['bg']='gray'
        self.entries.bind_or_unbind(None)

        self.repopulate_form = tk.Button(parent,
            text='Get Last Submission',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.repopulate_form.bind('<Button-1>',self.repop_with_previous_row)
        self.repopulate_form.grid()
    def repop_with_previous_row(self,event):
        if self.donationID.get():
            self._dg_id_update()
        else:
            print('no donation selected')
            self.err.set('Please Select Donation.')
            return self
        get_previous_row_sql = \
        """
        SELECT COALESCE(c.pid,''),COALESCE(c.sn,''),COALESCE(hd.hdpid,''),COALESCE(hd.hdsn,''),
               COALESCE(dg.assetTag,''),dg.donation_id,s.name,dt.devicetype,q.quality
        FROM beta.donatedgoods dg
        LEFT OUTER JOIN beta.staff s ON dg.staff_id=s.staff_id
        LEFT OUTER JOIN beta.harddrives hd USING (hd_id)
        LEFT OUTER JOIN beta.computers c USING (pc_id)
        LEFT OUTER JOIN beta.devicetypes dt USING (type_id)
        LEFT OUTER JOIN beta.qualities q USING (quality_id)
        WHERE dg.donation_id = %s
        AND dg.id = %s;
        """
        row_back = self.fetchone(get_previous_row_sql,self.donationID.get(),self.dg_id)
        if row_back and len(row_back) >0:
            self.update_last_device_log(None,Barcode_Vals(*row_back[:5]),NonBarcode_Vals(*row_back[5:]))
            self.repopulate()
            self.google_sheets.donation_id=self.donationID.get()
            self.google_sheets.overWrite_sanitization()
        else:
            self.err.set('No Rows Found')
            self.dg_id=1e8
        return self
    def repopulate(self):
        self.clear_form()
        for key in self.lastDevice.get_entryfield_names():
            getattr(self.entries,key).insert(0,getattr(self.lastDevice,key).get())
        self.staffName.set(self.lastDevice_nonBarCode.staff_name.get())
        self.typeName.set(self.lastDevice_nonBarCode.type_name.get())
        self.qualityName.set(self.lastDevice_nonBarCode.quality_name.get())
        #getattr(self.entries,key).insert(0,getattr(self.lastDevice_nonBarCode,key).get())
        return self
    def _dg_id_update(self):
        getNextID = \
        """
        SELECT max(id)
        FROM beta.donatedgoods
        WHERE donation_id = %s
        and id < %s;
        """
        if not self.dg_id:
            self.dg_id=1e8
        dg_id_tup = self.fetchone(getNextID,self.donationID.get(),self.dg_id)
        if dg_id_tup and len(dg_id_tup) == 1:
            self.dg_id = dg_id_tup[0]
        else:
            self.dg_id=None
        return self
    def insertDevice(self,event):
        if not self.dg_id:
            self._dg_id_update()
        nonBarcode_Commands=tuple()
        donatedgoods_vals = tuple()
        donatedgoods_command=str()
        donatedgoods_command += "Update beta.donatedgoods "
        idChange=False
        isChanged=False
        if self.donationID.get() != self.lastDevice_nonBarCode.donation_id.get():
            isChanged=True
            donatedgoods_command += "SET donation_id= %s "
            donatedgoods_vals+= (self.donationID.get(),)
            idChange=True
        if self.staffName.get() != self.lastDevice_nonBarCode.staff_name.get():
            isChanged=True
            if idChange:
                donatedgoods_command+=', '
            else:
                donatedgoods_command+='SET '
            donatedgoods_command += "staff_id=(SELECT staff_id from beta.staff where name = %s) "
            donatedgoods_vals+= (self.staffName.get(),)
        donatedgoods_command+="Where id=%s" + ';'
        donatedgoods_vals +=(self.dg_id,)
        donatedgoods_sql = UpdateSql(donatedgoods_command,donatedgoods_vals)
        if isChanged:
            nonBarcode_Commands+=(donatedgoods_sql,)
            isChanged=False
        computers_vals=tuple()
        computers_command=str()
        computers_command+="UPDATE beta.computers "
        typeChange=False
        if self.typeName.get() != self.lastDevice_nonBarCode.type_name.get():
            isChanged=True
            computers_command += "SET type_id=(SELECT type_id from beta.devicetypes where devicetype = %s)"
            computers_vals+=(self.typeName.get(),)
            typeChange=True
        if self.qualityName.get() != self.lastDevice_nonBarCode.quality_name.get():
            isChanged=True
            if typeChange:
                computers_command+=', '
            else:
                computers_command+='SET '
            computers_command += "quality_id=(SELECT quality_id from beta.qualities where quality = %s)" + ' '
            computers_vals+=(self.qualityName.get(),)
        computers_command+="WHERE pc_id=(SELECT pc_id from beta.donatedgoods where id = %s);"
        computers_vals +=(self.dg_id,)
        if isChanged:
            isChanged=False
            nonBarcode_Commands +=(UpdateSql(computers_command,computers_vals),)

        barcode_commands=tuple()
        if getattr(self.entries,'pc_id').index('end') !=0 and len(getattr(self.lastDevice,'pc_id').get())==0:
            if getattr(self.entries,'pc_sn').index('end') !=0:
                pcs_command ="""
                WITH pc_update as (
                    INSERT INTO beta.computers(pid,sn)
                    VALUES(%s,%s)
                    RETURNING pc_id
                )
                UPDATE beta.donatedgoods
                SET pc_id = (SELECT pc_id from hd_update)
                WHERE id=%s;
                """
                pcs_vals = tuple([getattr(self.entries,'hd_id').get(),getattr(self.entries,'hd_sn').get(),self.dg_id])
            else:
                pcs_command ="""
                WITH pc_update as (
                    INSERT INTO beta.computers(pid)
                    VALUES(%s)
                    RETURNING pc_id
                )
                UPDATE beta.donatedgoods
                SET pc_id = (SELECT pc_id from hd_update)
                WHERE id=%s;
                """
                pcs_vals = tuple([getattr(self.entries,'hd_id').get(),self.dg_id])
            barcode_commands+=(UpdateSql(pcs_command,pcs_vals),)
        if getattr(self.entries,'pc_sn').get() !=getattr(self.lastDevice,'pc_sn').get():
            computers_command ="""
            Update beta.computers
            SET sn = %s
            WHERE pc_id =
                (SELECT pc_id
                 FROM beta.donatedgoods
                 WHERE id=%s);
            """
            computers_vals = tuple([getattr(self.entries,'pc_sn').get(),
                                    self.dg_id])
            barcode_commands+=(UpdateSql(computers_command,computers_vals),)
        if getattr(self.entries,'hd_id').index('end') !=0 and len(getattr(self.lastDevice,'hd_id').get())==0:
            if getattr(self.entries,'hd_sn').index('end') !=0:
                hds_command ="""
                WITH hd_update as (
                    INSERT INTO beta.harddrives(hdpid,hdsn)
                    VALUES(%s,%s)
                    RETURNING hd_id
                )
                UPDATE beta.donatedgoods
                SET hd_id = (SELECT hd_id from hd_update)
                WHERE id=%s;
                """
                hd_vals = tuple([getattr(self.entries,'hd_id').get(),getattr(self.entries,'hd_sn').get(),self.dg_id])
            else:
                hds_command ="""
                WITH hd_update as (
                    INSERT INTO beta.harddrives(hdpid)
                    VALUES(%s)
                    RETURNING hd_id
                )
                UPDATE beta.donatedgoods
                SET hd_id = (SELECT hd_id from hd_update)
                WHERE id=%s;
                """
                hd_vals = tuple([getattr(self.entries,'hd_id').get(),self.dg_id])
            barcode_commands+=(UpdateSql(hds_command,hd_vals),)
        if getattr(self.entries,'hd_sn').get() !=getattr(self.lastDevice,'hd_sn').get():
            hds_command ="""
            Update beta.harddrives
            SET hdsn = %s
            WHERE hd_id =
                (SELECT hd_id
                 FROM beta.donatedgoods
                 WHERE id=%s);
            """
            hd_vals = tuple([getattr(self.entries,'hd_sn').get(),self.dg_id])
            barcode_commands+=(UpdateSql(hds_command,hd_vals),)
        if getattr(self.entries,'asset_tag').get() !=getattr(self.lastDevice,'asset_tag').get():
            dg_command ="""
            Update beta.donatedgoods
            SET assettag = %s
            WHERE id =%s;
            """
            dg_vals = tuple([getattr(self.entries,'asset_tag').get(),self.dg_id])
            barcode_commands+=(UpdateSql(dg_command,dg_vals),)
        for sql in nonBarcode_Commands + barcode_commands:
            out=self.insertToDB(sql.msg,*sql.args)
        get_previous_row_sql = \
        """
        SELECT COALESCE(c.pid,''),COALESCE(c.sn,''),COALESCE(hd.hdpid,''),COALESCE(hd.hdsn,''),
               COALESCE(dg.assetTag,''),dg.donation_id,s.name,dt.devicetype,q.quality
        FROM beta.donatedgoods dg
        LEFT OUTER JOIN beta.staff s ON dg.staff_id=s.staff_id
        LEFT OUTER JOIN beta.harddrives hd USING (hd_id)
        LEFT OUTER JOIN beta.computers c USING (pc_id)
        LEFT OUTER JOIN beta.devicetypes dt USING (type_id)
        LEFT OUTER JOIN beta.qualities q USING (quality_id)
        WHERE dg.donation_id = %s
        AND dg.id = %s;
        """
        row_back = self.fetchone(get_previous_row_sql,self.donationID.get(),self.dg_id)
        if row_back and len(row_back) >0:
            self.update_last_device_log(None,Barcode_Vals(*row_back[:5]),NonBarcode_Vals(*row_back[5:]))
        self.google_sheets.donation_id=self.donationID.get()
        self.google_sheets.overWrite_sanitization()

class extractionGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        donationIDVar = tk.StringVar(parent)
        sheet_id_var=tk.StringVar(parent)
        lastDevice_nonBarCode=Entry_Form(parent,None,NonBarcode_Vals,TO_GENERATE='VARIABLES ONLY')
        lastDevice = Entry_Form(parent,None,Barcode_Vals,TO_GENERATE='VARIABLES ONLY')
        DonationBanner(parent,
            ini_section=kwargs['ini_section'],
            sheet_id_var=sheet_id_var,
            donationIDVar = donationIDVar)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        Obj=InsertDrives(self.tab1,Barcode_Vals,
            ini_section=kwargs['ini_section'],
            sheet_id_var=sheet_id_var,
            donationID=donationIDVar,
            lastDevice_info=lastDevice,
            lastDevice_nonBarCode=lastDevice_nonBarCode)
        # note: binding is working on root
        # root is special for keybinding -- no matter where your "focus",
        # i.e. cursor, is this key will trigger this action.
        # Because we're inserting a form here, we could be shooting blanks and
        # need to account for that.
        # You can pass root as an arg or kwarg to classes to give them the power to
        # change the root binding, or google about it and you can adjust keybindings
        # based on focus and more.
        parent.bind('<Control-space>',Obj.insertDevice)
        self.tab2 = ttk.Frame()
        Review(self.tab2,Barcode_Vals,
            ini_section=kwargs['ini_section'],
            donationID=donationIDVar,
            sheet_id_var=sheet_id_var,
            lastDevice_info=lastDevice,
            lastDevice_nonBarCode=lastDevice_nonBarCode)
            #sheetID = self.sheetIDVar)
        # GenerateReport(self.tab3,
        #     ini_section=kwargs['ini_section'],
        #     donationID=self.donationIDVar)
        self.add(self.tab1,text="Insert New Drives.")
        self.add(self.tab2,text="Review Submissions")
        #self.add(self.tab3,text="Generate Report")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hard Drive Extraction Station")
    app = extractionGUI(root,ini_section='local_launcher')
    app.mainloop()
