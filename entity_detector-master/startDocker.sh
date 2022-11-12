DOCKER_NAME=argon-ner
DOCKER_PATH=argon-ner


docker run --name $DOCKER_NAME \
        -d \
        --restart always \
        -e TZ=Europe/Madrid \
        -p 6001:4999 \
    $(echo $DOCKER_PATH)


