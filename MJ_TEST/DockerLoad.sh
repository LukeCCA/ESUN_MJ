#!/bin/bash
docker load --input tag_api.tar
docker load --input recommand_api.tar
docker-compose up 