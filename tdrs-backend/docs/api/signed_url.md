# Signed url

Accepts an aws client method string, a file name, and a file type. File type is not used if client method is not `put_object`. 
Produces a signed s3 url, which is used to temporarily grant permission to access an s3 resource.

**Request**

`POST` `/v1/reports/signed_url`

Parameters:
```json
{
    "client_method":"put_object",
    "file_name":"report.txt",
    "file_type":"text/plain"
}
```

`client_method` AWS s3 client method, defines expected behavior of pr. 
    Possilble options are 
    + "put_object"
    + "get_object"
`file_name` original name of the file. This is the value that will be passed to `POST /v1/reports/` to create
    the database entry
`file_type` Only useful for `put_object`, the mime type of the file being uploaded. 
    Can be infered from file extension if it is present.

**Note:**

- Authorization Protected 
- Only OFA admin and OFA analyst roles can access this end point.

**Response**

```json
Content-Type application/json
200 Ok
{
    "signed_url":"https://cg-f073b546-cf1c-4960-845f-746318ebc15e.s3.us-gov-west-1.amazonaws.com/28b98dc2-80ec-11eb-9439-0242ac130002?AWSAccessKeyId=AKIAR7FXZINYNGDGPPZ5&Signature=6pAg9%2BwoCfOH%2FlAIlUYu1OksFV8%3D&content-type=text&Expires=1615305483"
}
```

This will return a json response with a signed url the client can use to perform the 
action denoted in the request by `client_method`.
