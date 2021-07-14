
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


  
## Contributing

Contributions are always welcome!

  