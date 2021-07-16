from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import bcrypt
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
    app.config["upload_location"] = os.path.join(os.getcwd()+"\static\profile_pic\\")
else:
    app.config["upload_location"] = os.path.join(os.getcwd()+"\static\profile_pic\\")

client = MongoClient(params["database_url"], tls=True, tlsCAFile=certifi.where())
db = client.BookMyTable
userCollection = db.Users


@app.route("/sign_up_user", methods=["GET", "POST"])
def signupUser():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        # Check User exits or Not By Phone Number
        user = userCollection.find_one(
            {"user_phone_number": request.form["user_phone_number"]}
        )
        if user:
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
            text_password = request.form["user_password"]
            hashed_password = bcrypt.hashpw(text_password.encode('utf-8'),bcrypt.gensalt())
            user = {
                "user_auth_id": request.form["user_auth_id"],
                "user_name": request.form["user_name"],
                "user_phone_number": request.form["user_phone_number"],
                "user_email": request.form["user_email"],
                "user_password": hashed_password,
                "user_profile_pic": profile_pic_file_name,
                "user_device_token": request.form["user_device_token"],
                "user_location": request.form["user_location"],
            }

            userCollection.insert_one(user)

            result["success"] = 1
            result["user_status"] = "created"

    return jsonify(result)

@app.route("/login_user", methods=["GET", "POST"])
def loginUser():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        # Check User exits or Not By Phone Number and password
        user = userCollection.find_one(
            {"user_phone_number": request.form["user_phone_number"]}
        )
        if user is None:
            result["success"] = 1
            result["user_status"] = "not_available"
        else: 
            text_password = request.form["user_password"]
            if bcrypt.checkpw(text_password.encode('utf-8'),user["user_password"]):
                result["success"] = 1
                result["user_name"] = user["user_name"]
                result["user_email"] = user["user_email"]
                result["user_phone_number"] = user["user_phone_number"]
                result["user_profile_pic"] = user["user_profile_pic"]
                result["user_location"] = user["user_location"]
                result["user_status"] = "loged_in"
            else:
                result["success"] = 1
                result["user_status"] = "invalid_credentials"
    return jsonify(result)


@app.route("/update_user",methods=["GET", "POST"])
def updateUser():
    result = dict()
    result["success"] = 0

    if request.method == "POST":
        user = userCollection.find_one({"_id": ObjectId(request.form["user_id"])})

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
            result["status"] = "user_updated"
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
