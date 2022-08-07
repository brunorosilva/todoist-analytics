# Todoist Analytics

The main goal for this tool is to help you visualize, analyze and get insights about your todoist tasks data. 

You can interact with the demo here: 
* https://todoist-analytics.azurewebsites.net/

You can also find a docker image here:
* https://hub.docker.com/repository/docker/marianoog/todoist_analytics

![Analytics logo](img/analytics_logo_300x300.png)

I always wanted to have something like this in todoist or with an integration, I was thinking on doing something my own,
but I didn't want to deal with some parts of the app like session states and data retrieval. 
After some time of searching I found [this project](https://github.com/brunorosilva/todoist-analytics) from Bruno 
Chicelli. I was happy to see somebody already solved most of the problems I was avoiding. And thanks to that I was able 
to start from there and not from zero. 

Now the dashboards have more functionality. I guess this app could be used for other people and as a starting point for
other projects that want to create something similar. Feel free to fork and improve it or send an issue if you have any
suggestions.

## How to run this tool locally

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
- [X] Kanban-like metrics (throughput, velocity, etc)
- [ ] Focus view (recommendations of tasks to focus on, with balance of effort)
