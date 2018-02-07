FROM python

RUN pip install praw
RUN pip install requests

COPY notify.py .

CMD python -u notify.py
