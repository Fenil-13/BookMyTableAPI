from flask import Flask, render_template, request ,session,jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json
from werkzeug.utils import secure_filename
import certifi


with open('config.json', 'r+') as c:
    params = json.load(c)["params"]

if params['local_server'] == "True":
    local_server = True
else:
    local_server = False

app = Flask(__name__)
app.config['upload_location'] = params['upload_location']
client = MongoClient("mongodb+srv://admin:krupal123@cluster0.r0oii.mongodb.net/BookMyTable?retryWrites=true&w=majority",tls=True,tlsCAFile=certifi.where())
db = client.BookMyTable
userCollection = db.Users

# res = userCollection.find_one({'_id': ObjectId('60eee32180b8955038913e5f')})
all_user = userCollection.find()

@app.route("/signupuser",methods=['GET','POST'])
def signupUser():
    result=dict();
    if request.method=="POST":
        user=userCollection.find({"user_phone_number":request.form["user_phone_number"]})
        if (user==None) :
            result["success"]=1;
            result["user_status"]="available"
        else :

            profile_pic = request.files['user_profile_pic']
            profile_pic.save(os.path.join(
                    app.config['upload_location'], secure_filename(profile_pic.filename)))

            user={"user_auth_id":request.form["user_auth_id"],
            "user_name":request.form["user_name"],
            "user_phone_number":request.form["user_phone_number"],
            "user_email":request.form["user_email"],
            "user_password":request.form["user_password"],
            "user_profile_pic": profile_pic.filename,
            "user_device_token":request.form["user_device_token"],
            "user_location":request.form["user_location"]
                }
            
            userCollection.insert_one(user)
            result["success"]=1;
            result["user_status"]="user_created"
    else:
         result["success"]=0;

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)