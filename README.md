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
| ---------- | ------ | ---------------------------------- |
| `username` | string | The user's username. |
| `password` | string | The user's password. |

Response
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
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

`POST /users/users`

Allows an Admin user to create other users

Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |
| `username` | string | The user's username |
| `email` | string | The user's email |
| `password` | string | The user's password |
| `role` | enum | The user's role (ADMIN or STUDENT) |

Response
json, 201
{
"message": "User created successfully",
"id": user.id,
}

`GET /users/user/<int:user_id>`,

`POST /users/user/<int:user_id>`,

`GET /users/user/<int:user_id>`,

`DELETE /users/user/<int:user_id>`,

These routes allow operations on a specific user by the admin.

Parameters for `POST`, AND `PUT`. `GET` and `DELETE` only require Authorization.

| Name          | Type   | Description                        |
| ------------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role        |
| `username`    | string | The user's username                |
| `email`       | string | The user's email                   |
| `password`    | string | The user's password                |
| `role`        | enum   | The user's role (ADMIN or STUDENT) |

### STUDENT

`GET /users/students`

Retrieves a list of all students.

Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |

Response

| Name              | Type   | Description                                             |
| ----------------- | ------ | ------------------------------------------------------- |
| `name`            | string | The Students full name                                  |
| `enrollment_date` | string | The student's enrollment date                           |
| `user`            | object | The Student's user info as contained on the users table |
| `gpa`             | float  | The student's gpa                                       |

`POST /user/students`

Allows an Admin user to create students. Authorization is required

Parameters

| Name              | Type   | Description                                             |
| ----------------- | ------ | ------------------------------------------------------- |
| `name`            | string | The Students full name                                  |
| `enrollment_date` | string | The student's enrollment date                           |
| `user`            | object | The Student's user info as contained on the users table |
| `gpa`             | float  | The student's gpa                                       |

Response:
{"message": "Student created Successfully"}, 201

`DELETE /user/students`
Allows an Admin user to delete all students

`GET /users/students/student/<int:student_id>`

`PUT /users/students/student/<int:student_id>`

`DELETE /users/students/student/<int:student_id>`

The endpoints above allow operations on a specific student by the admin.
The authenticated student is only allowed access to the `GET` route.
Authorization is required.

Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |

### STUDENT GRADES

`GET /users/students/student/<int:student_id>/grades`

Retrieves all grades for a specific student.
Authorization is required, and both ADMIN and the authenticated STUDENT are allowed access.

### COURSES

`GET /courses/courses` - Retrieves a list of all courses

`POST /courses/courses` - Creates a Course.

Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |
| `name` | string | The Name of the Course |
| `teacher` | string | The Name of the Instructor |
| `credit_hours` | Integer | The number of credit hours |
| `course_code` | string | The course code |

`GET /courses//course/<int:course_id>`

`PUT /courses//course/<int:course_id>`

`DELETE /courses//course/<int:course_id>`

Allow operations on a specific course.
Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |
| `name` | string | The Name of the Course |
| `teacher` | string | The Name of the Instructor |
| `credit_hours` | Integer | The number of credit hours |
| `course_code` | string | The course code |

#### GradesByCourse

`GET  /courses/grades/<int:course_id>/`

`POST  /courses/grades/<int:course_id>/`

`PUT  /courses/grades/<int:course_id>/`

`DELETE  /courses/grades/<int:course_id>/`

Allows retrieving, adding, updating and deleting grades for individual courses.
Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |

#### GradesByStudent

`GET /courses/grades/student/<int:student_id>`
Retrieves all grades belonging to a particular student. Only the authenticated student or and ADMIN can access this route.

### ENROLLMENT

`GET /enrollment/enroll`

Retrieves a list of all students and the courses they are enrolled in.
Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |

`POST /enrollment/enroll`

Enroll a student in a Course.
Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'ADMIN' role |
| `student_id` | Integer | The Student ID |
| `Course_id` | Integer | The Course ID |

`GET /enrollment/enrollment/<int:enrollment_id>`

`PUT /enrollment/enrollment/<int:enrollment_id>`

`DELETE /enrollment/enrollment/<int:enrollment_id>`
Allows an ADMIN user to retrieve and modify the details of a specific course enrollment.

#### COURSE REGISTRATION BY STUDENT

`POST /enrollment/students/<int:student_id>/enroll`

Allows students to register for courses themselves.
Parameters
| Name | Type | Description |
| ---------- | ------ | ---------------------------------- |
| Authorization | Header | JWT Token with 'STUDENT' role |
| `student_id` | Integer | The Student ID |
| `Course_id` | Integer | The Course ID |

Cheers!
