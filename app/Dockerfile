FROM python:3.6-onbuild
COPY onlinestat.yml /etc/onlinestat.yml
CMD  cd /usr/src && APP_SETTING=.env python -m app.onlinestat
