FROM amazonlinux
MAINTAINER aftabalam01

USER root
RUN mkdir /var/task

ENV APP_DIR /var/task
#ENV PATH=${PATH}:/var/task/bin
ENV PYTHONPATH=/var/task/src

WORKDIR $APP_DIR

RUN yum install -y wget unzip libX11.so.6

RUN wget https://chromedriver.storage.googleapis.com/73.0.3683.20/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
#RUN chromedriver --version
# install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
RUN yum install -y google-chrome-stable_current_x86_64.rpm
#RUN yum list | grep python3
RUN yum install -y python37

#RUN google-chrome --version


COPY requirements.txt .
COPY src $APP_DIR/src
COPY urls $APP_DIR/urls
COPY config $APP_DIR/config

#RUN update-ca-certificates
RUN pip3 install -r requirements.txt

# make sure to pass correct ENV
# USER_NUM any number less total url count - urls per session
# NUM_URLs url per session
# LOGIN_ID - login id for confluence
# LOGIN_PASSWD  - password for confluence

ENTRYPOINT [ "python3","./src/test_script.py" ]