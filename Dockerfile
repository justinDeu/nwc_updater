FROM python:3.7

WORKDIR /relay

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD /bin/bash