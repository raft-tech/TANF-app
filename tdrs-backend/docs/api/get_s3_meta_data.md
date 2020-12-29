# Get S3 Meta Data 

Aceepts a GET request to get S3 slug and other data associated with the file. When the frontend needs to get a file, it will hit this endpoint to locate the most recent version of a report file.

**Request**

`GET /v1/reports/<str:year>/<str:quarter>/<str:section>`


## Parameters

+ year : Year of the report ("2020","2021",etc)
+ quarter : String representing the quarter of the year ("Q1","Q2","Q3","Q4")
+ section : String representing the section of the report ("Active Case Data", "Close Case Data","Aggregate Data",  "Stratum Data")


## Request body 

```json
Content-Type application/json
200 Ok

{

            "original_filename":"filename", 
            "slug":"hdslajhfdaksdjflajlsdfa",
            "extension":"txt",
            "user":"lnsdfkldlkajdfa",
            "stt":15 
            "year": 2020,
            "quarter":"Q1", 
            "section":"Active Case Data", 
            "version":2
}
```

This will return a JSON response with the report file meta data composed of the following:
+ original_filename : Name of the file before being uploaded
+ slug : String identifying the file in s3
+ extension : The files extension, if none is provided or the file has no extension, we assume text
+ user : A UUID Identifying the user who uploaded this file.
+ stt : A numeric ID representing the STT this report is for
+ year : The year this is a report for
+ quarter : The quarter this is a report for as "Q1", etc
+ section : The section of the report this file is a part of.
+ version : the version of this file
