import os
import json
import datetime
from uuid import uuid4
import pymysql
import pymysql.cursors

## GLOBALS

db = pymysql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USERNAME"], passwd=os.environ["DB_PASSWORD"], db=os.environ["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)

## HELPERS

def mysql_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

## FUNCTIONS

def get_users(event, context):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users;")
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchall(), default=mysql_converter)
        return result

def register_user(event, context):
    email = event["email"]
    username = event["username"]
    password = event["password"]
    org_id = event["org_id"]

    with db.cursor() as cursor:
        sql = "INSERT INTO Users (email, username, password, api_key, org_id, updated_at, created_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW());"
        cursor.execute(sql, (email, username, password, str(uuid4()), org_id))
    db.commit()

    with db.cursor() as cursor:
        sql = "SELECT * FROM Users WHERE email = %s"
        cursor.execute(sql, (email, ))
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchone(), default=mysql_converter)
        return result
        
def login(event, context):
    username = event["username"]
    password = event["password"]

    with db.cursor() as cursor:
        sql = "SELECT * FROM Users WHERE username = %s and password = %s;"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
    
    result = {}
    if user is None:
        result["status"] = 400
        result["body"] = json.dumps({})
        return result

    with db.cursor() as cursor:
        sql = "SELECT * FROM Organizations WHERE id = %s;"
        cursor.execute(sql, (user["org_id"], ))
        user["org"] = cursor.fetchone()

    result["status"] = 200
    result["body"] = json.dumps(user, default=mysql_converter)
    return result


if __name__ == "__main__":
    req = {}
    req["username"] = "fakeusername1"
    req["password"] = "fakepassword1"
    print(login(req, ''))