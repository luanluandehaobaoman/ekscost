FROM python:alpine3.8
COPY ekscost ./ekscost
WORKDIR /ekscost
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]

