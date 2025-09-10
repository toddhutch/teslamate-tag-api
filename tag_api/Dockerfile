FROM python:3.12-slim
RUN pip install flask psycopg[binary]
ENV DB_HOST=database DB_USER=teslamate DB_NAME=teslamate DB_PASS=changeme TOKEN=changeme
COPY app.py /app/app.py
WORKDIR /app
CMD ["python", "/app/app.py"]
