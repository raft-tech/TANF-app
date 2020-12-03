# Groupless users list

Get a list of users who have yet to be assigned to a role

**Request**:

`GET /v1/users/no_roles`

Parameters:


 A valid httpOnly cookie in the request header to track the users session

*Note:*

- Authorization Protected 

**Response**:

```json
Content-Type: Application/json
200 OK

[
  {
    "id":"1fe8525c-5e91-4adb-8eb6-a0d3152a3fff",
    "username":"user@example.com",
    "first_name":"User",
    "last_name":"Name"
  },
  {
    "id":"a6b3d2ff-e5e6-3f9a-8eb6-b0a53fffafff",
    "username":"user@example.com",
    "first_name":"Jane",
    "last_name":"Doe"
  },
  {
    "id":"b0a5525c-e6e5-ff9a-8eb6-3fffaf3fb0a5a6b3",
    "username":"user@example.com",
    "first_name":"Jane",
    "last_name":"Doe"
  }
]
```

### Fields

This will return a json response with all users who are currently not associated with any groups/roles

+ `first_name` : string (first name of user)
+ `last_name` : string (last name of user)
+ `username` : string (email of user)
+ `id` : string (UUID of user, used to locate a user in various queries)



**Failure to Authenticate Response:**

```json
Content-Type application/json
403 Forbidden

{
  "detail": "Authentication credentials were not provided."
}
```
----
**Calls made by authorized users who aren't Admins:**
```json
Content-Type application/json
500 Internal Server Error

System Error Message:
Does Not Exist
Group matching query does not exist.
