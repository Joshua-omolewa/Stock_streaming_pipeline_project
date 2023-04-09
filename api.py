#created by joshua omolewa

#importing required library 
import boto3
import csv
import io
import json
import toml #library to load my configuration files
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()
current_line = 0  #To keep track of the current row so  it is initially set to zero
app_config = toml.load('config.toml') #loading aws configuration files
access_key = app_config['s3']['keyid'] #getting access key id from config.toml file
secret_access_key = app_config['s3']['keysecret'] #getting access key secrets from config.toml file
s3 = boto3.client('s3' , aws_access_key_id=access_key, aws_secret_access_key=secret_access_key) #access s3 high level api to interact with s3


triggered = False

def trigger_airflow():
    # Make request to Airflow endpoint
    response = requests.post('http://54.82.46.217:8080/api/experimental/dags/invoke_lambda_and_check_batch_status/dag_runs',
                             json={'conf': {'triggered_by': 'stock'}})
    # Check response status code
    if response.status_code == 200:
        print('Airflow DAG triggered successfully')
    else:
        print('Error triggering Airflow DAG')

"""
Defining API endpoints using the @app.get() decorator
"""

@app.get("/", response_class=HTMLResponse)
async def root():

    """
    Creating the API landing page using HTML & CSS
    """
    return """
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <title>Welcome to Joshua Stock API</title>
            <style>
              body {
                background-color: #F5F5F5;
                font-family: Arial, sans-serif;
              }
              #container {
                width: 80%;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #FFFFFF;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
              }
              h1 {
                color: #008CBA;  /* Changed color to blue */
                text-align: center;
                white-space: nowrap; /* Prevents wrapping */
                overflow: hidden; /* Hides overflow */
                position: relative; /* Positions the text relative to the container */
                animation: marquee 10s linear infinite; /* Starts animation */
              }
              @keyframes marquee {
                0% { transform: translateX(50%); } /* Starts from the middle */
                50% { transform: translateX(0%); } /* Moves to the left */
                100% { transform: translateX(-50%); } /* Comes out from the right */
              }
              p {
                color: #555555;
                font-size: 18px;
                line-height: 1.5;
                margin: 20px 0;
              }
              a {
                color: #FFFFFF;
                background-color: #008CBA;
                border-radius: 5px;
                padding: 10px 20px;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
              }
              a:hover {
                background-color: #00587A;
              }
            </style>
          </head>
          <body>
            <div id="container">
              <h1>Welcome to Joshua Stock API</h1>
              <p>Please use end point <code>http://127.0.0.1:8000/stock</code> in local machine to get real time stock data per request</p>
              <a href="#">Get Started</a>
            </div>
          </body>
        </html>
    """

@app.get("/stock")
async def get_line():
    """
    This api reads the CSV file from the last row to the first row, which makes it easier to retrieve the latest data .
    Note: the stock data from csv file  has the oldest data at the bottom
    """

    """
    added a global boolean variable triggered that keeps track of whether the Airflow DAG has already been triggered. 
    When the /stock endpoint is called for the first time, the trigger_airflow function is called to make the request to the Airflow endpoint, 
    and the triggered flag is set to True to indicate that the request has been triggered. On subsequent calls to the /stock endpoint, 
    the trigger_airflow function is not called again because the triggered flag is already set to True
    """
    global triggered
    if not triggered:
        trigger_airflow()
        triggered = True

    """
     global current_line is a global variable that keeps track of the current line that has been retrieved from the CSV file
    """
    global current_line 
    obj = s3.get_object(Bucket='finalproject-streamdata', Key='amazon.csv')

    """
    io.StringIO is used to parse the CSV data obtained from S3. The CSV data is read from S3 as a binary string using obj['Body'].read(). 
    This binary string is then decoded into a UTF-8 string using the decode() method. 
    This decoded string is then passed to io.StringIO to create a file-like object that can be read using the csv.reader() method.
    """
    file = io.StringIO(obj['Body'].read().decode('utf-8'))
    reader = csv.reader(file)
    header = next(reader)
    lines = [row for row in reader] #list compression of all the rows in the csv file
    try:
        line = lines[len(lines) - 1 - current_line]  #expression calculates the index of the line to be retrieved from the lines list, which contains all the lines of the CSV file.
        result = {header[i]: line[i] for i in range(len(header))}
        result["symbol"] = "AMZN" #adding the a new column called symbol with value IBM to the data gotten from csv file
        current_line += 1   # keeps track of the current row in the csv file
        return result
    except IndexError:
        current_line = 0
        return {"error": "end of file"}

@app.get("/line/{line_number}")
async def get_line_by_number(line_number: int):
    """
    optional api for trouble shooting
    API retrieves the stock data for a specific row by passing the row number as a parameter
    """
    obj = s3.get_object(Bucket='finalproject-streamdata', Key='amazon.csv')

    """
    io.StringIO is used to parse the CSV data obtained from S3. The CSV data is read from S3 as a binary string using obj['Body'].read(). 
    This binary string is then decoded into a UTF-8 string using the decode() method. 
    This decoded string is then passed to io.StringIO to create a file-like object that can be read using the csv.reader() method.
    """
    file = io.StringIO(obj['Body'].read().decode('utf-8'))
    reader = csv.reader(file)
    header = next(reader)
    lines = [row for row in reader]
    try:
        line = lines[len(lines) - 1 - line_number]
        result = {header[i]: line[i] for i in range(len(header))}
        result["symbol"] = "AMZN"
        return result
    except IndexError:
        return {"error": "line not found"}

@app.get("/stock1")
async def get_line():
    """
    This api reads the CSV file from the last row to the first row, which makes it easier to retrieve the latest data .
    Note: the stock data from csv file  has the oldest data at the bottom
    """

    """
     global current_line is a global variable that keeps track of the current line that has been retrieved from the CSV file
    """
    global current_line 
    obj = s3.get_object(Bucket='finalproject-streamdata', Key='apple.csv')

    """
    io.StringIO is used to parse the CSV data obtained from S3. The CSV data is read from S3 as a binary string using obj['Body'].read(). 
    This binary string is then decoded into a UTF-8 string using the decode() method. 
    This decoded string is then passed to io.StringIO to create a file-like object that can be read using the csv.reader() method.
    """
    file = io.StringIO(obj['Body'].read().decode('utf-8'))
    reader = csv.reader(file)
    header = next(reader)
    lines = [row for row in reader] #list compression of all the rows in the csv file
    try:
        line = lines[len(lines) - 1 - current_line]  #expression calculates the index of the line to be retrieved from the lines list, which contains all the lines of the CSV file.
        result = {header[i]: line[i] for i in range(len(header))}
        result["symbol"] = "AAPL" #adding the a new column called symbol with value IBM to the data gotten from csv file
        current_line += 1   # keeps track of the current row in the csv file
        return result
    except IndexError:
        current_line = 0
        return {"error": "end of file"}

@app.get("/line1/{line_number}")
async def get_line_by_number(line_number: int):
    """
    optional api for trouble shooting
    API retrieves the stock data for a specific row by passing the row number as a parameter
    """
    obj = s3.get_object(Bucket='finalproject-streamdata', Key='apple.csv')

    """
    io.StringIO is used to parse the CSV data obtained from S3. The CSV data is read from S3 as a binary string using obj['Body'].read(). 
    This binary string is then decoded into a UTF-8 string using the decode() method. 
    This decoded string is then passed to io.StringIO to create a file-like object that can be read using the csv.reader() method.
    """
    file = io.StringIO(obj['Body'].read().decode('utf-8'))
    reader = csv.reader(file)
    header = next(reader)
    lines = [row for row in reader]
    try:
        line = lines[len(lines) - 1 - line_number]
        result = {header[i]: line[i] for i in range(len(header))}
        result["symbol"] = "AAPL"
        return result
    except IndexError:
        return {"error": "line not found"}

if __name__ == "__main__":

    """
    the program starts the FastAPI server using app.run(port=8000) on port 8000. 
    The API can be accessed by sending HTTP requests to the endpoints at 
    """
    app.run(port=8000)