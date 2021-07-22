PYEXE	= python3

########
DKRREPO	= mhastro
DOCKER_NAME	= fdi
DVERS	= v1.3
DFILE	=dockerfile

SERVER_NAME      =httppool
SVERS	= v5
SFILE	= fdi/pns/resources/httppool_server.docker

PORT        =9884
SECFILE = $${HOME}/.secret
EXTPORT =$(PORT)
IP_ADDR     =10.0.10.114
PROJ_DIR	= /var/www/httppool_server
SERVER_POOLPATH	= $(PROJ_DIR)/data

LATEST	=im:latest
B       =/bin/bash

build_docker:
	DOCKER_BUILDKIT=1 docker build -t $(DOCKER_NAME):$(DVERS) \
	--secret id=envs,src=$(SECFILE) \
	--build-arg fd=$(fd) \
	--build-arg  re=$(re) \
	-f $(DFILE) \
	$(D) --progress=plain .
	docker tag $(DOCKER_NAME):$(DVERS) $(LATEST)

launch_docker:
	docker run -dit --network=bridge --env-file $(SECFILE) --name $(DOCKER_NAME) $(D) $(LATEST) $(LAU)

build_server:
	DOCKER_BUILDKIT=1 docker build -t $(SERVER_NAME):$(SVERS) \
	--secret id=envs,src=$(SECFILE) \
	--build-arg PROJ_DIR=$(PROJ_DIR) \
	--build-arg fd=$(fd) \
	--build-arg  re=$(re) \
	-f $(SFILE) \
	$(D) --progress=plain .
	docker tag $(SERVER_NAME):$(SVERS) $(LATEST)

launch_server:
	docker run -dit --network=bridge \
	--mount source=httppool,target=$(SERVER_POOLPATH) \
	--mount source=log,target=/var/log \
	--env-file $(SECFILE) \
	-p $(PORT):$(EXTPORT) \
	--name $(SERVER_NAME) $(D) $(LATEST) $(LAU)
	sleep 2
	#docker inspect $(SERVER_NAME)
	docker ps -n 1

rm_docker:
	cid=`docker ps -a|grep $(LATEST) | awk '{print $$1}'` &&\
	echo Gracefully shutdown server ... 10sec ;\
	if docker stop $$cid; then docker  rm $$cid; else echo NOT running ; fi

rm_dockeri:
	cid=`docker ps -a|grep $(LATEST) | awk '{print $$1}'` &&\
	echo Gracefully shutdown server ... 10sec ;\
	if docker stop $$cid; then docker  rm $$cid; else echo NOT running ; fi
	docker image rm $(LATEST)

it:
	cid=`docker ps -a|grep $(LATEST) | head -n 1 |awk '{print $$1}'` &&\
	if [ -z $$cid ]; then echo NOT running ; else \
	docker exec -it $(D) $$cid $(B); fi

t:
	cid=`docker ps -a|grep $(LATEST) | head -n 1 | awk '{print $$1}'` &&\
	if [ -z $$cid ]; then echo NOT running ; else \
	docker exec -it $(D) $$cid /usr/bin/tail -n 100 -f /home/apache/error-ps.log; fi

i:
	cid=`docker ps -a|grep $(LATEST) | head -n 1 | awk '{print $$1}'` &&\
	if [ -z $$cid ]; then echo NOT running ; else \
	docker exec -it $(D) $$cid /usr/bin/less -f /home/apache/error-ps.log; fi

push_docker:
	im=$(DKRREPO)/$(DOCKER_NAME):$(DVERS); \
	docker tag  $(DOCKER_NAME):$(DVERS) $$im &&\
	docker push $$im

push_server:
	im=$(DKRREPO)/$(SERVER_NAME):$(SVERS); \
	docker tag  $(SERVER_NAME):$(SVERS) $$im &&\
	docker push $$im

vol:
	docker volume create httppool
	docker volume create log
	docker volume inspect httppool log

backup_server:
	f=backup_$(SERVER_NAME)_$(SVERS)_`date +'%y%m%dT%H%M%S' --utc`.tar &&\
	echo Backup file: $$f ;\
	docker run -it --rm \
	--mount source=httppool,target=$(SERVER_POOLPATH) \
	--mount source=log,target=/var/log \
	--env-file $(SECFILE) \
	-p 9883:9883 \
	-a stdin -a stdout \
	--entrypoint "" \
	--name $(SERVER_NAME)_backup $(D) $(SERVER_NAME):$(SVERS)  \
	/bin/bash -c 'cd $(PROJ_DIR)/data && tar cf /dev/stdout .' >  $$f

restore_server:
ifndef from
	echo Must give filename: make restare_server from=filename
else
	echo Restore from backup file: $(from)
	cat $(from) | docker run -i --rm \
	--mount source=httppool,target=$(SERVER_POOLPATH) \
	--mount source=log,target=/var/log \
	--env-file $(SECFILE) \
	-p 9883:9883 \
	-a stdin -a stdout \
	--entrypoint "" \
	--name $(SERVER_NAME)_backup $(D) $(SERVER_NAME):$(SVERS)  \
	/bin/bash -c 'cd $(PROJ_DIR)/data && tar xvf - .'
endif

restore_test:
	make rm_docker
	docker volume prune --force && 	docker volume ls
	@echo %%% above should be empty %%%%%%%
	make launch_server && make it B='/bin/ls -l $(PROJ_DIR)/data'
	@echo %%% above should be empty %%%%%%%
	make restore_server from=backup_httppool_v5_210722T015659.tar
	make it B='/bin/ls -l $(PROJ_DIR)/data'
	@echo %%% above should NOT be empty %%%%%%%

