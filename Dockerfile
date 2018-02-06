FROM python:2

ADD notify.py /

RUN pip install praw
RUN pip install requests

CMD [ "python", "./notify.py" ]
