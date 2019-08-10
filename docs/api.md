# API Documentation
## v1 API

### Computer Structure
**NOTE**: You do *not* use this as the top level object for request/responses.

```
"computer": {
    "_id": "<mongoDB id>",
    "serial": "<serial #>",
    "manufacturer": "...",
    "model": "<model>",
    "hostname": "<hostname>",
    "modules": {
        "<module_broad_name>": [
            {
                "...":"..."
            }
        ]
    }
}
```
### Computer Module Structures
#### Supported Modules
- sound
- graphic
- partition
- storage
- cpu
- memory
- network
- uplink (network)
- controller
- port
- monitor
- bios
- software

#### Module Example
```
"storage" : [
    { 
        "cid": "<client-generated id>",
        "sid": "<server-generated id>",
        "letter": "C",
        "...": "..."
    },
    { 
        "cid": "<client-generated id>",
        "sid": "<server-generated id>",
        "letter": "H",
        "...": "..."
    }
]
```
#### Sound
```
"sound" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "manufacturer": (string),
    "description": (string)
}
```

#### Graphics
```
"graphic" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "chipset": (string),
    "memory": (string),
    "resolution": (string)
}
```

#### Partitions
```
"partition" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "letter": (string),
    "type": (string),
    "filesystem": (string),
    "free_data": (string),
    "total_data": (string)
}
```

#### Storage
```
"storage" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "manufacturer": (string),
    "model": (string),
    "desc": (string),
    "type": (string),
    "size": (string),
    "serial": (string),
    "firmware": (string)
}
```

#### CPU
```
"cpu" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "speed": (string),
    "cores": (number)
}
```

#### Memory
```
"memory" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "caption": (string),
    "desc": (string),
    "capacity": (string),
    "purpose": (string),
    "type": (string),
    "speed": (string),
    "slot": (string),
    "serial": (string)
}
```

#### Network
```
"network" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "desc": (string),
    "type": (string),
    "speed": (string),
    "mac": (string),
    "status": (boolean),
    "uplink": [
        { (uplink) }
    ]
}
```

##### Uplink (network ip)
```
"uplink": {
    "timestamp": "<unix timestamp>",
    "ipv4": (string),
    "ipv6": (string),
    "network": (string),
    "gateway": (string),
    "netmask": (string),
    "dhcp-ip": (string)
}
```


#### Controllers
```
"controller" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "manufacturer": (string),
    "type": (string)
}
```

#### Ports
```
"port" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "type": (string),
    "interface": (string),
    "desc": (string)
}
```

#### Monitors
```
"monitor" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "caption": (string),
    "manufacturer": (string),
    "type": (string),
    "serial": (string)
}
```

#### Bios
```
"bios" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "serial": (string),
    "manufacturer": (string),
    "model": (string),
    "type": (string),
    "asset_tag": (string),
    "bios_manufacturer": (string),
    "bios_version": (string),
    "bios_date": (string)
}
```

#### Software
```
"software" : {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "version": (string),
    "editor": (string),
    "comments": (string)
}
```

#### Printers
```
"printer": {
    "cid": "<client-generated id>",
    "sid": "<server-generated id>",
    "name": (string),
    "driver": (string),
    "port": (string),
    "desc": (string),
    "serial": (string) 
}
```
---
## v0 API

### Computer Structure
```
computer {
    "serial": "<serial>",
    "model": "<computer model>",
    "manufacturer": "<dell,HP,etc>",
    "name": "<hostname/something>",
    "assigned_data" : {
        "property_tag": "<UMBC TAG>",
        "description": "<super descriptive data>",
    },
    "modules": {
        "network": {
            "hostname": "<hostname>",
            "domain": "<ad.umbc.edu/etc>",
            "ip": "<ip address>",
            "mac": "<mac address>",
            "timestamp": "<unix timestamp>"
        }
    }
}
```

### Server Request API (Sent from client -> Server)
```
request {
    "task": "<relevant task>",
    "timestamp": "<timestamp",
    "data": {
        <context specific data>,
        "keypub": "<keypub>", (this is given by the server on initial inventory)
        "computer_id": "<id>", (this is given by the server on initial inventory)
        "computer" : {
            <send top level data, (serial, name, manufacturer, NOT modules, etc)>
        }
    }
}
```

### Server Response API (Server -> Client)
```
response {
    status: "<HTTP status code>",
    errors: [ <any errors, if any> ],
    data: {
        <context specific data>,
        config: {
            <client configuration data>
        },
        identifiers: {
            "keypub": "<key>",
            "computer_id": "<id>"
        }
    }
}
```

## Response codes
- 200 - OK
- 201 - Accepted (Upon first inventory check you'll get this)
- 400 - Bad Request (Incorrect format, check errors)
- 401 - Unauthorized (No keypub, or wrong key match)
- 403 - Forbidden
- 404 - Not Found
- 405 - Method not allowed (GET/POST)
- 406 - Not Acceptable (Cannot fulfill the request)
- 500 - Internal Server Error
- 503 - Service unavailable