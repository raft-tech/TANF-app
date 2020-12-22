# Signed Report Urls

Grant access to a resource temporarily using aws keys.

**Request**:

`POST /v1/reports/signed_url**

**Parameters**:
```json
{
    "file_name":"string.txt",
    "file_type":"text/plain"
}
```

**Response**:

```json
Content-Type application/json
200 OK
{
    "signed_url":"https://cg-f0e35234-e70c-491c-a044-6836dd6abd59.s3.amazonaws.com/New%20Test.txt?AWSAccessKeyId=nljsandkjasb&Signature=zpKciPsJFZpa9PdgPy%2Fnn5azZjc%3D&content-type=text%2Fplain&Expires=1608584358"
}
```
