FROM python:2
MAINTAINER Chien-An Chen <lukchen419@gmail.com>
COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt
EXPOSE 6010
CMD bash start.sh
# docker build -t tag_api:1.0 .
# docker run -itd --name redis redis:latest
# docker run -itd --name postgres -e POSTGRES_PASSWORD=lukechen0419 -d postgres
# docker run -itd --name postgres -e POSTGRES_PASSWORD=lukechen0419 postgres:latest
# docker run -itd --name chen_test -p 6010:6010 --link redis:redis --link postgres:postgres tag_api:1.0
