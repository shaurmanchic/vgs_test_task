FROM python:3.7.3-slim-stretch

RUN apt-get update &&\
    apt-get install -y procps vim curl gnupg build-essential libssl-dev libxml2-dev libxmlsec1-dev libxmlsec1-openssl &&\
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN mkdir /usr/src/vgs_test_task

COPY requirements.txt /usr/src/vgs_test_task/requirements.txt

WORKDIR /usr/src/vgs_test_task

RUN pip install -r requirements.txt --no-cache-dir

# Update PYTHONPATH
ENV PYTHONPATH $PYTHONPATH:/usr/src/vgs_test_task

COPY ./ /usr/src/vgs_test_task

EXPOSE 5000/tcp
CMD ["uwsgi", "--ini", "uwsgi.ini"]