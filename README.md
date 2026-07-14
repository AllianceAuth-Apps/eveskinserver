# EVE SKIN server

An image server designed to serve SKIN icons for various EVE Online types.

[![release](https://img.shields.io/badge/release-1.0.0-orange)](https://pypi.org/project/eveskinserver/)
[![Python](https://img.shields.io/badge/python-3.7-blue)](https://pypi.org/project/eveskinserver/)
[![CI/CD](https://github.com/AllianceAuth-Apps/eveskinserver/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/AllianceAuth-Apps/eveskinserver/actions/workflows/ci-cd.yaml)
[![license](https://img.shields.io/badge/license-MIT-green)](https://github.com/AllianceAuth-Apps/eveskinserver#MIT-1-ov-file)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

This is an image server designed to serve SKIN icons for various EVE Online types. The server aims to fill the gap of the official [CCP image server](https://imageserver.eveonline.com/), which does not provide images for SKIN icons. The API has been designed to match the API of CCP's image server.

## Self-hosting

This section describes briefly how to setup eveskinserver on your own host.

>[!Note]
> eveskinserver is a normal Flask app and can be deployed in many different ways. This guide describes how to deploy it with with Gunicorn + Webserver (e.g. NGINX) on Ubuntu.

Create a service user and switch to that user:

```bash
adduser --disabled-login eveskinserver
su eveskinserver
```

Setup a virtual environment for the server, activate it and update key packages:

```bash
cd /home/eveskinserver
python3 -m venv venv
source venv/bin/activate
```

Update and install needed packages:

```bash
pip install -U pip
pip install wheel
pip install gunicorn
```

Install eveskinserver from the repo into the venv:

```bash
pip install git+https://github.com/AllianceAuth-Apps/eveskinserver.git
```

Copy the following files from `gunicorn` into your home folder:

- `wsgi.py`
- `supervisor.conf`

Run gunicorn manually to check that your setup is working:

```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Add eveskinserver to your supervisor configuration and restart supervisor to activate the change:

```bash
ln -s /home/eveskinserver/supervisor.conf /etc/supervisor/conf.d
systemctl restart supervisor
```

Add a new configuration to your webserver that routes HTTP/HTTPS requests to gunicorn on port 8000 as proxy.

## Donation

But if you'd like to say thanks, a ISK donation is always very welcome: **Erik Kalkoken**

## Legal

All game related data ("game data", e.g. in folder ccp_data) is owned by CCP hf and used in accordance with the developer licence agreement.
