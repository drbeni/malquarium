# Malquarium - A modern malware repository

Malquarium is a web based malware repository tool built on modern web technologies with the follwoing goals in mind:  

- Easy to install and maintain
- Fast searches over hashes and indicators
- VirusTotal like UI
- Isolated execution of binary analysis for security reasons

See it in action at https://malquarium.org
 
## Installation

### Requirements

A Linux system. Tested on Ubuntu 16.04 and Ubuntu 18.04, but should work everywhere.

Malquarium requires Docker to run it's binary analyzer modules. If you decide to run the backend and frontend outside of Docker containers, the user which runs the backend needs to be in the docker group because the backend needs to launch containers on demand.

The Backend Database must be PostgreSQL 9+ which can run in a container or outside of Docker.


### Installation using Docker

Use this setup to run everything in Docker containers, the fastest way to get it up and running. There are 2 docker-compose files, one which includes the database, the other not.  

Change at least the following parameters to get your Malquarium up and running

#### Service malquarium-backend

| Parameter | Value | Description |  
| --- |  --- |  --- |  
| volumes | ```/data/malquarium/samples:/data/samples``` | Persistend volume of the sample binaries. Change the path if your samples are not at ```/data/malquarium/samles``` |
| volumes | ```/usr/bin/docker:/bin/docker``` | Pass the docker binary to the backend. Change to the output of ```which docker``` if it's not ```/usr/bin/docker``` |
| DJANGO_SECRET_KEY | Your random Django secret key | You can generate one with ```head /dev/urandom | tr -dc A-Za-z0-9 | head -c 80 ; echo ''``` |   
| OUTER_SAMPLE_STORE | ```/data/malquarium/samples``` | The path where your samples are on the host, not inside the container. Needed for the binary analysis containers. Must be the same as the left part of the corresponding volumes setting |   


#### Service malquarium-backend
| Parameter | Value | Description |  
| --- |  --- |  --- |  
| volumes | ```/data/malquarium/db:/var/lib/postgresql/data``` | Persistend volume of the database. Change the path if your database files are not at ```/data/malquarium/db``` |


**Start the containers**  

	docker-compose up

The web frontend will be available on http://localhost:8080

## Configuration
You can use the Django admin GUI to change all settings: http://localhost:8080/admin/

