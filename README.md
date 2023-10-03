# manual

## prerequisites
* docker
* python 3.9 +
* uvicorn (with python or standalone)

### install uvicorn with python

```shell
pip3 install uvicorn
```

### install deps

```shell
pip3 install -r requirements.txt
```

### run mongo and server

Run mongo and mongo web-interface with command
```shell
docker-compose up -d
```

And run server in hot-reload mode

```shell
export PYTHONPATH=$(pwd)/src
python3 -m uvicorn main:app --reload
```