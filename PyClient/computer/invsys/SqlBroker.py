import sqlite3
import os

class SqlBroker:
    """
    This class is designed to be used only with InvSys.
    """

    def __init__(self, fp=None, debug=False):
        self.__debug=debug
        self._sqlfp = fp
        self.__conn = None
        self.__c = None

    @property
    def sqlfp(self):
        return self._sqlfp

    def exists(self):
        return os.path.exists(self._sqlfp)

    def fp(self,fp=None):
        self._sqlfp = fp

    def open(self):
        if not self._sqlfp:
            raise ConnectionRefusedError("No Filepath ever declared")

        if self.__conn or self.__c:
            return

        self.__conn = sqlite3.connect(self.sqlfp)
        self.__c = self.__conn.cursor()

    def close(self):
        if not self.__conn:
            return

        self.__c.close()
        self.__conn.close()

        self.__conn = self.__c = None

    def execute(self,*args):
        try:
            if self.__debug:
                print(*args)
            return self.__c.execute(*args)
        except:
            self.close()
            raise

    def commit(self):
        if self.__debug:
            print("Commit")
        self.__conn.commit()

    def create_module_table(self):
        # Create one
        self.open()
        c = self.__c

        # Create the config table
        query = 'CREATE TABLE config ' \
                '(property VARCHAR(100) PRIMARY KEY, ' \
                'value VARCHAR(200))'
        self.execute(query)

        # Create the config table
        query = 'CREATE TABLE modules ' \
                '(module VARCHAR(100) PRIMARY KEY)'
        self.execute(query)

        self.commit()

        self.close()

    def dump_config_to_db(self,tmr,config):
        """
        Dump configuration to local db
        :param tmr: time of operation
        :return:
        """
        # Get the database
        self.open()

        # General insert for configuration items
        query = 'INSERT OR REPLACE INTO config (property, value) VALUES (?, ?)'

        # Save configuration to sql table
        for i in config:
            opts = [i, config[i]]

            self.execute(query, opts)
            self.commit()

        # Update lastupdate case
        opts = ['lastupdate', str(tmr)]
        self.execute(query, opts)
        self.commit()

        # Close connections
        self.close()

    def config(self):
        self.open()

        # Get all of the results from the remote database
        res = self.execute('SELECT * FROM config').fetchall()

        self.close()

        config = {}

        # Apply them
        for i in res:
            config[i[0]] = i[1]

        return self.typeify_config(config)

    def cidsid(self, module, cid, sid):
        self.open()

        self.execute("UPDATE "+module+" SET sid = '"+sid+"' WHERE cid == '"+cid+"'")

        self.commit()

        self.close()

    def syncmodule(self, module, sid, tmr):
        self.open()

        #rows = self.execute('SELECT * FROM '+module+' WHERE sid == "'+sid+'"')

        #for row in rows.fetchall():
        #    self.sync(module, row[0], sid, tmr)

        query = ("UPDATE ",module,
                 " SET sync_date = '",str(tmr),
                 "' WHERE sid == '"+sid+"'")
        self.execute("".join(query))

        self.commit()

        #self.sync(module, '%%', sid, tmr)
        # self.execute("UPDATE "+module+" SET sync_date = '"+tmr+"' WHERE sid == '"+cid+"'")

        self.close()

    def sync(self, module, property, sid, tmr):
        query = ("UPDATE ",module,
                 " SET sync_date = '",str(tmr),
                 "' WHERE sid == '"+sid+"' and property == '"+property+"'")

        self.execute("".join(query))

        self.commit()

    def typeify_config(self, config):
        """
        Helper for our code to have the configuration in the types we want it in, str is default
        :return:
        """
        types = {
            'lastupdate': float,
            'hbt': int,
            'backoff': int,
            'forceHTTPS': bool,
            'client_id': str,
            'apikey': str,
            'keypub': str
        }

        for attr in config:
            if attr in types:
                config[attr] = types[attr](config[attr])

        return config
