# Flask REST API for Student Management System

This is a Flask REST API for managing students, courses and grades in a student management system. The API provides endpoints for creating, updating, and retrieving students, as well as creating, updating, and retrieving courses and grades.

## Installation

1. Clone the repository:
   `git clone https://github.com/<username>/<repository>.git`

2. Install the dependencies:
   `pip install -r requirements.txt`

3. Initialize the database:
   `flask db init`
   `flask db migrate`
   `flask db upgrade`
4. Run the Application:
   `flask run`

## Endpoints

The API provides the following endpoints:

### Authentication

`POST /auth/signup`

This route should only be accessible to Admin users for registration.

Parameters

| Name       | Type   | Description                        |
| ---------- | ------ | ---------------------------------- |
| `username` | string | The user's username                |
| `email`    | string | The user's email                   |
| `password` | string | The user's password                |
| `role`     | enum   | The user's role (ADMIN or STUDENT) |

`GET /auth/login`
Logs any user in and returns an access token.

Parameters
| Name | Type | Description |
| `username` | string | The user's username. |
| `password` | string | The user's password. |

Response
| Name | Type | Description |
| `access_token`| string | An access token that can be used to authenticate future requests to protected endpoints.
| `refresh_token` | string | A refresh token |

### Users

`GET /users/users`

Retrieves a list of all users.

Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |

Response

| Name       | Type   | Description                        |
| ---------- | ------ | ---------------------------------- |
| `username` | string | The user's username                |
| `email`    | string | The user's email                   |
| `role`     | enum   | The user's role (ADMIN or STUDENT) |

Cheers!
