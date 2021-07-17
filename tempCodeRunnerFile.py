 # for i in range(6):
    #     param="upload_"+str(i)
    #     print(param)
    #     if (param in request.files):
    #         rest_pic = request.files[param]
    #         rest_pic_file_name = secure_filename(request.form["restaurant_id"] +
    #                                              "_restaurant_profile_pic_" +
    #                                              rest_pic.filename)
    #         rest_pic.save(
    #             os.path.join(
    #                 app.config["upload_location"] +
    #                 "\restaurant_profile_pic\\", rest_pic_file_name))