FROM python:3.8.6

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip --no-cache-dir && \
    pip install -r requirements.txt --no-cache-dir

EXPOSE 80

CMD ["streamlit", "run", "Homepage.py", "--server.port", "80"]
