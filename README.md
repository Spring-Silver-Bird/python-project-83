### Hexlet tests and linter status:
[![Actions Status](https://github.com/Spring-Silver-Bird/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Spring-Silver-Bird/python-project-83/actions)
[![my check](https://github.com/Spring-Silver-Bird/python-project-83/actions/workflows/project_check.yml/badge.svg)](https://github.com/Spring-Silver-Bird/python-project-83/actions/workflows/project_check.yml)

### Description
This is a study project - web-app for brief seo-analysis of sites by url.

### Technologies
This project is made with:
- uv package manager
- flask
- ruff as linter
- postgresql and psycopg2
- gunicorn 
- python libraries for work with http: requests and validators
- pytest and pytest-cov

Site is available [here](https://page-analyzer-2q1h.onrender.com//)

---

## Installation

### Clone the repository:

```
git clone git@github.com:Spring-Silver-Bird/python-project-83.git
```

```
cd python-project-83
```

### To use this application, you need to configure the .env file.

After cloning the repository, rename the .env_example file to .env. Inside the file, you will find the SECRET_KEY and
DATABASE_URL variables. Replace their values with your own.
****

### Next, use the command below to install the required dependencies and generate the database tables.

```
make build
```

### Start the application with the following command:

```
make start
```