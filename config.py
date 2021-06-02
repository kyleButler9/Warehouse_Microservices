from configparser import ConfigParser
import psycopg2
#   config returns a dictionary
def config(ini_file='database.ini', ini_section='local_launcher'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(ini_file)
    # get section, default to postgresql
    db = {}
    if parser.has_section(ini_section):
        params = parser.items(ini_section)
        for param in params:
            db[param[0]] = param[1]
    elif len(parser.read(ini_file)) == 0:
        raise Exception("No {0} in same directory as {1}".format(ini_file,__name__))

    else:
        raise Exception('Section {0} not found in the {1} file'.format(ini_section, ini_file))
    return db
RETRY_CONNECTION_MAX_COUNT = 5
SCHEMA = "beta"
class DBI:
    def __init__(self,**kwargs):
        # at the start of every scession need to run "set search_path = beta;"
        # then you can drop beta. everywhere
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
        self.schema=SCHEMA
        self.connectToDB(self.ini_section)

    def connectToDB(self,ini_section,try_count = 0):
        try:
            # read database configuration
            if self.conn: #is not None
                self.conn.close()
            params = config(ini_section=ini_section)
            self.conn = psycopg2.connect(**params)
            self.cur = self.conn.cursor()
            set_search_path = \
            """
            SET search_path=%s;
            SHOW search_path;
            """.format(SCHEMA)
            self.cur.execute(set_search_path,SCHEMA)
            self.conn.commit()
            if self.cur.fetchone()[0][0] != SCHEMA:
                if try_count < RETRY_CONNECTION_MAX_COUNT:
                    print('failed conn or search_path setting to ',SCHEMA,try_count,'times.')
                    try_count+=1
                    # this function recursively calls itself here to reattempt the connection
                    self.connectToDB(ini_section,try_count)
                else:
                    print('failed conn or search_path setting to ',SCHEMA,try_count,'times.'
                    print('No more attempts... check cable.')
            else:
                print(self.cur.fetchone(), '<< result from search path setting to',SCHEMA)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.conn = None
        finally:
            return self
    def restartConnection(self,ini_section):
        print('\nretrying connection...')
        self.connectToDB(self.ini_section)
    def insertToDB(self,sql,*args):
        try:
            cur = self.conn.cursor()
            if len(args) != 0:
                cur.execute(sql,(*args,))
            else:
                cur.execute(sql)
            try:
                out=cur.fetchone()
            except:
                out='success!'
            finally:
                cur.close()
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print('\nretrying connection...')
            self.restartConnection(self.ini_section)
            try:
                cur = self.conn.cursor()
                if len(args) != 0:
                    cur.execute(sql,(*args,))
                else:
                    cur.execute(sql)
                out=cur.fetchone()
                cur.close()
                self.conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                out=error
            finally:
                pass
        finally:
            return out
    def fetchone(self,sql,*args):
        #returns one tuple
        try:
            if self.testConnection() == 0:
                self.restartConnection(self.ini_section)
            self.cur = self.conn.cursor()
            if len(args) != 0:
                self.cur.execute(sql,(*args,))
            else:
                self.cur.execute(sql)
            return self.cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None

    def fetchall(self,sql,*args):
        #returns a list of tuples
        if self.testConnection() == 0:
            self.restartConnection(self.ini_section)
        if len(args) != 0:
            self.cur.execute(sql,(*args,))
        else:
            self.cur.execute(sql)
        return self.cur.fetchall()
    def testConnection(self):
        try:
            self.cur.execute("SELECT 1")
            back = self.cur.fetchone()[0]
        except:
            back = 0
        finally:
            return back
if __name__ == "__main__":
    DBI = DBI(ini_section='local_launcher')
    from datetime import datetime
    from sql import *
    now =datetime.now()
    DBI.cur.execute(testConnection)
    print(len(DBI.cur.fetchall()))
