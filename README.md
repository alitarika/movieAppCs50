# MovieApp, a movie inspection website where you can rate movies and see your friends' ratings

#### Video Demo: https://youtu.be/waOJ3GsgK8Q

## An SQL and Flask based final project for CS50x written in mostly python

### Technical Information

The website takes the movie information from [TMDB](https://www.themoviedb.org/) and [OMDB](https://omdbapi.com/) databases and collects user information in movieApp.db.

The technologies used are:

- HTML with jinja templates
- Plain CSS
- Plain Javascript (minimally)
- Flask
- SQLite
- Python

###### SQL Table Structure

movieApp.db

1. Table: users

   - id (INTEGER, PRIMARY KEY)
   - username (TEXT, NOT NULL)
   - password_hash (TEXT, NOT NULL)
   - bucket (TEXT, DEFAULT '')

2. Table: users_interaction

   - id (INTEGER, PRIMARY KEY)
   - user_id (INTEGER)
   - movie_id (INTEGER)
   - users_rating (INTEGER)
   - comment (TEXT)
   - timestamp (DATETIME)
   - FOREIGN KEY (user_id) REFERENCES users (id)

3. Table: friend_requests

   - id (INTEGER, PRIMARY KEY)
   - sender_id (INTEGER)
   - recipient_id (INTEGER)
   - status (TEXT)
   - FOREIGN KEY (sender_id) REFERENCES users (id)
   - FOREIGN KEY (recipient_id) REFERENCES users (id)

4. Table: friendships
   - user_id (INTEGER)
   - friend_id (INTEGER)
   - PRIMARY KEY (user_id, friend_id)
   - FOREIGN KEY (user_id) REFERENCES users (id)
   - FOREIGN KEY (friend_id) REFERENCES users (id)

### Motivation and Usage

When deciding on which movie to watch with a friend, it does save time to know what your friend liked to watch, whether or not that person actually watched a particular movie in your mind, what ratings and nominations the movie received, who was the director, who has written the scenario, who played in the movie etc. etc.

The website is created so that the people can have the information mentioned above with few clicks. A person registers with a username and a password hence becoming a user. The person searchs for friends with their usernames and sends them friend requests. In the case the friend request is accepted they become friends and able to see each other's comments, ratings, friends and buckets.

When someone comments and posts a rating on a movie. Only the friends of that person can see that someone's ratings and comments on their feeds (by pressing the movieapp logo), on that someone's user profile and the movie's page.

Bucket is designed for which movies a person wants to watch in the future and can be seen by everyone under the user profile of that person. A person can compare his/her movies that are in the bucket from the compare link on the navigation bar. To compare movies one must at least two movies added to bucket. Movies can be added to bucket by clicking the add button in the movie's page.

Movies can be searched from both the quick search input field on the navigation bar and search movie link on the navigation bar. Alternatively, any movie poster and title in the page is a link to the particular movie except for the compare route in which the poster and title is used for choosing the movie to compare.

On the movie's page, one sees the ratings on, poster and title of the movie etc. and directors, writers and actors with their character's names. By clicking on the name or photograph of the person, one will be directed to the person's page where movies they have been a part of and their bio alongside with their popularity is shown. Rating and commenting on an actor, writer, director is not a feature of the site. One cannot do that since the act exceed the scope of the motive of the website.

On a side note, when you hit enter on the quick search after typing your search query, it will not work. It is designed for quick search. It is a feature.
# movieAppCs50
