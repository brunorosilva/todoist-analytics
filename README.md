# Todoist Analytics

![version](https://img.shields.io/badge/version-0.0.0-brightgreen)

<b>
If you use Todoist for daily, weekly, monthly or yearly planning you should try this tool.
</b>

This is how the current version of the tool looks like.

<img src='assets/images/dashboard_sample.png'>


The main goal for this tool is to help you keep track and create analytics based on your data from todoist.


--- MVP ---
- [x] Part 1: Getting the data
  
  Create an application that calls the Todoist API and gets all done and tbd tasks from an user
- [ ] Part 2: Weekly review tab
  
  From the gattered data create a dashboard with info from the user's last week plus some insights
- [ ] Part 3: Monthly review tab
  
  Personalized insights and monthly reviews (:

--- Post-MVP ---
- [ ] Part 4: Drop Streamlit
Develop a Flask backend and a React frontend for better usage

# Usage

## Get your API Key
Go to your Todoist settings into the integrations tab, at the bottom you'll find your API key, copy it.

## Create your credentials.py file

`$ make credentials`

and if your credential file doesn't exist, you will be prompted to input your token.

## Run the app

`$ make app`
