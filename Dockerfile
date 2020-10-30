FROM neo4j:4.1.0-enterprise

RUN apt-get update
RUN apt install -y wget
RUN wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/4.1.0.0/apoc-4.1.0.0-all.jar
RUN mv apoc-4.1.0.0-all.jar plugins/

RUN wget https://github.com/neo4j/graph-data-science/releases/download/1.3.0/neo4j-graph-data-science-1.3.0-standalone.jar
RUN mv neo4j-graph-data-science-1.3.0-standalone.jar plugins/

#run as neo4j user to avoid permission issues with mounted volumes in later version of neo4j
#https://github.com/neo4j/docker-neo4j/issues/223
USER neo4j