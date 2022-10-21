FROM python:3.8.6

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip --no-cache-dir && \
    pip install -r requirements.txt --no-cache-dir

COPY img/ /app/img
COPY *_Homepage.py "/app/🏠_Homepage.py"
COPY src/ /app/src
COPY pages/01_*_Habits_and_Goals.py "/app/pages/01_🎯_Habits_and_Goals.py"
COPY pages/02_*_Productivity.py "/app/pages/02_📈_Productivity.py"
COPY pages/03_*_Planning.py "/app/pages/03_📝_Planning.py"

EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "🏠_Homepage.py", "--server.port", "8080"]
