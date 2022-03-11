FROM python:3.7.4
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install dist/todoist-analytics-0.0.0.tar.gz


CMD ["sh", "-c", "streamlit run --server.port $PORT streamlit_app.py"]
# ENTRYPOINT ["streamlit", "run", "", "--server.port $PORT"]
