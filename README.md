
# Hi, Programmers ! 👋

# BookMyTable API

Instant restaurant reservation at your favorite restaurants across several cities in India. · Discover and book a table on the go using bookmytable mobile app.

## API Reference

#### Crate user - signup

```http
  POST /sign_up_user
```

| Parameter | Type     |
| :-------- | :------- |
| `user_phone_number` | `string` |
| `user_name` | `string` |
| `user_email` | `string` |
| `user_password` | `string` |
| `user_auth_id` | `string` |
| `user_location` | `string` |
| `user_profile_pic` | `string` |
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


#### Update User Profile

```http
  POST /update_user
```

| Parameter | Type     |
| :-------- | :------- |
| `user_id` | `string` |
| `user_phone_number` | `string` |
| `user_name` | `string` |
| `user_email` | `string` |
| `user_password` | `string` |
| `user_auth_id` | `string` |
| `user_location` | `string` |
| `user_profile_pic` | `string` |
| `user_device_token` | `string` |
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

    

#### Login User Profile

```http
  POST /login_user
```

| Parameter | Type     |
| :-------- | :------- |
| `user_phone_number` | `string` |
| `user_password` | `string` |

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

  
## Contributing

Contributions are always welcome!


## Support

For support, email fjmoradiya@gmail.com or krupalpatel1611@gmail.com .
