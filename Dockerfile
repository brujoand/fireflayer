FROM python:3.10

COPY fireflayer /opt/fireflayer/fireflayer
COPY fireflayer.app /opt/fireflayer/fireflayer.app
COPY requirements.txt /opt/fireflayer/requirements.txt

WORKDIR /opt/fireflayer

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/opt/fireflayer/fireflayer.app"]

