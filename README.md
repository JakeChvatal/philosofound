# philosofound2
A reboot of Philosofound, now written in Flask rather than Spring Boot! 
View the completed project at http://philosofound.com


Requirements:
- Python

To test:
1. Clone the repo

``` git clone https://github.com/JakeChvatal/philosofound2.git ```
```cd philosofound2```

2. Create a Python virtual environment (ensures that dependencies are only installed locally)
Windows:```python3 -m virtualenv env```
Mac/Linux:```py -m virtualenv env```

3. Install dependencies
```pip install -e .```

4. Define flask app as the flaskr folder
```set FLASK_APP=flaskr```

5. Set environment as development
```set FLASK_ENV=development```


6. Initialize the database
```flask init-db```

7. Run the application
```flask run```

Instructions should appear in the console supplying information for accessing the application.
