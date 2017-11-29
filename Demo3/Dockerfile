FROM python:2
MAINTAINER Chien-An Chen <lukchen419@gmail.com>
COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt
CMD sleep 10 && bash start.sh
# docker build -t tag_api:1.0 .
# docker build -t recommand_api:1.0 ./RecommandSystem
# docker run -itd --name redis redis:latest
# docker run -itd --name postgres -e POSTGRES_PASSWORD=lukechen0419 -d postgres
# docker run -itd --name postgres -e POSTGRES_PASSWORD=lukechen0419 postgres:latest
# docker run -it --name tagserver --link redis:redis --link postgres:postgres tag_api:1.0
# docker run -it --name recommand -p 6010:80 --link tagserver:tagserver recommand_api:1.0
