# Authentication
For clients to authenticate, they have to authenticate with Login.gov via the backend service. Upon successful authentication the backend service will create an [httpOnly cookie](https://owasp.org/www-community/HttpOnly). 

 This will allow the backend to identify the browser which requested access and authorize them based on the cookie they provide in their API calls. 

 The secured portion of this authorization is due to the httpOnly cookie being inaccessible to the client's local browser. 

# Generating API token

In order to use APIs, the `OFA Admin` user has to generate a new token and use it in the API request following these steps:
1. User has to first login using frontend and going through the normal login process
2. After user is logged in, user can grab a token at `/v1/security/get-toke`
3. The token then can be used in authorization header. As an example:
   
```curl --location 'http://{host}/v1/users/' --header 'Authorization: Token {token}'```

Note the token is available for certain period of time: this is set using `TOKEN_EXPIRATION_HOURS` env vars. If not set, it is set to 24hrs by default.  
