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
    # testing
if params["local_server"] == "True":
    local_server = True
else:
    local_server = False

app = Flask(__name__)
if local_server:
    app.config["profile_pic_upload_location"] = os.path.join(
        os.getcwd() + "\static\\profile_pic\\")
    app.config["restaurant_pic_upload_location"] = os.path.join(
        os.getcwd() + "\static\\restaurant_profile_pic\\")
else:
    app.config["upload_location"] = os.path.join(os.getcwd() + "\static")
    app.config["upload_location"] = os.path.join(os.getcwd() + "\static")

client = MongoClient(params["database_url"],
                     tls=True,
                     tlsCAFile=certifi.where())

db = client.BookMyTable
userCollection = db.Users
restaurantCollection = db.Restaurant
bookingCollection = db.Booking
tableCollection = db.tables


@app.route("/sign_up_user", methods=["GET", "POST"])
def signupUser():
    result = dict()
    result["success"] = 0
    if request.method == "POST":

        data = json.loads(request.data.decode('utf8'))

        # Check User exits or Not By Phone Number
        user = userCollection.find_one(
            {"user_phone_number": data["user_phone_number"]})
        if user:
            result["success"] = 1
            result["status"] = "user_already_available"
            return jsonify(result)
        else:
            # text_password = data["user_password"]
            # hashed_password = bcrypt.hashpw(text_password.encode('utf-8'),
            #                                 bcrypt.gensalt())
            user = {
                "user_auth_id": data["user_auth_id"],
                "user_name": data["user_name"],
                "user_phone_number": data["user_phone_number"],
                "user_email": data["user_email"],
                "user_profile_pic": "",
                "user_device_token": data["user_device_token"],
                "user_location": data["user_location"],
            }

            response = userCollection.insert_one(user)

            result["success"] = 1
            result["status"] = "user_created"
            result["id"] = str(response.inserted_id)
            return jsonify(result)
    return jsonify(result)


@app.route("/login_user", methods=["GET", "POST"])
def loginUser():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        # Check User exits or Not By Phone Number and password
        data = json.loads(request.data.decode('utf8'))
        user = userCollection.find_one(
            {"user_phone_number":  data["user_phone_number"]})

        if user is None:
            result["success"] = 1
            result["user_status"] = "user_not_available"

        else:

            if data["user_auth_id"] == user["user_auth_id"]:
                result["success"] = 1
                result["user_status"] = "user_available"
                user_data = dict()
                user_data["user_id"] = str(user.get("_id"))
                user_data["user_name"] = user["user_name"]
                user_data["user_auth_id"] = user["user_auth_id"]
                user_data["user_email"] = user["user_email"]
                user_data["user_phone_number"] = user["user_phone_number"]
                user_data["user_device_token"] = user["user_device_token"]
                user_data["user_profile_pic"] = params[
                    "image_path"] + "profile_pic/" + user["user_profile_pic"]
                user_data["user_location"] = user["user_location"]
                result["user_data"] = user_data
            else:
                result["success"] = 1
                result["user_status"] = "invalid_credentials"

    return jsonify(result)


@app.route("/upload_pic", methods=["GET", "POST"])
def uploadPic():
    result = dict()
    try:
        picture_file = request.files["picture_file"]
        picture_file_name = secure_filename(request.form["user_auth_id"]
                                            + "_"+request.form["picture_type"]+"_"+picture_file.filename)
        picture_file.save(
            os.path.join(app.config[f'{request.form["picture_type"]}_upload_location'],
                         picture_file_name))
        query = {"user_auth_id": request.form["user_auth_id"]}
        update = {"$set": {"user_profile_pic": picture_file_name}}
        userCollection.update_one(query, update)
        result["success"] = 1
        result["picture_filename"] = picture_file_name
        return jsonify(result)
    except:
        result["success"] = 0
        result["picture_filename"] = "Not Saved"
        return jsonify(result)


@app.route("/update_user", methods=["GET", "POST"])
def updateUser():
    result = dict()
    result["success"] = 0

    if request.method == "POST":
        data = json.loads(request.data.decode('utf8'))

        # Get user from user_id

        user = userCollection.find_one(
            {"_id": ObjectId(data["user_id"])})

        if user is None:
            result["success"] = 1
            result["status"] = "user_not_available"
        else:

            old_user = {"_id": ObjectId(data["user_id"])}

            hashed_password = bcrypt.hashpw(data["user_password"].encode('utf-8'),
                                            bcrypt.gensalt())

            updated_user = {
                "$set": {
                    "user_auth_id": data["user_auth_id"],
                    "user_name": data["user_name"],
                    "user_phone_number": data["user_phone_number"],
                    "user_email": data["user_email"],
                    "user_password": hashed_password,
                    "user_profile_pic": user["user_profile_pic"],
                    "user_device_token": data["user_device_token"],
                    "user_location": data["user_location"],
                }
            }

            userCollection.update_one(old_user, updated_user)
            result["success"] = 1
            result["status"] = "user_updated"
    return jsonify(result)


@app.route("/fetch_users")
def fetchUsers():
    result = dict()
    result["success"] = 0
    query = userCollection.find()
    userList = list()
    for x in query:
        x["_id"] = str(x["_id"])
        x.pop("user_password")
        userList.append(x)
    result["userList"] = userList
    result["success"] = 1
    return jsonify(result)


@app.route("/fetch_user_by_id")
def fetchUserById():
    result = dict()
    result["success"] = 0

    user_id = request.form["user_id"]
    user = userCollection.find_one({"_id": ObjectId(user_id)})

    if user is None:
        result["status"] = "user not found"
    else:
        user["_id"] = str(user["_id"])
        result["status"] = "user found"
        result["user"] = user
    result["success"] = 1
    return jsonify(result)


@app.route("/fetch_all_restaurant")
def fetchAllRestaurant():
    result = dict()
    result["success"] = 0
    query = restaurantCollection.find()
    restaurantList = list()
    for x in query:
        x["_id"] = str(x["_id"])
        user = userCollection.find_one(
            {"_id": ObjectId(x["user_id"])})
        x["user_name"] = user["user_name"]
        x["user_profile_pic"] = user["user_profile_pic"]
        x["user_email"] = user["user_email"]
        restaurantList.append(x)
    result["success"] = 1
    result["restaurantList"] = restaurantList
    return jsonify(result)


@app.route("/fetch_restaurant_by_id")
def fetchRestaurantById():
    result = dict()
    result["success"] = 0

    restaurant_id = request.form["restaurant_id"]
    restaurant = restaurantCollection.find_one(
        {"_id": ObjectId(restaurant_id)})

    if restaurant is None:
        result["status"] = "restaurant not found"
    else:
        restaurant["_id"] = str(restaurant["_id"])
        result["status"] = "restaurant found"
        result["restaurant"] = restaurant
    result["success"] = 1
    return jsonify(result)


@app.route("/add_tables", methods=["GET"])
def addTables():
    result = dict()
    result["success"] = 0
    restaurant_id = request.form["restaurant_id"]
    table_type = request.form["table_type"]
    table_count = int(request.form["table_count"])
    time_slot = list()

    for i in range(8, 23):
        temp = dict()
        temp["available_table"] = table_count
        temp["time"] = f"{i}:00 - {i+1}:00"
        time_slot.append(temp)

    table = {
        "restaurant_id": restaurant_id,
        "table_type": table_type,
        "table_count": table_count,
        "time_slot": time_slot
    }
    tableCollection.insert_one(table)
    result["success"] = 1
    result["status"] = "table_inserted"
    return jsonify(result)


# User Refereance
@app.route("/get_table_by_type", methods=["GET", "POST"])
def getTables():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))

    restaurant_id = data["restaurant_id"]
    table_type = data["table_type"]
    table = tableCollection.find_one(
        {"restaurant_id": restaurant_id, "table_type": table_type})
    if table is not None:
        result["success"] = 1
        result["table_id"] = str(table["_id"])
        temp = table["time_slot"]
        time_slot = list()
        for x in temp:
            if x["available_table"] > 0:
                time_slot.append(x)
        result["time_slot"] = time_slot
        result["status"] = "table_available"

        return jsonify(result)
    else:
        result["success"] = 1
        result["status"] = "table_not_available"
        return jsonify(result)
    result["status"] = "technical_error"
    return jsonify(result)


@app.route("/book_table", methods=["GET"])
def bookTable():
    result = dict()
    result["success"] = 0
    table_id = request.form["table_id"]
    table_type = request.form["table_type"]
    time_slot = request.form["time_slot"]
    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    restaurant_id = request.form["restaurant_id"]
    restaurant_name = request.form["restaurant_name"]
    query = {"_id": ObjectId(table_id), "time_slot.time": time_slot}
    update = {"$inc": {"time_slot.$.available_table": -1}}
    tableCollection.update_one(query, update)
    # update booking collection
    booking = {
        "user_id": user_id,
        "user_name": user_name,
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
        "table_id": table_id,
        "table_type": table_type,
        "time_slot": time_slot,
        "status": "Panding"
    }
    bookingCollection.insert(booking)

    result["success"] = 1
    return jsonify(result)


@app.route("/booking_history", methods=["GET"])
def bookingHistory():
    result = dict()
    result["success"] = 0
    user_id = request.form["user_id"]
    query = bookingCollection.find({"user_id": user_id})
    currentBookingList = list()
    completedBookingList = list()
    if query.count() == 0:
        result["booking_count"] = 0
    else:
        result["booking_count"] = query.count()
        for x in query:
            x["_id"] = str(x["_id"])
            if x["status"] == "Panding":
                currentBookingList.append(x)
            else:
                completedBookingList.append(x)
    result["success"] = 1
    result["currentBookingList"] = currentBookingList
    result["completedBookingList"] = completedBookingList
    return jsonify(result)


@app.route("/booking_list_by_restaurant_id")
def bookingListByRestaurantId():
    result = dict()
    result["success"] = 0
    restaurant_id = request.form["restaurant_id"]
    query = bookingCollection.find(
        {"restaurant_id": restaurant_id, "status": "Panding"})
    bookingList = list()
    if query.count() == 0:
        result["booking_count"] = 0
        result["success"] = 1
    else:
        for x in query:
            x["_id"] = str(x["_id"])
            bookingList.append(x)
        result["booking_count"] = query.count()
        result["success"] = 1
        result["bookingList"] = bookingList
    return jsonify(result)


@app.route("/cancel_booking")
def cancelBooking():
    result = dict()
    result["success"] = 0
    booking_id = request.form["booking_id"]
    booking = bookingCollection.find_one({"_id": ObjectId(booking_id)})
    table_id = booking["table_id"]
    time_slot = booking["time_slot"]
    bookingCollection.delete_one({"_id": ObjectId(booking_id)})
    query = {"_id": ObjectId(table_id), "time_slot.time": time_slot}
    update = {"$inc": {"time_slot.$.available_table": 1}}
    tableCollection.update_one(query, update)
    result["success"] = 1
    return jsonify(result)


@app.route("/order_completed")
def orderCompleted():
    result = dict()
    result["success"] = 0
    booking_id = request.form["booking_id"]
    booking = bookingCollection.find_one({"_id": ObjectId(booking_id)})
    table_id = booking["table_id"]
    time_slot = booking["time_slot"]
    query = {"_id": ObjectId(table_id), "time_slot.time": time_slot}
    update = {"$inc": {"time_slot.$.available_table": 1}}
    tableCollection.update_one(query, update)
    bookingCollection.update_one({"_id": ObjectId(booking_id)}, {
                                 "$set": {"status": "Completed"}})
    result["success"] = 1
    return jsonify(result)


@app.route("/create_restaurant", methods=["GET", "POST"])
def createRestaurant():
    result = dict()
    result["success"] = 0
    if request.method == "POST":
        data = json.loads(request.data.decode('utf8'))

        restaurant = {
            "user_id": data["user_id"],
            "restaurant_name": data["restaurant_name"],
            "restaurant_pics": [],
            "restaurant_short_desc": data["restaurant_short_desc"],
            "restaurant_long_desc": data["restaurant_long_desc"],
            "restaurant_opening_time": data["restaurant_opening_time"],
            "restaurant_closing_time": data["restaurant_closing_time"],
            "restaurant_contact_number": data["restaurant_contact_number"],
            "restaurant_location": data["restaurant_location"],
            "status": "Pending",
        }

        restaurantCollection.insert_one(restaurant)

        result["success"] = 1
        result["status"] = "restaurant_created"
        return jsonify(result)
    result["status"] = "technical_error"
    return jsonify(result)


@app.route("/update_restaurant")
def updateRestaurant():
    result = dict()
    result["success"] = 0

    restaurant_id = request.form["restaurant_id"]
    query = restaurantCollection.find_one({"_id": ObjectId(restaurant_id)})
    if query is None:
        result["success"] = 1
        result["status"] = "restaurant not found"
    else:
        restaurant = {
            "$set": {
                "restaurant_name": request.form["restaurant_name"],
                "restaurant_short_desc": request.form["restaurant_short_desc"],
                "restaurant_long_desc": request.form["restaurant_long_desc"],
                "restaurant_opening_time": request.form["restaurant_opening_time"],
                "restaurant_closing_time": request.form["restaurant_closing_time"],
                "restaurant_contact_number": request.form["restaurant_contact_number"],
                "restaurant_location": request.form["restaurant_location"],
            }
        }
        restaurantCollection.update_one(
            {"_id": ObjectId(restaurant_id)}, restaurant)
        result["success"] = 1
        result["status"] = "restaurant updated"
    return jsonify(result)


@app.route("/admin_get_restaurants")
def adminGetRestaurants():
    result = dict()
    result["success"] = 0

    user_id = request.form["user_id"]
    query = restaurantCollection.find({"user_id": user_id})

    if query.count() == 0:
        result["success"] = 1
        result["restaurant_count"] = 0
    else:
        restaurantList = list()
        for x in query:
            x["_id"] = str(x["_id"])
            restaurantList.append(x)
        result["success"] = 1
        result["restaurant_count"] = query.count()
        result["restaurantList"] = restaurantList

    return jsonify(result)


@app.route("/admin_get_tables")
def adminGetTables():
    result = dict()
    result["success"] = 0

    restaurant_id = request.form["restaurant_id"]
    query = tableCollection.find({"restaurant_id": restaurant_id})
    if query.count() == 0:
        result["success"] = 1
        result["table_count"] = 0
    else:
        tableList = list()
        for x in query:
            x["_id"] = str(x["_id"])
            tableList.append(x)
        result["success"] = 1
        result["table_count"] = query.count()
        result["tableList"] = tableList

    return jsonify(result)


@app.route("/admin_remove_table")
def adminRemoveTable():
    result = dict()
    result["success"] = 0

    table_id = ObjectId(request.form["table_id"])
    tableCollection.delete_one({"_id": table_id})
    result["success"] = 1

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
