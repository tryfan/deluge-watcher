FROM python:3
COPY requirements.txt /
RUN pip install -r /requirements.txt
WORKDIR /code
ADD watcher.py /code/
ADD config.yml /code/
CMD [ "python", "watcher.py" ]
