FROM python:3.10

COPY fireflayer /opt/fireflayer/fireflayer
COPY fireflayer.app /opt/fireflayer/fireflayer.app
COPY requirements.txt /opt/fireflayer/requirements.txt

WORKDIR /opt/fireflayer

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/opt/fireflayer/fireflayer.app"]
CMD ["--help"]

