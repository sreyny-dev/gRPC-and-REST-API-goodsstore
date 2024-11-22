# JWT + OpenAPI Generator
This codebase provides a PoC implementation of using JWT-based authentication in OpenAPI-generated Python Flask code.

**NOTE: if pure Flask server is intended without using OpenAPI Generator, check this official documentation instead: https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html.**

## Requirements
- Check `requirements.txt` in the `generated/` folder for Python requirements. Set up with `python -m pip install -r generated/requirements.txt`. Note that `pwjwt` is additionally required.
- Docker

## Update OpenAPI Specification File
The `auth_demo.yaml` records the API specifications of how the client will interact with the server. We will use this file to generate a code stub for our backend server.

**Note that `securitySchemes` inside the `components` block specifies a JWT-based authentication named `BearerAuth`. Then, the `/protected` API requires this authentication method.**

For more information on OpenAPI Specification, check here: https://swagger.io/specification/.

## Generate and Implement the Backend Server
With [Docker](https://openapi-generator.tech/#try), we can use the OpenAPI Generator CLI to generate code stubs for the Python Flask backend server.

Run the following command:
```docker
docker run --rm -v ./:/app/ openapitools/openapi-generator-cli generate \
    -i /app/auth_demo.yaml \
    -g python-flask \
    -o /app/out/
```

The outputs will appear in the local `out/` directory. Now you can implement the API functions  based on this code structure. Basically, write something for the controllers inside `openapi_server/`.

**Note that the `security_controller.py` will contain a function `info_from_BearerAuth` that takes in a JWT, validates it, and returns the decoded payload. This function will auto-execute for all APIs that require `BearerAuth` authentication. The decoded payload will be stored in the context as described in its generated function comment. As a twin function, implement token generation as well.**

## Run and Test the Backend Server
Check the `README.md` file inside the generated `out/` directory. To start a backend server for testing, simply run:

```bash
cd out
python -m openapi_server
```

By default, the server will serve on all network interfaces with port=`8080`. The available endpoints will be output by the server program. Below shows an output example:

```bash
(dncc) root@RAINBOW:/dncc-lab/rpc_rest/1_rest/1_codegen/out# python -m openapi_server
 * Serving Flask app '__main__' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://172.30.236.136:8080
Press CTRL+C to quit
```

In this example, there are 2 endpoints - http://127.0.0.1:8080 and http://172.30.236.136:8080. You can always start with `localhost:8080`.

To test the APIs, you can use `curl`, Postman, or SwaggerUI (http://127.0.0.1:8080/ui). Register the user and login, a JWT will be returned in the login response. Use it to call the `/protected` API:

```bash
# cURL (replace xxx with JWT)
curl http://127.0.0.1:8080/protected \
    -H "Authorization: Bearer xxx"
```

In Postman, select `Bearer Token` in the `Authorization` panel and input the token.

In SwaggerUI, click the lock icon at the top-right position of the `/protected` API and input the token.

Suppose the user name is `Peter`, the output of this method will be:
```json
{
  "message": "Congratulations! Authentication passed! You are Peter."
}
```

If the JWT is not provided or is invalid due to malforming or expiration, the API will return 401 - Unauthorized.
