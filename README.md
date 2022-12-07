# seekers
An artificial intelligence programming challenge targeted at students.

AIs compete by controlling bouncy little circles ("seekers") trying to collect the most goals.

Based on Python 3 and pygame.

This repository contains a Python implementation of the Seekers gRPC server as well as a gRPC Seekers client library. 

## How to run
Install python3 and the packages in [`requirements.txt`](requirements.txt).

### Run a Python Server
This will run the gRPC server and start the specified AIs. These will not be connected to the sever via gRPC but their 
`decide()` method will be called directly from the server. This is unsafe but faster.
```bash
$ python3 run_seekers.py <AI files>
```

### Run a Python Client
You will need a separate server running. For example [the Java implementation](https://github.com/seekers-dev/seekers-api).

```bash
$ python3 run_clients.py <AI files>
```

## License
You can, and are invited to, use, redistribute and modify seekers under the terms
of the GNU General Public License (GPL), version 3 or (at your option) any
later version published by the Free Software Foundation.
