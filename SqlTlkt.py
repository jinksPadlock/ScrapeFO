import pyodbc
import uuid


class SqlTlkt:

    def __init__(self, s, db, p, u, pw):
        # Connection example: Windows, without a DSN, using the Windows SQL Server driver
        cxnStr = 'DRIVER={SQL Server Native Client 11.0}' +\
                 ';SERVER=' + s +\
                 ';PORT=' + p +\
                 ';DATABASE=' + db +\
                 ';UID=' + u +\
                 ';PWD=' + pw + ';'
        self.cnxn = pyodbc.connect(cxnStr)

    def set_conn(self, c):
        self.cnxn = c

    def run_query(self, strSQL, p=[]):
        cursor = self.cnxn.cursor()
        if p is None:
            cursor.execute(strSQL)
        else:
            cursor.execute(strSQL, p)
        self.cnxn.commit()

    def insert_get_id(self, strSQL, p=[]):
        try:
            cursor = self.cnxn.cursor()
            if p is None:
                cursor.execute(strSQL)
            else:
                cursor.execute(strSQL, p)
            cursor.execute("SELECT SCOPE_IDENTITY()")

            row = cursor.fetchone()
            row_id = row[0]
            self.cnxn.commit()
            return row_id
        except:
            return None

    def get_sql_list(self, strSQL, p=[]):
        cursor = self.cnxn.cursor()
        if p is None:
            cursor.execute(strSQL)
        else:
            cursor.execute(strSQL, p)
        rows = cursor.fetchall()
        if rows:
            return rows
        else:
            return None

    def get_uuid(self):
        return uuid.uuid1()

