FROM galaxy-build

RUN yum -y install vim tmux
RUN pip install honcho supervisor
WORKDIR /galaxy
CMD /galaxy/scripts/docker-develop/start_develop.sh 

