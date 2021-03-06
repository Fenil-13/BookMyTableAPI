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
    app.config["restaurant_profile_pic_upload_location"] = os.path.join(
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
                user_data["user_profile_pic"] = "http://192.168.0.106:5000/static/profile_pic/" + \
                    str(user.get("_id"))+"_profile_pic_" + \
                    user["user_profile_pic"]
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
        user = userCollection.find_one(
            {"_id": ObjectId(request.form["user_id"])})
        try:
            if user["user_profile_pic"] != "":
                os.remove(app.config[f'{request.form["picture_type"]}_upload_location']+request.form["user_id"]
                          + "_"+request.form["picture_type"]+"_"+user["user_profile_pic"])
        except:
            print("Old file Not deleted")
        print(request.files["picture_file"])
        print(request.form["picture_type"])
        print(request.form["user_id"])
        picture_file = request.files["picture_file"]

        picture_file_name = secure_filename(request.form["user_id"]
                                            + "_"+request.form["picture_type"]+"_"+picture_file.filename)
        picture_file.save(
            os.path.join(app.config[f'{request.form["picture_type"]}_upload_location'],
                         picture_file_name))
        query = {"user_auth_id": user["user_auth_id"]}
        update = {"$set": {"user_profile_pic": picture_file.filename}}
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

        try:
            print(data["user_id"])
            user = userCollection.find_one(
                {"_id": ObjectId(data["user_id"])})

            if user is None:
                result["success"] = 1
                result["status"] = "user_not_available"
            else:
                old_user = {"_id": ObjectId(data["user_id"])}
                updated_user = {
                    "$set": {
                        "user_auth_id": data["user_auth_id"],
                        "user_name": data["user_name"],
                        "user_phone_number": data["user_phone_number"],
                        "user_email": data["user_email"],
                        "user_profile_pic": user["user_profile_pic"],
                        "user_device_token": data["user_device_token"],
                        "user_location": data["user_location"],
                    }
                }

                userCollection.update_one(old_user, updated_user)
                result["success"] = 1
                result["status"] = "user_updated"
        except:
            result["success"] = 1
            result["status"] = "user_not_updated"

    return jsonify(result)


@app.route("/fetch_users", methods=["GET", "POST"])
def fetchUsers():
    result = dict()
    result["success"] = 0
    query = userCollection.find()
    userList = list()
    for x in query:
        x["_id"] = str(x["_id"])
        # x.pop("user_password")
        if x["user_profile_pic"] != "":
            x["user_profile_pic"] = "http://192.168.0.106:5000/static/profile_pic/" + \
                x["_id"]+"_profile_pic_"+x["user_profile_pic"]
        userList.append(x)
    result["userList"] = userList
    result["success"] = 1
    return jsonify(result)


@app.route("/fetch_user_by_id", methods=["GET", "POST"])
def fetchUserById():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    try:
        user_id = data["user_id"]
        user = userCollection.find_one({"_id": ObjectId(user_id)})
        result["success"] = 1
        if user is None:
            result["status"] = "user not found"
        else:
            user["_id"] = str(user["_id"])
            result["status"] = "user found"
            result["user"] = user
            if result["user"]["user_profile_pic"] != "":
                result["user"]["user_profile_pic"] = "http://192.168.0.106:5000/static/profile_pic/" + \
                    result["user"]["_id"]+"_profile_pic_" + \
                    result["user"]["user_profile_pic"]
    except:
        result["success"] = 1
        result["status"] = "Internal Server Error"

    return jsonify(result)


@app.route("/fetch_all_restaurant", methods=["GET", "POST"])
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
        if user["user_profile_pic"] != "":
            x["user_profile_pic"] = "http://192.168.0.106:5000/static/profile_pic/" + \
                str(user["_id"])+"_profile_pic_"+user["user_profile_pic"]
        else:
            x["user_profile_pic"] = user["user_profile_pic"]
        x["user_email"] = user["user_email"]
        restaurantList.append(x)
    result["success"] = 1
    result["restaurantList"] = restaurantList
    return jsonify(result)


@app.route("/fetch_restaurant_by_id", methods=["GET", "POST"])
def fetchRestaurantById():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    restaurant_id = data["restaurant_id"]
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


@app.route("/add_tables", methods=["GET", "POST"])
def addTables():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    restaurant_id = data["restaurant_id"]
    table_type = data["table_type"]
    table_count = int(data["table_count"])
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
    # print(request.data)
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


@app.route("/book_table", methods=["GET", "POST"])
def bookTable():
    result = dict()
    result["success"] = 0
    try:
        data = json.loads(request.data.decode('utf8'))
        table_id = data["table_id"]
        table_type = data["table_type"]
        time_slot = data["time_slot"]
        user_id = data["user_id"]
        user_name = data["user_name"]
        booking_date = data["booking_date"]
        restaurant_id = data["restaurant_id"]
        restaurant_name = data["restaurant_name"]
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
            "booking_date": booking_date,
            "status": "Pending"
        }
        response = bookingCollection.insert_one(booking)

        result["success"] = 1
        result["status"] = "Booked"
        result["booking_id"] = str(response.inserted_id)
    except:
        result["success"] = 1
        result["status"] = "Not Booked"
    return jsonify(result)


@app.route("/booking_history", methods=["GET", "POST"])
def bookingHistory():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    user_id = data["user_id"]
    query = bookingCollection.find({"user_id": user_id})
    currentBookingList = list()
    if query.count() == 0:
        result["booking_count"] = 0
    else:
        result["booking_count"] = query.count()
        for x in query:
            x["_id"] = str(x["_id"])
            currentBookingList.append(x)
    currentBookingList.reverse()
    result["success"] = 1
    result["bookingList"] = currentBookingList
    return jsonify(result)


@app.route("/booking_list_by_restaurant_id", methods=["GET", "POST"])
def bookingListByRestaurantId():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    restaurant_id = data["restaurant_id"]
    query = bookingCollection.find(
        {"restaurant_id": restaurant_id})
    incompleteBookingList = list()
    completedBookingList = list()

    for x in query:
        x["_id"] = str(x["_id"])
        if x["status"] == "Pending":
            incompleteBookingList.append(x)
        if x["status"] == "Completed":
            completedBookingList.append(x)
    incompleteBookingList.reverse()
    completedBookingList.reverse()
    result["success"] = 1
    result["incompleteBookingList"] = incompleteBookingList
    result["completedBookingList"] = completedBookingList
    return jsonify(result)


@app.route("/cancel_booking", methods=["GET", "POST"])
def cancelBooking():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    booking_id = data["booking_id"]
    booking = bookingCollection.find_one({"_id": ObjectId(booking_id)})
    table_id = booking["table_id"]
    time_slot = booking["time_slot"]
    bookingCollection.delete_one({"_id": ObjectId(booking_id)})
    query = {"_id": ObjectId(table_id), "time_slot.time": time_slot}
    update = {"$inc": {"time_slot.$.available_table": 1}}
    tableCollection.update_one(query, update)
    result["success"] = 1
    return jsonify(result)


@app.route("/order_completed", methods=["GET", "POST"])
def orderCompleted():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    booking_id = data["booking_id"]
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
            "restaurant_pics": ["", "", "", ""],
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


@app.route("/update_restaurant", methods=["GET", "POST"])
def updateRestaurant():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    restaurant_id = data["restaurant_id"]
    query = restaurantCollection.find_one({"_id": ObjectId(restaurant_id)})
    if query is None:
        result["success"] = 1
        result["status"] = "restaurant not found"
    else:
        restaurant = {
            "$set": {
                "restaurant_name": data["restaurant_name"],
                "restaurant_short_desc": data["restaurant_short_desc"],
                "restaurant_long_desc": data["restaurant_long_desc"],
                "restaurant_opening_time": data["restaurant_opening_time"],
                "restaurant_closing_time": data["restaurant_closing_time"],
                "restaurant_contact_number": data["restaurant_contact_number"],
                "restaurant_location": data["restaurant_location"],
            }
        }
        restaurantCollection.update_one(
            {"_id": ObjectId(restaurant_id)}, restaurant)
        result["success"] = 1
        result["status"] = "restaurant updated"
    return jsonify(result)


@app.route("/user_get_restaurants", methods=["GET", "POST"])
def userGetRestaurants():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    user_id = data["user_id"]
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


@app.route("/owner_get_restaurant_tables", methods=["GET", "POST"])
def ownerGetRestaurantTables():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    restaurant_id = data["restaurant_id"]
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


@app.route("/owner_remove_restaurant_table", methods=["GET", "POST"])
def ownerRemoveRestaurantTables():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))
    table_id = ObjectId(data["table_id"])
    tableCollection.delete_one({"_id": table_id})
    result["success"] = 1

    return jsonify(result)


@app.route("/all_booking_history", methods=["GET", "POST"])
def allBookingHistory():
    result = dict()
    result["success"] = 0
    query = bookingCollection.find()
    currentBookingList = list()
    completedBookingList = list()
    if query.count() == 0:
        result["booking_count"] = 0
    else:
        result["booking_count"] = query.count()
        for x in query:
            x["_id"] = str(x["_id"])
            if x["status"] == "Pending":
                currentBookingList.append(x)
            else:
                completedBookingList.append(x)
    currentBookingList.reverse()
    completedBookingList.reverse()
    result["success"] = 1
    result["currentBookingList"] = currentBookingList
    result["completedBookingList"] = completedBookingList
    return jsonify(result)


@app.route("/verify_restaurant", methods=["GET", "POST"])
def verifyRestaurant():
    result = dict()
    result["success"] = 0
    data = json.loads(request.data.decode('utf8'))

    # os.remove(app.config['restaurant_profile_pic_upload_location_upload_location']+data["restaurant_id"]
    #                         + "_restaurant_profile_pic_"+restaurant["restaurant_pics"][0])
    # os.remove(app.config['restaurant_profile_pic_upload_location_upload_location']+data["restaurant_id"]
    #                         + "_restaurant_profile_pic"+_"+restaurant["restaurant_pics"][1])
    # os.remove(app.config['restaurant_profile_pic_upload_location_upload_location']+data["restaurant_id"]
    #                         + "_restaurant_profile_pic"+data["picture_type"]+"_"+restaurant["restaurant_pics"][2])
    # os.remove(app.config['restaurant_profile_pic_upload_location_upload_location']+data["restaurant_id"]
    #                         + "_restaurant_profile_pic"+data["picture_type"]+"_"+restaurant["restaurant_pics"][3])

    restaurant_id = data["restaurant_id"]
    restaurantCollection.update_one({"_id": ObjectId(restaurant_id)}, {
                                    "$set": {"status": "Verified",
                                             "restaurant_pics": ["", "", "", ""]}})
    result["success"] = 1
    result["status"] = "Verified"
    return jsonify(result)


@app.route("/uplod_restaurant_pics", methods=["GET", "POST"])
def uploadResturantPic():
    result = dict()
    try:
        restaurant = restaurantCollection.find_one(
            {"_id": ObjectId(request.form["restaurant_id"])})
        print(restaurant)
        print(restaurant["restaurant_pics"][0])
        if restaurant["restaurant_pics"][0] != '':
            os.remove(app.config[f'{request.form["picture_type"]}_upload_location']+request.form["restaurant_id"]
                      + "_"+request.form["picture_type"]+"_"+restaurant["restaurant_pics"][0])
            os.remove(app.config[f'{request.form["picture_type"]}_upload_location']+request.form["restaurant_id"]
                      + "_"+request.form["picture_type"]+"_"+restaurant["restaurant_pics"][1])
            os.remove(app.config[f'{request.form["picture_type"]}_upload_location']+request.form["restaurant_id"]
                      + "_"+request.form["picture_type"]+"_"+restaurant["restaurant_pics"][2])
            os.remove(app.config[f'{request.form["picture_type"]}_upload_location']+request.form["restaurant_id"]
                      + "_"+request.form["picture_type"]+"_"+restaurant["restaurant_pics"][3])

        pic1_file = request.files["pic1"]
        print(pic1_file)
        pic1_file_name = secure_filename(request.form["restaurant_id"]
                                         + "_"+request.form["picture_type"]+"_"+pic1_file.filename)

        print(f'{request.form["picture_type"]}_upload_location')
        pic1_file.save(
            os.path.join(app.config[f'{request.form["picture_type"]}_upload_location'],
                         pic1_file_name))

        pic2_file = request.files["pic2"]

        pic2_file_name = secure_filename(request.form["restaurant_id"]
                                         + "_"+request.form["picture_type"]+"_"+pic2_file.filename)
        pic2_file.save(
            os.path.join(app.config[f'{request.form["picture_type"]}_upload_location'],
                         pic2_file_name))

        pic3_file = request.files["pic3"]

        pic3_file_name = secure_filename(request.form["restaurant_id"]
                                         + "_"+request.form["picture_type"]+"_"+pic3_file.filename)
        pic3_file.save(
            os.path.join(app.config[f'{request.form["picture_type"]}_upload_location'],
                         pic3_file_name))

        pic4_file = request.files["pic4"]

        pic4_file_name = secure_filename(request.form["restaurant_id"]
                                         + "_"+request.form["picture_type"]+"_"+pic4_file.filename)
        pic4_file.save(
            os.path.join(app.config[f'{request.form["picture_type"]}_upload_location'],
                         pic4_file_name))

        updatedPics = [pic1_file.filename, pic2_file.filename,
                       pic3_file.filename, pic4_file.filename]
        print(updatedPics)
        query = {"_id": ObjectId(request.form["restaurant_id"])}
        update = {"$set": {"restaurant_pics": updatedPics}}
        restaurantCollection.update_one(query, update)
        result["success"] = 1
        result["updated_files"] = updatedPics
        return jsonify(result)
    except:
        result["success"] = 0
        result["updated_files"] = []
        return jsonify(result)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    result = dict()
    result["success"] = 0
    booking = bookingCollection.find()
    user = userCollection.find()
    resturant = restaurantCollection.find()
    result["booking_count"] = booking.count()
    result["user_count"] = user.count()
    result["resturant_count"] = resturant.count()
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
