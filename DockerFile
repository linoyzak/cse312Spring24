FROM python:3.9.13

ENV HOME /root
WORKDIR /root

COPY . .
RUN pip3 install -r requirement.txt

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u server.py