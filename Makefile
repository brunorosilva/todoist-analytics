package := "todoist-analytics"

# launch streamlit app
get_token:
	read token; \
	echo "token = " \"$$token\" > "./todoist_analytics/credentials.py"

credentials:
	[ -f ./todoist_analytics/credentials.py ] && echo credentials ok || $(MAKE) get_token

app:
	poetry run streamlit run streamlit_app.py

# black and isort
lint:  
	black .
	isort .

# build documentation 
docs:
	poetry run sphinx-build -a docs docs/site

# show documentation in browser
show:
	start docs/site/index.html

# publish documentation to Github Pages
pages:
	poetry run ghp-import docs/site 

# create rst source for API documentation
apidoc:
	sphinx-apidoc -o docs src/{{package}}