# philosofound2
A reboot of philosofound, now with flask rather than Spring Boot!
This is a modified tutorial as it stands but is in the process of being updated to conform to our app

Python 3 is required to run this (goes without saying)

To test:
Clone the repo
``` git clone https://github.com/JakeChvatal/philosofound2.git ```
```cd philosofound2```

Create a Python virtual environment (ensures that dependencies are only installed locally)
Windows:```python3 -m virtualenv env```
Mac/Linux:```py -m virtualenv env```

Install dependencies
```pip install -e .```

Define flask app as the flaskr folder
```set FLASK_APP=flaskr```

Set environment as development
```set FLASK_ENV=development```


Initialize the database
```flask init-db```

Run the application
```flask run```

Instructions should appear in the console supplying information for accessing the application.