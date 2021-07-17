from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import bcrypt
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import certifi

with open("config.json", "r+") as c:
    params = json.load(c)["params"]

if params["local_server"] == "True":
    local_server = True
else:
    local_server = False

app = Flask(__name__)
if local_server:
    app.config["profile_pic_upload_location"] = os.path.join(os.getcwd() + "\static\\profile_pic\\")
    app.config["restaurant_pic_upload_location"] = os.path.join(os.getcwd() + "\static\\restaurant_profile_pic\\")
else:
    app.config["upload_location"] = os.path.join(os.getcwd() + "\static")
    app.config["upload_location"] = os.path.join(os.getcwd() + "\static")

client = MongoClient(params["database_url"],
                     tls=True,
                     tlsCAFile=certifi.where())

db = client.BookMyTable
userCollection = db.Users
restaurantCollection = db.Restaurant


@app.route("/sign_up_user", methods=["GET", "POST"])
def signupUser():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        # Check User exits or Not By Phone Number
        user = userCollection.find_one(
            {"user_phone_number": request.form["user_phone_number"]})
        if user:
            result["success"] = 1
            result["status"] = "user_available"
        else:
            # Save Profile Pic in folder and save file name in Db
            profile_pic = request.files["user_profile_pic"]
            profile_pic_file_name = secure_filename(
                request.form["user_auth_id"] + "_profile_pic_" +
                profile_pic.filename)
            profile_pic.save(
                os.path.join(app.config["profile_pic_upload_location"],
                             profile_pic_file_name))
            text_password = request.form["user_password"]
            hashed_password = bcrypt.hashpw(text_password.encode('utf-8'),
                                            bcrypt.gensalt())
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
            result["status"] = "user_created"

    return jsonify(result)


@app.route("/login_user", methods=["GET", "POST"])
def loginUser():
    result = dict()
    result["success"] = 0
    if request.method == "GET":
        # Check User exits or Not By Phone Number and password
        user = userCollection.find_one(
            {"user_phone_number": request.form["user_phone_number"]})
        if user is None:
            result["success"] = 1
            result["user_status"] = "user_not_available"
        else:
            text_password = request.form["user_password"]
            if bcrypt.checkpw(text_password.encode('utf-8'),
                              user["user_password"]):
                result["success"] = 1
                user_data = dict()
                user_data["user_id"] = str(user.get("_id"))
                user_data["user_name"] = user["user_name"]
                user_data["user_auth_id"] = user["user_auth_id"]
                user_data["user_email"] = user["user_email"]
                user_data["user_phone_number"] = user["user_phone_number"]
                user_data["user_profile_pic"] = params[
                    "image_path"] + "profile_pic/" + user["user_profile_pic"]
                user_data["user_location"] = user["user_location"]
                result["user_data"] = user_data
            else:
                result["success"] = 1
                result["user_status"] = "invalid_credentials"
    return jsonify(result)


@app.route("/update_user", methods=["GET", "POST"])
def updateUser():
    result = dict()
    result["success"] = 0

    if request.method == "POST":
        user = userCollection.find_one(
            {"_id": ObjectId(request.form["user_id"])})

        if user is None:
            result["success"] = 1
            result["status"] = "user_not_available"
        else:
            profile_pic_file_name = user["user_profile_pic"]

            # if any Change in Profile Pic then upload and change file name
            if request.form["profile_pic_updated"] == "true":

                #First Remove exits file so server keep clean
                os.remove(app.config["profile_pic_upload_location"] +
                          user["user_profile_pic"])

                #Now Upload New File
                profile_pic = request.files["user_profile_pic"]
                profile_pic_file_name = secure_filename(
                    request.form["user_auth_id"] + "_profile_pic_" +
                    profile_pic.filename)
                profile_pic.save(
                    os.path.join(app.config["upload_location"],
                                 profile_pic_file_name))

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


@app.route("/create_restaurant", methods=["GET", "POST"])
def createRestaurant():
    result = dict()
    result["success"] = 0
    if request.method == "POST":

        wait_user = dict()
        wait_user["user_id"] = ""
        wait_user["for"] = "2_seater"

        waiting_users = []

        table = dict()
        table["type"] = "2_seater"
        table["total_table"] = "3"
        table["available_table"] = "5"

        restaurant_tables = []

        restaurant = {
            "user_id": request.form["user_id"],
            "restaurant_name": request.form["restaurant_name"],
            "restaurant_pics": [],
            "restaurant_short_desc": request.form["restaurant_short_desc"],
            "restaurant_long_desc": request.form["restaurant_long_desc"],
            "restaurant_opening_time": request.form["restaurant_opening_time"],
            "restaurant_closing_time": request.form["restaurant_closing_time"],
            "restaurant_contact_number":
            request.form["restaurant_contact_number"],
            "restaurant_location": request.form["restaurant_location"],
            "status": "Pending",
            "waiting_users": waiting_users,
            "restaurant_tables": restaurant_tables
        }

        restaurantCollection.insert_one(restaurant)

        result["success"] = 1
        result["status"] = "restaurant_created"

    return jsonify(result)


@app.route("/get_restaurants", methods=["GET", "POST"])
def getRestaurant():
    result = dict()
    result["success"] = 0
    if request.method == "GET":
        restaurant = restaurantCollection.find(
            {"user_id": request.form["user_id"]})
        if restaurant is None:
            result["success"] = 1
            result["status"] = "restaurant_not_available"
            return jsonify(result)
        result["success"] = 1
        restaurant_data = []
        for res in restaurant:
            restaurant_pics=res["restaurant_pics"]
            restaurant_pics=appendUrl(restaurant_pics)
            rest_data = dict()
            rest_data["user_id"] = res["user_id"]
            rest_data["restaurant_name"] = res["restaurant_name"]
            rest_data["restaurant_id"] = str(res.get("_id"))
            rest_data["restaurant_pics"] = restaurant_pics
            rest_data["restaurant_short_desc"] = res["restaurant_short_desc"]
            rest_data["restaurant_long_desc"] = res["restaurant_long_desc"]
            rest_data["restaurant_opening_time"] = res[
                "restaurant_opening_time"]
            rest_data["restaurant_closing_time"] = res[
                "restaurant_closing_time"]
            rest_data["restaurant_contact_number"] = res[
                "restaurant_contact_number"]
            rest_data["restaurant_location"] = res["restaurant_location"]
            rest_data["waiting_users"] = res["waiting_users"]
            rest_data["restaurant_tables"] = res["restaurant_tables"]
            rest_data["status"] = res["status"]
            restaurant_data.append(rest_data)

        result["restaurant_data"] = restaurant_data

        return jsonify(result)
    return jsonify(result)


@app.route("/upload_restaurant_pic", methods=["GET", "POST"])
def uploadRestaurantPics():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        restaurant = restaurantCollection.find_one(
            {"_id": ObjectId(request.form["restaurant_id"])})

        if request.form["updated_pics_index"] != "True":
            restaurant_pics = restaurant["restaurant_pics"]
            restaurant_pics=checkPicsAndUploads(request,restaurant_pics)
            
        else:
            restaurant_pics = restaurant["restaurant_pics"]
            restaurant_pics=checkPicsAndReUploads(request,restaurant_pics)

        old_rest = {"_id": ObjectId(request.form["restaurant_id"])}
        updated_rest = {
                "$set": {
                    "restaurant_pics": restaurant_pics,
                }
            }
        restaurantCollection.update_one(old_rest,updated_rest)
        result["success"] = 1
        result["status"]="image_uploded"
        return jsonify(result)    
    return jsonify(result)


def appendUrl(restaurant_pics):
    res_data=[]
    for res in restaurant_pics:
        res_data.append(params["image_path"]+"restaurant_profile_pic/"+res)
    return res_data

def checkPicsAndUploads(request,restaurant_pics):
    rest_pic = request.files["upload_0"]
  
    for i in range(6):
        param="upload_"+str(i)
        if (param in request.files):
            rest_pic = request.files[param]
            f=FileStorage(filename=rest_pic.filename)
            rest_pic_file_name = secure_filename(request.form["restaurant_id"] +
                                                 "_restaurant_profile_pic_" +
                                                 param+"."+f.filename.split('.')[1])
            rest_pic.save(
                os.path.join(
                    app.config["restaurant_pic_upload_location"], rest_pic_file_name))
            restaurant_pics.append(rest_pic_file_name)

    return restaurant_pics      

def checkPicsAndReUploads(request,restaurant_pics):
    avail_len=len(restaurant_pics)
    for i in range(6):
        param="upload_"+str(i)
        if (param in request.files):

            # First Delating File  and if user enter this indexing images 2nd time
            if i<avail_len :    
                if(os.path.isfile(app.config["restaurant_pic_upload_location"]+restaurant_pics[i])):
                    os.remove(app.config["restaurant_pic_upload_location"]+restaurant_pics[i])
            

            rest_pic = request.files[param]

            f=FileStorage(filename=rest_pic.filename)
            rest_pic_file_name = secure_filename(request.form["restaurant_id"] +
                                                 "_restaurant_profile_pic_" +
                                                 param+"."+f.filename.split('.')[1])
            rest_pic.save(
                os.path.join(
                    app.config["restaurant_pic_upload_location"], rest_pic_file_name))
            if i < avail_len:
                restaurant_pics[i]=rest_pic_file_name
            else:
                restaurant_pics.append(rest_pic_file_name)

    return restaurant_pics        

if __name__ == "__main__":
    app.run(debug=True)
