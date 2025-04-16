FROM ubuntu:latest
LABEL authors="illia"

ENTRYPOINT ["top", "-b"]