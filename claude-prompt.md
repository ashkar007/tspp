I am building a domain specific language called TSIL (Timeseries Intermediate Language) in Python.  The goal is to create a frontend for financial market timeseries analytics.  The backend will be a Python library that can be used to perform complex operations on timeseries data.  Think of it like a dataframe manipulation language, but with a syntax that is optimized for fetching correct financial timeseries data.

Help me build this application in python. I will plugin the API later to provide the actual data.  You can use mock data for now.  The application should have the following features:

- A parser that can parse TSIL expressions
- A lexer that can tokenize TSIL expressions
- A backend that can perform complex operations on timeseries data
- A frontend that can display the results of the operations

Project Structure:

TSIL/
├── lexer.py
├── parser.py
├── backend.py
├── frontend.py
└── main.py


