FROM python:3.9-slim

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./diffhest.py ./

ENTRYPOINT python3 diffhest.py --log_notime
