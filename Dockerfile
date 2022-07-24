FROM python:3.8.6

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 80

CMD ["streamlit", "run", "main.py", "--server.port", "80"]
