FROM python:alpine3.8
COPY ekscost ./ekscost
WORKDIR /ekscost
RUN pip install -r requirements.txt
CMD [ "python","main.py" ]


