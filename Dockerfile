FROM python

RUN pip install praw
RUN pip install requests
RUN pip install imapclient

COPY notify.py .

CMD python -u notify.py
