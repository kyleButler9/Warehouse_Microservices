from config import DBI;
import psycopg2
class Conn(DBI):
    def __init__(self,*args,**kwargs):
        DBI.__init__(self,ini_section = kwargs['ini_section'])
def write_csv(vals,filename='stss_deviceSNs.txt'):
    try:
        f=open(filename,'w')
        for row in vals:
            for item in row:
                f.write(item)
                if item !=row[-1]:
                    f.write(',')
            f.write('\n')
            f.close()
    except Exception("Failed to write csv."):
        print('inputs was\n',vals)
    return None
if __name__ == "__main__":
    conn = Conn(ini_section='local_launcher')
    sql = """
    select serialnumber,productkey from beta.licenses;
    """
    try:
        res=conn.fetchall(sql)
        write_csv(res,'stss_deviceSNs.txt')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    print('Script Completed "Successfully."')
