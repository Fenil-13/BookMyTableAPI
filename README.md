# Hi, Programmers ! 👋

# BookMyTable API

Instant restaurant reservation at your favorite restaurants across several cities in India. · Discover and book a table on the go using bookmytable mobile app.

## API Reference

#### Crate user - signup

```http
  POST /sign_up_user
```

| Parameter           | Type     |
| :------------------ | :------- |
| `user_phone_number` | `string` |
| `user_name`         | `string` |
| `user_email`        | `string` |
| `user_password`     | `string` |
| `user_auth_id`      | `string` |
| `user_location`     | `string` |
| `user_profile_pic`  | `string` |
| `user_device_token` | `string` |

#### Response

```bash
  {
        "success": 1,
        "status": "user_created"
  }
```

```bash
  {
        "success": 1,
        "status": "user_available"
  }
```

#### Login User Profile

```http
  GET /login_user
```

| Parameter           | Type     |
| :------------------ | :------- |
| `user_phone_number` | `string` |
| `user_password`     | `string` |

#### Response

```bash
  {
        "success": 1,
        "status": "user_not_available"
  }
```

```bash
   {
    "success": 1,
      "user_data": {
          "user_auth_id": "sdfsdfdsdff",
          "user_email": "test@gmail.com",
          "user_id": "60f1b747d3deb982aea658a6",
          "user_location": "Gujarat",
          "user_name": "kp18",
          "user_phone_number": "9876543210",
          "user_profile_pic": "sdfsdfdsdff_profile_pic_IMG_5044.JPG"
       }
    }
```

#### Update User Profile

```http
  POST /update_user
```

| Parameter             | Type     |
| :-------------------- | :------- |
| `user_id`             | `string` |
| `user_phone_number`   | `string` |
| `user_name`           | `string` |
| `user_email`          | `string` |
| `user_password`       | `string` |
| `user_auth_id`        | `string` |
| `user_location`       | `string` |
| `user_profile_pic`    | `string` |
| `user_device_token`   | `string` |
| `profile_pic_updated` | `string` |

#### Response

```bash
  {
        "success": 1,
        "status": "user_not_available"
  }
```

```bash
  {
        "success": 1,
        "status": "user_updated"
  }
```

#### Create Restaurant Profile

```http
  POST /create_restaurant
```

| Parameter                   | Type     |
| :-------------------------- | :------- |
| `user_id`                   | `string` |
| `restaurant_name`           | `string` |
| `restaurant_short_desc`     | `string` |
| `restaurant_long_desc`      | `string` |
| `restaurant_opening_time`   | `string` |
| `restaurant_closing_time`   | `string` |
| `restaurant_contact_number` | `string` |
| `restaurant_location`       | `string` |

#### Response

```bash
  {
        "success": 1,
        "status": "restaurant_created"
  }
```

```bash
  {
        "success": 0
  }
```

#### Get Restaurant Profile of user

```http
  GET /get_restaurants
```

| Parameter | Type     |
| :-------- | :------- |
| `user_id` | `string` |

#### Response

```bash
  {
    "restaurant_data": [
        {
            "restaurant_closing_time": "11:00 PM",
            "restaurant_contact_number": "7573056506",
            "restaurant_id": "60f1a9c9e4fd91764295bc21",
            "restaurant_location": "Vadodara",
            "restaurant_long_desc": "Vadodara's most favourite Pizza Restaurant The D Pizza. Come and enjoy with unlimited food cold drink and Nitrogen Booster. Don't miss the chance to dance on music beats with our special dance light",
            "restaurant_name": "D Pizza",
            "restaurant_opening_time": "7:30 AM",
            "restaurant_pics": [
                "http://127.0.0.1:5000/static/restaurant_profile_pic/60f1a9c9e4fd91764295bc21_restaurant_profile_pic_upload_0.jpg",
                ...
            ],
            "restaurant_short_desc": "Hello Vadodara... We are unlock, We are ready to serve. The D Pizza introducing exciting offer for Pizza Lovers.",
            "restaurant_tables": [
                {
                    "available_table": 5,
                    "total_table": 3,
                    "type": "2_seater"
                },
                {
                    "available_table": 10,
                    "total_table": 4,
                    "type": "3_seater"
                },
                ...
            ],
            "status": "Under Verification",
            "user_id": "60f1b98c85357a37bdf8d626",
            "waiting_users": [
                {
                    "for": "2_seater",
                    "user_id": "156532"
                },
                ...
            ]
        },
        {
            "restaurant_closing_time": "12:00 PM",
            "restaurant_contact_number": "7573056506",
            "restaurant_id": "60f2e5ed7af7f8baa7b65078",
            "restaurant_location": "Vesu,Surat",
            "restaurant_long_desc": "The nice hostel to stay and celevrate the function",
            "restaurant_name": "TGB",
            "restaurant_opening_time": "07:00 AM",
            "restaurant_pics": [],
            "restaurant_short_desc": "The Best Hostel Now",
            "restaurant_tables": [],
            "status": "Pending",
            "user_id": "60f1b98c85357a37bdf8d626",
            "waiting_users": []
        },
        {
            "restaurant_closing_time": "12:00 PM",
            "restaurant_contact_number": "9723995961",
            "restaurant_id": "60f2f3f359a7fa9c2202a5ca",
            "restaurant_location": "Kamrej,Surat",
            "restaurant_long_desc": "McDonald's in Adajan Road, Surat. Desserts, Fast Food Cuisine Restaurant. Order Food Online. ",
            "restaurant_name": "Mcdonadls",
            "restaurant_opening_time": "07:00 AM",
            "restaurant_pics": [],
            "restaurant_short_desc": "McDonald's Corporation is an American fast food company",
            "restaurant_tables": [],
            "status": "Pending",
            "user_id": "60f1b98c85357a37bdf8d626",
            "waiting_users": []
        }
    ],
    "success": 1
}
```

```bash
  {
        "success": 0
  }
```

#### Update Restaurant Picture

```http
  POST /upload_restaurant_pic
```

| Parameter            | Type     | Desc       |
| :------------------- | :------- | :--------- |
| `restaurant_id`      | `string` |            |
| `updated_pics_index` | `string` | True/False |
| `upload_0`           | `string` |            |
| `upload_1`           | `string` |            |
| `---`                | `string` | continue   |

#### Response

```bash
  {
        "success": 1,
        "status": "image_uploded"
  }
```

```bash
  {
        "success": 0
  }
```

#### Update Restaurant Table

```http
  POST /upload_restaurant_table
```

| Parameter         | Type     | Desc     |
| :---------------- | :------- | :------- |
| `restaurant_id`   | `string` |          |
| `type`            | `string` | 2_seater |
| `total_table`     | `string` |          |
| `available_table` | `string` |          |

#### Response

```bash
  {
        "success": 1,
        "status": "2_seater_table_updated"
  }
```

```bash
  {
        "success": 0
  }
```

```bash
  {
        "success": 1.
        "status":"restaurant_not_available"
  }
```

#### Book Table

```http
  POST /book_table
```

| Parameter         | Type     | Desc            |
| :---------------- | :------- | :-------------- |
| `user_id`         | `string` |                 |
| `restaurant_id`   | `string` |                 |
| `restaurant_name` | `string` |                 |
| `booking_time`    | `string` |                 |
| `booking_date`    | `string` |                 |
| `table_type`      | `string` | 2_seater        |
| `table_quantity`  | `string` | 1/2             |
| `status`          | `string` | pending/confirm |

#### Response

```bash
  {
    "order_data": {
        "booking_id": "60f580eb0ddc47cfab8a814c",
        "status": "pending"
    },
    "success": 1
}
```

```bash
  {
        "success": 0
  }
```

#### Update Book Table

```http
  POST /update_book_table
```

| Parameter              | Type     | Desc            |
| :--------------------- | :------- | :-------------- |
| `booking_id`           | `string` |                 |
| `status`               | `string` | pending/confirm |
| `confirm_booking_time` | `string` |                 |

#### Response

```bash
  {
    "status": "updated_book_table_successfully",
    "success": 1
  }
```

```bash
  {
        "success": 0
  }
```

```bash
  {
        "success": 0,
        "status":"not_available_booking"
  }
```

#### Get Booking History

```http
  POST /get_booking_history
```

| Parameter       | Type     | Desc       |
| :-------------- | :------- | :--------- |
| `user_id`       | `string` |            |
| `by_user`       | `string` | True/False |
| `restaurant_id` | `string` |            |

#### Response

```bash
  {
    "success": 1
    "booking_data": [
        {
            "booking_date": "02/08/2001",
            "booking_id": "60f580eb0ddc47cfab8a814c",
            "booking_time": "07:00 PM",
            "confirm_booking_time": "",
            "restaurant_id": "60f570b163fa428c63631d87",
            "restaurant_name": "Mcdonadls",
            "status": "pending",
            "table_quantity": "3",
            "table_type": "2_seater",
            "user_id": "60f1b747d3deb982aea658a6"
        },
        {
            "booking_date": "02/08/2001",
            "booking_id": "60f585250aebcfc5f0279d3c",
            "booking_time": "07:00 PM",
            "confirm_booking_time": "",
            "restaurant_id": "60f570b163fa428c63631d87",
            "restaurant_name": "Mcdonadls",
            "status": "pending",
            "table_quantity": "3",
            "table_type": "2_seater",
            "user_id": "60f1b747d3deb982aea658a6"
        }
    ]
}
```

```bash
  {
        "success": 1,
        "status":"no_booking_history"
  }
```

```bash
  {
        "success": 0
  }
```

## Contributing

Contributions are always welcome!

## Support

For support, email fjmoradiya@gmail.com or krupalpatel1611@gmail.com .
