# Temp imports
import sys

# Software imports
from . import RequestAPI
from . import Logger
from . import Software
from . import SqlBroker

# Imports
import sqlite3
import time
import os.path
import json
import urllib.request
import urllib.error
import urllib.parse
import collections


def flatten(d, parent_key='', sep='_'):
    """
    Flatten dictionary to single depth
    :param d: dictionary
    :param parent_key:
    :param sep:
    :return:
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class InvSys(Software.Software):
    """
    Lits Virtual Inventory Software
    """

    @property
    def request(self):
        """
        Provide a request helper that returns the api object
        :return:
        """
        return RequestAPI.RequestApi

    @property
    def sql(self):
        return self._sqlbroker

    @property
    def client_id(self):
        """
        TODO: Get the client_id of the system
        :return:
        """
        self.sql.open()
        # self.sql.execute('SELECT `client_id` FROM identifiers WHERE')
        self.sql.close()
        return None

    def sql_filepath(self):
        """
        Generate the sql filepath for this specific installation
        :return:
        """
        return os.path.join(self.config['sqlstore'], self._kernel.get_serial()) + ".db3"

    def __init__(self):
        """
        Initialize the software
        :return:
        """
        self._kernel = None
        self._initialized = False
        self._sqlbroker = None

        super().__init__()

    def install(self, fs, *args):
        """
        Create an instance of the installed software and return,

        Additional arguments required [0] -> System Kernel
        :param fs: FileSystem instance
        :param args: Additional arguments passed to this installation
        :return:
        """
        super().install(fs)

        self._kernel = args[0]

        # Initialize the SQL Broker
        self._sqlbroker = SqlBroker.SqlBroker(debug=True)

        return self

    def start(self):
        """
        Virtually start the software
        :return:
        """
        config = json.loads(self._filesystem.getfile('invconf'))

        # Make sure API name is friendly
        if urllib.parse.urlparse(config['api']).scheme != '':
            return self.crash("FOUND HTTP OR HTTPS IN API")

        self._params['config'] = config

        self.config['lastupdate'] = 0

        # self._logger = Logger(self._filesystem,'error.log')
        self._logger = Logger.Logger(self._filesystem,
                                     filename=self.config['logfile'],
                                     loglevel=self.config['loglevel'])

        # Run parent starting code
        super().start()

        sqlfp = os.path.join(self.config['sqlstore'], self._kernel.get_serial()) + ".db3"
        self.sql.fp(sqlfp)

        # Initialize inventory software
        self.initialize()

    def initialize(self):
        """
        Initialize the software
        :return:
        """
        if self._initialized:
            return

        self.log("Initializing")

        # Create the DB if it doesn't exist, otherwise update configuration
        if self.create_sqldb():
            self.update_config()

        # Retrieve the configuration
        self.get_config()

        # Begin initial inventory
        self.init_inventory()

        self._initialized = True

        self.post_inventory()
        return True

    def tick(self, tmr, dtime):
        """
        The software simulation loop, what happens per tick
        :return:
        """
        if not self.started():
            return
        config = self._params['config']

        # If not initialized, quit from ticking
        if not self._initialized:
            return

        # Time to send heartbeat?
        if self.ram.get('last_hb', 0) + config['hbt'] < tmr:
            self.ram.get('last_hb', None)
            self.heartbeat(tmr)

        # print((tmr, dtime))
        # print(self._params['config']['api'])

        return True

    # SQL ACTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def create_sqldb(self):
        """
        Create the system sqlite3 base database
        :return:
        """

        if self.sql.exists():
            return False

        self.log("Creating SQL DB")
        self.sql.create_module_table()

        return True

    def dump_config_to_table(self, tmr=time.time()):
        """
        Dump configuration to local db
        :param tmr: time of operation
        :return:
        """
        self.log("Dumping config to DB")
        self.sql.dump_config_to_db(tmr, self.config)

    def update_config(self, tmr=time.time(), config=None):
        """
        Update the configuration from remote API
        :param tmr: time of update
        :return:
        """

        # Get the remote configuration if none passed in
        if not config:
            # Get the remote configurations
            config = self.inv_rconf()

        self.log("Updating configuration")

        # Overwrite current configuration for remote
        for i in config:
            self.config[i['attribute']] = i['value']

        self.config['lastupdate'] = tmr

        # Dump to db
        self.sql.dump_config_to_db(tmr, self.config)

        # Clean up types
        conf = self.sql.typeify_config(self.config)
        for i in conf:
            self.config[i] = conf[i]

    # API ACTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_config(self):
        """
        Master function for getting the configuration either via remote API or local SQLite table
        :return:
        """
        self.log("Getting configuration")

        # If the table doesn't exists
        if self.sql.exists():
            self.log("Loading configuration")
            conf = self.sql.config()
            for i in conf:
                self.config[i] = conf[i]

            return self.config

    def heartbeat(self, tmr):
        """
        InvSys heartbeat prepper
        :param tmr:
        :return:
        """
        # Put to RAM when our next heartbeat should be
        data = self.inv_heartbeat()

        self.log('Heartbeat as '+self.config.get('client_id', 'N/A'))

        # Update local configuration with config from heartbeat
        self.update_config(config=data['config'])

        self.ram['last_hb'] = tmr

    def init_inventory(self):
        """
        Get an initial capture of the underlying system and save it to the sql database and
            sent the full inventory to the inventory server to get client_id and apikey for
            future interactions
        :return:
        """
        self.log("Gathering Initial Inventory")
        kernel = self._kernel

        self.sql.open()

        # Template queries
        create_module = 'INSERT INTO modules (`module`) VALUES (?)'

        create_table = ('CREATE TABLE ',
                        ' (property VARCHAR(100), '
                        'cid TEXT,'
                        'sid TEXT,'
                        'value TEXT,'
                        'updated_at datetime,'
                        'sync_date datetime,'
                        'sync_key VARCHAR(100),'
                        'PRIMARY KEY (property, cid))')

        insert_property = ('INSERT INTO ',
                           ' (`property`, `cid`, `value`, `updated_at`, `sync_date`, `sync_key`) '
                           'VALUES (?, ?, ?, ?, NULL, NULL)')

        # Dynamically create module tables and insertions of data
        modules = list(kernel.modules)
        for i in modules:
            if len(self.sql.execute('SELECT * FROM modules WHERE `module` = ?', [i]).fetchall()) == 0:
                self.log("Creating inventory for " + i + " module")
                self.sql.execute(create_module, [i])

                # CREATE TABLE <module> (property ....
                self.sql.execute(i.join(create_table))

            for k in kernel.get_component(i):
                # Get flattened list of components
                flat_component = flatten(k.component)

                for j in flat_component:
                    rep = self.sql.execute('SELECT value FROM '+i+' WHERE cid = "'+k['cid']+'" and property = "'+j+'"')

                    if len(rep.fetchall()) <= 0 and j != 'cid':
                        opts = [j, k['cid'], flat_component[j], time.time()]
                        self.sql.execute(i.join(insert_property), opts)

                self.sql.commit()

        self.sql.close()

        self.log("Building inventory object")

        # Build inventory object for API
        inventory = {}
        for i in kernel.modules:
            if not inventory.get(i, None):
                inventory[i] = []

            for j in kernel.get_component(i):
                inventory[i].append(j.component)

        idents = self.inv_init(inventory)

        if not idents:
            return None

        self.log("Applying indentifiers")
        for i in idents:
            self.config[i] = idents[i]

        self.sql.dump_config_to_db(time.time(), self.config)

    def post_inventory(self):
        resp = self.inv_post()

        modules = resp['computer']['modules']

        for i in modules:
            opts = (i, modules[i])
            for x in opts[1]:
                self.sql.cidsid(i, x['cid'], x['sid'])
                self.sql.syncmodule(i, x['sid'], time.time())

    # Inventory API Interactions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def inv_idents(self, data=None):
        """
        Generate identifiers for given data object
        :param data: data object
        :return:
        """
        if not data:
            data = {}

        # If we have a client_id we have some authentication
        if self.config.get('client_id', None):
            data['client_id'] = self.config.get('client_id', None)
            data['apikey'] = self.config.get('apikey', None)
            data['serial'] = self._kernel.get_serial()

        return data

    def inv_rconf(self):
        """
        Interface between InvSys and RequestApi for requesting configuration
        :return:
        """
        self.log("Getting remote configuration")

        data = self.inv_idents()

        # Get configuration
        rconf, code = self.request.rconf(self.config, data)

        # If code is not OK(200)
        if code == 404:
            return self.crash("Could not connect to API")
        elif code != 200:
            return self.crash(rconf)

        return rconf['data']['config']

    def inv_init(self, inventory):
        """
        Interface between InvSys and RequestApi for initial inventory
        :param inventory: entire system in inventory friendly structure
        :return:
        """
        self.log("Sending Initial Inventory Data")

        data = {
            'computer': {
                'modules': inventory
            }
        }

        data = self.inv_idents(data)

        resp, code = self.request.init(self.config, data)

        # Handle the error codes
        if code == 500:
            return self.crash(resp)
        elif code != 200:
            for i in resp.get('errors', []):
                # UnauthorizedAPI: We need to reinit in this case
                if i['code'] == '0x0003':
                    self.config.pop('client_id', None)
                    self.config.pop('apikey', None)
                    return self.inv_init(inventory)
                # ExistsInventory: Already exists in inventory, returns client_id
                elif i['code'] == '0x000B':
                    self.log(i['type'] + "|" + i['message'], 3)
                    return resp['data']['identifiers']

            # Other codes result in crash
            return self.crash(resp)

        self.log("SUCCESS!")
        return resp['data']['identifiers']

    def inv_post(self):
        """
        TODO: Interface between InvSys and RequestApi for post inventory
        :return:
        """
        # Bind identifiers
        self.log("Finding post inventory")
        data = {}
        data = self.inv_idents(data)

        resp, code = self.request.post(self.config, data)

        return resp['data']

    def inv_update(self, changes):
        """
        TODO: Interface between InvSys and RequestApi for update inventory
        :param changes: What changes are to be made
        :return:
        """
        print(changes)
        return self.request.update(self.config)

    def inv_heartbeat(self, data=None):
        """
        Interface between InvSys and RequestApi for heartbeat
        :param data: dataobject
        :return:
        """
        if not data:
            data = {}

        # Bind identifiers
        data = self.inv_idents(data)

        # Handle heartbeat request
        resp, code = self.request.heartbeat(self.config, data)

        # Handle error cases
        if code != 200:
            return self.crash(resp)

        # Return data
        return resp['data']
