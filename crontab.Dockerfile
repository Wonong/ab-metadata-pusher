FROM python:3.7-slim
WORKDIR /app

RUN apt update
RUN apt -y install libpq-dev python3.7-dev gcc cron

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app
RUN python setup.py install

# cron
ADD crontab /etc/cron.d/cron
RUN chmod 644 /etc/cron.d/cron

# RUN chmod +x /app/shell/bootstrap.sh
# ENTRYPOINT ["/app/shell/bootstrap.sh"]
RUN chmod +x /app/bootstrap.py
RUN python /app/bootstrap.py
ENTRYPOINT [ "cron -f" ]
