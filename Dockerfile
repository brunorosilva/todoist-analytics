FROM python:3.7.4
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install dist/todoist-analytics-0.0.0.tar.gz

EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]