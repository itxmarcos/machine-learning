FROM python:3.7.3-slim-stretch

RUN apt-get update && apt-get upgrade -y
RUN mkdir -p /usr/share/man/man1
RUN apt-get install default-jre wget  -y
RUN apt-get clean



RUN rm /tmp/* -Rf 

ENV PYTHON_HOME "/envs/py36/bin"
ENV SERVICE_PATH "/work"
ENV ENTRY_POINT "run.py"
USER root


ENV SHELL=/bin/sh \
    NB_USER=jovyan \
    NB_GNAME=mstudio \
    NB_GID=180730

       
RUN echo "$NB_GNAME:x:$NB_GID:" >> /etc/group
RUN adduser $NB_USER
RUN adduser $NB_USER $NB_GNAME 
RUN usermod -g $NB_GID $NB_USER

RUN mkdir /entity_detector-master

ADD . /entity_detector-master
RUN ls -la /entity_detector-master/

#ADD ./installNer.sh /
RUN chmod 777 /entity_detector-master/installNer.sh

SHELL ["/bin/bash", "-c"]
RUN /entity_detector-master/installNer.sh

RUN pip3 install -r /entity_detector-master/requirements.txt
#ADD ./startService.sh /
RUN chmod 777 /entity_detector-master/startService.sh

#RUN mkdir -p /entity_detector-master/results/ner/
#RUN chmod 0666 /entity_detector-master/results/ner/ -R
RUN touch /entity_detector-master/results/ner/log.txt
#RUN chown jovyan:mstudio /entity_detector-master/results/ner/log.txt

#USER $NB_USER

ENTRYPOINT ["/entity_detector-master/startService.sh"]


