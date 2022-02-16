FROM python:3.9-slim
WORKDIR diffhest

# copy requirements in separate command, to make use of docker caches
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY setup.py ./
RUN pip install -e .

ENTRYPOINT python3 -m diffhest --log_notime
