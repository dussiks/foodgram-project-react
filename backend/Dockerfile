FROM python:3.8.5
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
CMD python3 /code/manage.py runserver 0:8000