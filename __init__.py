from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import certifi

with open("config.json", "r+") as c:
    params = json.load(c)["params"]

if params["local_server"] == "True":
    local_server = True
else:
    local_server = False

app = Flask(__name__)
if local_server:
    app.config["upload_location"] = params["local_upload_location"]
else:
    app.config["upload_location"] = params["prod_upload_location"]

client = MongoClient(params["database_url"], tls=True, tlsCAFile=certifi.where())
db = client.BookMyTable
userCollection = db.Users


@app.route("/sign_up_user", methods=["GET", "POST"])
def signupUser():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        # Check User exits or Not By Phone Number
        user = userCollection.find(
            {"user_phone_number": request.form["user_phone_number"]}
        )
        if user is None:
            result["success"] = 1
            result["user_status"] = "available"
        else:
            # Save Profile Pic in folder and save file name in Db 
            profile_pic = request.files["user_profile_pic"]
            profile_pic_file_name = secure_filename(
                request.form["user_auth_id"] + "_profile_pic_" + profile_pic.filename
            )
            profile_pic.save(
                os.path.join(app.config["upload_location"], profile_pic_file_name)
            )

            user = {
                "user_auth_id": request.form["user_auth_id"],
                "user_name": request.form["user_name"],
                "user_phone_number": request.form["user_phone_number"],
                "user_email": request.form["user_email"],
                "user_password": request.form["user_password"],
                "user_profile_pic": profile_pic_file_name,
                "user_device_token": request.form["user_device_token"],
                "user_location": request.form["user_location"],
            }

            userCollection.insert_one(user)

            result["success"] = 1
            result["user_status"] = "user_created"

    return jsonify(result)


@app.route("/update_user", methods=["GET"])
def updateUser():
    result = dict()
    result["success"] = 0

    user=None
    
    try:
        user = userCollection.find_one({"_id": ObjectId(request.form["user_id"])})
    except:
        result["success"] = 1
        result["status"] = "user_not available"

    if user is None:
        result["success"] = 1
        result["status"] = "user_not available"
    else:
        profile_pic_file_name = user["user_profile_pic"]

        # if any Change in Profile Pic then upload and change file name
       
        if request.form["profile_pic_updated"] == "true":

            #First Remove exits file so server keep clean
            os.remove(app.config["upload_location"]+user["user_profile_pic"])

            #Now Upload New File
            profile_pic = request.files["user_profile_pic"]
            profile_pic_file_name = secure_filename(
                request.form["user_auth_id"] + "_profile_pic_" + profile_pic.filename
            )
            profile_pic.save(
                os.path.join(app.config["upload_location"], profile_pic_file_name)
            )

        old_user = {"_id": ObjectId(request.form["user_id"])}
        updated_user = {
            "$set": {
                "user_auth_id": request.form["user_auth_id"],
                "user_name": request.form["user_name"],
                "user_phone_number": request.form["user_phone_number"],
                "user_email": request.form["user_email"],
                "user_password": request.form["user_password"],
                "user_profile_pic": profile_pic_file_name,
                "user_device_token": request.form["user_device_token"],
                "user_location": request.form["user_location"],
            }
        }

        userCollection.update_one(old_user, updated_user)
        result["success"] = 1
        result["status"] = "user_updated_successfully"
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
