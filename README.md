# Todoist Analytics

The main goal for this tool is to help you visualize, analyze and get insights about your todoist tasks. 

![Analytics logo](img/analytics_logo_300x300.png)

I always wanted to have something like this in todoist or with an integration, but I couldn't find any good solutions. 
After a while I found [this project](https://github.com/brunorosilva/todoist-analytics) from Bruno Chicelli,
that finally satisfied my curiosity. However, I wanted more features, and I wanted to make it my own.
So I decided to build starting from his ideas and code to include some additional things I always wanted to have.

## How to use this tool

- [ ] PENDING: deploy to azure web app

## How to run this tool locally

### Docker

Run the following commands to start the docker container:

```
docker build -t todoist_analytics .
docker run toodoist_analytics -p 80:80
``` 

### Virtual Environment

1. Create an app in your todoist account: https://developer.todoist.com/appconsole.html

2. Clone the repository
```
git clone https://github.com/MarianoOG/Todoist-Analytics.git
```

3. Create the credentials.py file inside the src folder with your app client_id and client_secret.
```
# Use this format change the values to your own
client_id = {client_id}
client_secret = {client_secret}
```

4. Create a virtual environment
```
python -m venv venv
```


4. Install dependencies
```
pip install -r requirements.txt
```

5. Run the streamlit app
```
streamlit run Homepage.py
```

## Ideas of new features

- [x] New habit reports (Weekly, Monthly and Yearly)
- [ ] Kanban-like metrics (throughput, velocity, etc)
- [ ] Balance of effort in projects (plan vs actual)
- [ ] Focus view (recommendations of tasks to focus on)
