import psycopg2
from config import config

# improvements include:
#   creating a variable to hold "beta" so that schema of different names
#   can easily be deployed

TEST_COMMAND = ('SELECT 1',)
def batchExecuteSqlCommands(ini_section,commands=TEST_COMMAND):
    conn = None
    try:
        # read the connection parameters
        params = config(ini_section=ini_section)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

class DBAdmin:
    createTableCommands = (
        """
        CREATE SCHEMA beta;
        """,
        """
        CREATE TABLE beta.recipients (
            recipient_id SERIAL PRIMARY KEY,
            complete Boolean,
            name VARCHAR(255),
            address VARCHAR(255),
            notes VARCHAR(255)
        );
        """,
        """
        CREATE TABLE beta.donors(
            donor_id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            address VARCHAR(255)
        );
        """,
        """
        CREATE TABLE beta.donations (
            donation_id SERIAL PRIMARY KEY,
            donor_id INTEGER NOT NULL,
            lotNumber bigint UNIQUE,
            dateReceived timestamp,
            sheetID varchar(100),
            numwiped INTEGER DEFAULT 0,
            report Boolean DEFAULT FALSE,
            FOREIGN KEY (donor_id)
                REFERENCES beta.donors (donor_id)
        );
        """,
        """
        CREATE TABLE beta.staff (
            staff_id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            password VARCHAR(100),
            active Boolean,
            nameabbrev VARCHAR(100)
        );
        """,
        """
        CREATE TABLE beta.licenses (
            license_id SERIAL PRIMARY KEY,
            serialNumber VARCHAR(100) UNIQUE,
            productKey VARCHAR(100),
            entry_time timestamp,
            staff_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES beta.staff (staff_id)
        );
        """,
        """
        CREATE TABLE beta.pallets (
            pallet_id SERIAL PRIMARY KEY,
            pallet INTEGER,
            recipient_id INTEGER NOT NULL,
            FOREIGN KEY (recipient_id)
                REFERENCES beta.recipients (recipient_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE beta.qualities (
            quality_id SERIAL PRIMARY KEY,
            quality VARCHAR(15)
        );
        """,
        """
        CREATE TABLE beta.deviceTypes (
            type_id SERIAL PRIMARY KEY,
            deviceType VARCHAR(15)
        );
        """,
        """
        CREATE TABLE beta.harddrives(
            hd_id SERIAL PRIMARY KEY,
            hdpid VARCHAR(25) UNIQUE NOT NULL,
            hdsn VARCHAR(100),
            destroyed Boolean default FALSE,
            sanitized Boolean default FALSE,
            model VARCHAR(100),
            size VARCHAR(20),
            wipedate Timestamp,
            staff_id INTEGER,
            license_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES beta.staff (staff_id),
            FOREIGN KEY (license_id)
                REFERENCES beta.licenses (license_id)
        );
        """, #note no unique constraint on hdsn
        """
        create table beta.computers(
            pc_id SERIAL PRIMARY KEY,
            pid VARCHAR(20) UNIQUE,
            quality_id INTEGER,
            type_id INTEGER not null,
            sn varchar(100),
            license_id INTEGER,
            FOREIGN KEY (quality_id) REFERENCES beta.qualities (quality_id),
            FOREIGN KEY (type_id) REFERENCES beta.devicetypes (type_id),
            FOREIGN KEY (license_id) REFERENCES beta.licenses (license_id)
        );
        """, #note that there isn't a unique constraint on device sn but there is on the pid
        """
        create table beta.donatedgoods(
            id SERIAL PRIMARY KEY,
            donation_id INTEGER NOT NULL,
            pc_id INTEGER,
            hd_id INTEGER UNIQUE,
            staff_id INTEGER NOT NULL,
            intakedate timestamp NOT NULL,
            assettag VARCHAR(255),
            FOREIGN KEY (pc_id) REFERENCES beta.computers (pc_id),
            FOREIGN KEY (hd_id) REFERENCES beta.harddrives (hd_id),
            FOREIGN KEY (staff_id) REFERENCES beta.staff (staff_id)
        );
        """,
        """
        CREATE TABLE beta.qualitycontrol(
            qc_id SERIAL PRIMARY KEY,
            hd_id INTEGER,
            staff_id INTEGER,
            qcDate timestamp,
            donation_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES beta.staff (staff_id),
            FOREIGN KEY (donation_id)
                REFERENCES beta.donations (donation_id),
            FOREIGN KEY (hd_id)
                REFERENCES beta.harddrives (hd_id)
        );
        """,
        """
        CREATE TABLE beta.missingparts(
            mp_id SERIAL PRIMARY KEY,
            quality VARCHAR(20),
            resolved Boolean,
            issue VARCHAR(255),
            notes VARCHAR(255),
            pc_id INTEGER,
            pallet VARCHAR(20),
            FOREIGN KEY (pc_id)
                REFERENCES beta.computers (pc_id)
        );
        """,
        """
        CREATE TABLE beta.internet (
            internet_id SERIAL PRIMARY KEY,
            hotspot_meid VARCHAR(25)
        );
        """,
        """
        CREATE TABLE beta.refurbishedDevices(
            device_id SERIAL PRIMARY KEY,
            pc_id INTEGER,
            hd_id INTEGER,
            internet_id INTEGER,
            FOREIGN KEY (pc_id)
                REFERENCES beta.computers (pc_id),
            FOREIGN KEY (hd_id)
                REFERENCES beta.harddrives (hd_id),
            FOREIGN KEY (internet_id)
                REFERENCES beta.internet (internet_id)
        );
        """,
        """
        CREATE TABLE beta.distributedDevices (
            distdev_id SERIAL PRIMARY KEY,
            internet_id INTEGER,
            device_id INTEGER,
            recipient_id INTEGER NOT NULL,
            pallet_id INTEGER,
            FOREIGN KEY (internet_id)
                REFERENCES beta.internet (internet_id),
            FOREIGN KEY (device_id)
                REFERENCES beta.refurbishedDevices (device_id),
            FOREIGN KEY (recipient_id)
                REFERENCES beta.recipients (recipient_id),
            FOREIGN KEY (pallet_id)
                REFERENCES beta.pallets (pallet_id)
        );
        """,
    )

    initializeDatabaseCommands = (
        """
        INSERT INTO beta.qualities(quality)
        VALUES('Fair'),('Good'),('Better'),('Best');
        """,
        """
        INSERT INTO beta.deviceTypes(deviceType)
        VALUES('Laptop'),('Desktop'),('Loose HD'),('Unknown');
        """,
        """
        INSERT INTO beta.donors(name)
        VALUES('Individual Donor');
        """,
        """
        INSERT INTO beta.donations(datereceived,donor_id,lotNumber)
        VALUES('12/25/2020',
            (SELECT donor_id
            FROM beta.donors
            WHERE name = 'Individual Donor'),0)
        """,
        """
        INSERT INTO beta.staff(name,active,nameabbrev)
        VALUES('Kyle Butler',TRUE,'kbutler');
        """,
        """
        ALTER TABLE beta.donatedgoods add UNIQUE (pc_id,hd_id)
        """,
    )
    dropTablesCommands = (
    """
    DROP TABLE if exists beta.qualitycontrol;
    """,
    """
    DROP TABLE IF EXISTS beta.donatedgoods;
    """,
    """
    DROP TABLE if exists beta.donations;
    """,
    """
    DROP TABLE if exists beta.donors;
    """,
    """
    DROP TABLE if exists beta.distributedDevices;
    """,
    """
    DROP TABLE IF EXISTS beta.refurbishedDevices;
    """,
    """
    DROP table if exists beta.missingparts;
    """,
    """
    DROP TABLE IF EXISTS beta.computers;
    """,
    """
    DROP TABLE if exists beta.qualities;
    """,
    """
    DROP TABLE if exists beta.devicetypes;
    """,
    """
    DROP TABLE IF EXISTS beta.harddrives;
    """,
    """
    DROP TABLE if exists beta.staff;
    """,
    """
    DROP TABLE if exists beta.licenses;
    """,
    """
    DROP TABLE IF EXISTS beta.internet;
    """,
    """
    DROP TABLE if exists beta.pallets;
    """,
    """
    DROP TABLE if exists beta.recipients;
    """,
    """
    DROP SCHEMA IF EXISTS beta CASCADE;
    """,
    )
if __name__ == '__main__':

    # This app instantiates a new PostgreSQL database.

    # In order to run, replace "local_launcher" below with the header of the .ini file
    # section.

    # For future development, consider compiling a CLI app that takes as input
    # a <example_path>.ini file path.

    #batchExecuteSqlCommands('local_launcher',commands=DBAdmin.dropTablesCommands)
    #print('deleted beta schema.')
    batchExecuteSqlCommands('local_launcher',commands=DBAdmin.createTableCommands)
    batchExecuteSqlCommands('local_launcher',commands=DBAdmin.initializeDatabaseCommands)
