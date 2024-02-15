# Movie Database API

## Overview

This Movie Database API is a FastAPI application designed to manage a comprehensive collection of movie-related information, including movies, actors, directors, users, and reviews. It provides a RESTful interface for CRUD operations on each entity within the database.

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn (for running the server)
- SQLAlchemy (for ORM support)

### Setup

1. Clone the repository:

 `git clone https://github.com/yourgithubusername/moviedbapi.git`
cd moviedbapi

2. Install the required packages:

`pip install -r requirements.txt`

3. Running the Application
To run the application, use the following command:

`uvicorn app.main:app --reload`

This will start the FastAPI application on <http://localhost:8000>.

## API Endpoints

### Movies

- GET /movies: Retrieve all movies.
- POST /movies: Create a new movie (Admin only).
- GET /movies/{movie_id}: Retrieve a movie by ID.
- PUT /movies/{movie_id}: Update a movie by ID (Admin only).
- DELETE /movies/{movie_id}: Delete a movie by ID (Admin only).

### Actors

- GET /actors: Retrieve all actors.
- POST /actors: Add a new actor (Admin only).
- GET /actors/{actor_id}: Retrieve an actor by ID.
- PUT /actors/{actor_id}: Update an actor's information (Admin only).
- DELETE /actors/{actor_id}: Remove an actor from the database (Admin only).

### Directors

- GET /directors: Retrieve all directors.
- POST /directors: Add a new director (Admin only).
- GET /directors/{director_id}: Retrieve a director by ID.
- PUT /directors/{director_id}: Update a director's information (Admin only).
- DELETE /directors/{director_id}: Remove a director from the database (Admin only).

### Reviews

- GET /reviews: Retrieve all reviews.
- POST /reviews: Create a new review.
- GET /reviews/{review_id}: Retrieve a review by ID.
- PUT /reviews/{review_id}: Update a review (Review author or Admin only).
- DELETE /reviews/{review_id}: Delete a review (Review author or Admin only).

### Users

- GET /users: Retrieve all users (Admin only).
- POST /users: Register a new user.
- GET /users/{user_id}: Retrieve a user by ID.
- PUT /users/{user_id}: Update user information (User or Admin only).
- DELETE /users/{user_id}: Delete a user (Admin only).

### Authentication

This API uses OAuth2 with JWT tokens for securing endpoints that require user authentication and authorization.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

MIT
