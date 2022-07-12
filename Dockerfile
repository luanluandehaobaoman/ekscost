FROM python:alpine3.8
MAINTAINER "347036700@qq.com"
COPY ./source/* /app/
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]

