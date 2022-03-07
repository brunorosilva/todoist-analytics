package := "todoist-analytics"

# launch streamlit app
get_token:
	read token; \
	echo "token = " \"$$token\" > "./todoist_analytics/credentials.py"

credentials:
	[ -f ./todoist_analytics/credentials.py ] && echo credentials ok || $(MAKE) get_token

app:
	poetry run streamlit run streamlit_app.py --server.port 7070

# black and isort
lint:  
	poetry run black .
	poetry run isort .

checks:
	@poetry run flake8 .
	@poetry run vulture .
	@poetry run poetry check
	@poetry run safety check --full-report

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


container:
	@poetry build
	@docker build -t todoist_analytics .
	@docker run -p 8080:8080 todoist_analytics

heroku:
	@heroku container:push web --app todoist-analytics-mvp
	@heroku container:release web --app todoist-analytics-mvp