FROM python:3.12-slim
RUN pip install flask psycopg[binary] gunicorn flask-cors
WORKDIR /app
COPY app.py /app/app.py
CMD ["gunicorn","-w","2","-b","0.0.0.0:5000","app:app"]
