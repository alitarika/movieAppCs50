import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, session
from flask_session import Session
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "shadow"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("movieApp.db")
    return db

def add_user(name, password, confirmation):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    if name == "":
        return f"Username cannot be empty."
    
    if password == "":
        return f"Password cannot be empty."
    
    if password != confirmation:
        return f"Passwords should match."

    # Check if the username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (name,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Username already exists, return an error or raise an exception
        conn.close()
        return f"{name} username is taken. Please take another username."
    else:
        hash = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash, bucket) VALUES (?, ?, ?)", (name, hash, ''))
        rows = cursor.execute("SELECT id FROM users WHERE username = ?", (name,)).fetchone()
        session["user_id"] = rows[0]
    
    conn.commit()
    conn.close()


def login_user(username, password):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Check if a user with the given username exists
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user[1], password):
        # Password is correct
        session["user_id"] = user[0]  # Set the user's ID in the session
        conn.close()
        return None
    else:
        conn.close()
        return "Invalid username or password"
    
def change_password(user_id, current_password, new_password, confirm_password):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Check if the user with the given user_id exists
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    current_password_hash = cursor.fetchone()

    if not current_password_hash:
        conn.close()
        return "User not found"

    # Check if the provided current password matches the stored password hash
    if not check_password_hash(current_password_hash[0], current_password):
        conn.close()
        return "Current password is incorrect"

    # Check if the new password and confirmation match
    if new_password != confirm_password:
        conn.close()
        return "New password and confirmation should match."

    # Update the password to the new hashed password
    new_password_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    conn.commit()
    conn.close()
    return None  # Password changed successfully

def add_to_bucket(user_id, movie_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Get the current bucket for the user
    cursor.execute("SELECT bucket FROM users WHERE id = ?", (user_id,))
    current_bucket = cursor.fetchone()[0]

    # If the bucket is empty, simply add the movie_id
    if not current_bucket:
        updated_bucket = str(movie_id)
    else:
        # If the bucket is not empty, append the new movie_id with a comma
        updated_bucket = f"{current_bucket},{movie_id}"

    # Update the user's bucket in the database
    cursor.execute("UPDATE users SET bucket = ? WHERE id = ?", (updated_bucket, user_id))
    conn.commit()
    conn.close()

    return updated_bucket

def get_movie_list_from_bucket(user_id):
        conn = sqlite3.connect('movieApp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT bucket FROM users WHERE id = ?", (int(user_id),))
        bucket_data = cursor.fetchone()[0]
        conn.close()

        if bucket_data:
            # Parse the bucket data into a list of movie IDs
            movie_ids =  bucket_data.split(',')
            return movie_ids
        
        return []

def delete_movie_from_bucket(user_id, movie_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Get the current bucket for the user
    cursor.execute("SELECT bucket FROM users WHERE id = ?", (user_id,))
    current_bucket = cursor.fetchone()[0]

    if current_bucket:
        # Split the current bucket data into a list of movie IDs
        movie_ids = current_bucket.split(',')

        # Check if the movie_id exists in the user's bucket
        if str(movie_id) in movie_ids:
            # Remove the movie_id from the list
            movie_ids.remove(str(movie_id))

            # Join the updated movie IDs back into a comma-separated string
            updated_bucket = ','.join(movie_ids)

            # Update the user's bucket in the database
            cursor.execute("UPDATE users SET bucket = ? WHERE id = ?", (updated_bucket, user_id))
            conn.commit()
        else:
            # Movie ID not found in the bucket, no changes needed
            conn.close()
    else:
        # Bucket is empty, no changes needed
        conn.close()


def empty_bucket(user_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Set the user's bucket to an empty string
    cursor.execute("UPDATE users SET bucket = ? WHERE id = ?", ('', user_id))

    conn.commit()
    conn.close()


def get_user_data_by_username(username):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Retrieve user's bucket and user_id
    cursor.execute("SELECT id, bucket FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    
    if user_data:
        user_id, bucket = user_data
    else:
        conn.close()
        return None  # User not found

    # Retrieve user's interactions
    cursor.execute("""
        SELECT ui.movie_id, ui.users_rating, ui.comment, ui.timestamp
        FROM users_interaction ui
        JOIN users u ON u.id = ui.user_id
        WHERE u.username = ?
    """, (username,))
    interactions = cursor.fetchall()

    # Count the number of friends
    cursor.execute("""
        SELECT COUNT(*) FROM friendships
        WHERE user_id = (SELECT id FROM users WHERE username = ?)
    """, (username,))
    friend_count = cursor.fetchone()[0]

    conn.close()

    # Create a dictionary to hold the retrieved data
    user_data = {
        'user_id': user_id,
        'bucket': bucket if bucket else '',  # Extract the bucket value
        'interactions': interactions,  # List of interactions
        'friend_count': friend_count  # Number of friends
    }

    return user_data


def get_username_by_user_id(user_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Retrieve the username based on the user's ID
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()

    conn.close()

    if username:
        return username[0]
    else:
        return None  # User not found
    

def get_user_id_from_username(username):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Retrieve the username based on the user's ID
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    username = cursor.fetchone()

    conn.close()

    if username:
        return username[0]
    else:
        return None  # User not found
    
def get_pending_friend_request_id(sender_id, recipient_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Retrieve the ID of a pending friend request, if it exists
    cursor.execute("""
        SELECT id
        FROM friend_requests
        WHERE sender_id = ? AND recipient_id = ? AND status = 'pending'
    """, (sender_id, recipient_id))
    
    request_id = cursor.fetchone()

    conn.close()

    return request_id[0] if request_id else None



def send_friend_request(sender_id, recipient_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Check if a friend request already exists between sender and recipient
    cursor.execute("""
        SELECT id FROM friend_requests
        WHERE sender_id = ? AND recipient_id = ? AND status = 'pending'
    """, (sender_id, recipient_id))
    existing_request = cursor.fetchone()


    if not existing_request:
        # If no pending request exists, insert a new friend request
        cursor.execute("""
            INSERT INTO friend_requests (sender_id, recipient_id, status)
            VALUES (?, ?, 'pending')
        """, (sender_id, recipient_id))
        conn.commit()
    else:
        conn.close()
        return "You have already sent friend request"

    conn.close()

def get_friend_requests(user_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Retrieve friend requests for the user
    cursor.execute("""
        SELECT friend_requests.id, users.username AS sender_username
        FROM friend_requests
        JOIN users ON friend_requests.sender_id = users.id
        WHERE friend_requests.recipient_id = ? AND friend_requests.status = 'pending'
    """, (user_id,))
    
    friend_requests = [{"sender_id": row[0], "sender_username": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return friend_requests


def get_friends(user_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Retrieve the user's friends
    cursor.execute("""
        SELECT users.id, users.username
        FROM friendships
        JOIN users ON friendships.friend_id = users.id
        WHERE friendships.user_id = ?
    """, (user_id,))
    
    friends = [{"friend_id": row[0], "friend_username": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return friends

def already_friends(user_id, friend_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Check if a friendship exists between user_id and friend_id
    cursor.execute("""
        SELECT user_id, friend_id FROM friendships
        WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)
    """, (user_id, friend_id, friend_id, user_id))
    existing_friendship = cursor.fetchone()

    conn.close()

    return existing_friendship is not None

def accept_friend_request(sender_id, recipient_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Delete the friend request
    cursor.execute("DELETE FROM friend_requests WHERE sender_id = ? AND recipient_id = ? AND status = 'pending'", (sender_id, recipient_id))

    # Add friendships to the 'friendships' table
    cursor.execute("INSERT INTO friendships (user_id, friend_id) VALUES (?, ?), (?, ?)", (recipient_id, sender_id, sender_id, recipient_id))

    conn.commit()
    conn.close()

def unfriend(user_id, friend_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    cursor.execute("DELETE FROM friendships WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)", (user_id, friend_id, friend_id, user_id))

    conn.commit()
    conn.close()

def decline_friend_request(sender_id, recipient_id):
    conn = sqlite3.connect('movieApp.db')  # Replace with your database connection
    cursor = conn.cursor()

    # Delete the friend request
    cursor.execute("DELETE FROM friend_requests WHERE sender_id = ? AND recipient_id = ? AND status = 'pending'", (sender_id, recipient_id))

    conn.commit()
    conn.close()

def add_users_interaction(user_id, movie_id, users_rating, comment):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    users_rating = int(users_rating)

    # Insert the user's interaction into the 'users_interaction' table
    cursor.execute("INSERT INTO users_interaction (user_id, movie_id, users_rating, comment, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (user_id, movie_id, users_rating, comment, timestamp))
    
    conn.commit()
    conn.close()

import sqlite3

def get_interaction_of_self_and_friends(user_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Retrieve interactions of the current user and their friends
    cursor.execute("""
        SELECT users_interaction.id AS users_interaction_id, users.id AS user_id, users.username, users_interaction.movie_id, users_interaction.users_rating, users_interaction.comment, users_interaction.timestamp
        FROM users
        LEFT JOIN users_interaction ON users.id = users_interaction.user_id
        WHERE users.id = ?
        UNION
        SELECT users_interaction.id AS users_interaction_id, users.id AS user_id, users.username, users_interaction.movie_id, users_interaction.users_rating, users_interaction.comment, users_interaction.timestamp
        FROM users
        LEFT JOIN users_interaction ON users.id = users_interaction.user_id
        WHERE users.id IN (
            SELECT friend_id FROM friendships WHERE user_id = ? 
            UNION
            SELECT user_id FROM friendships WHERE friend_id = ?
        )
        ORDER BY timestamp DESC
    """, (user_id, user_id, user_id))

    interactions = cursor.fetchall()
    conn.close()

    # Transform the result into a list of dictionaries
    interaction_list = []
    for row in interactions:
        interaction_dict = {
            'users_interaction_id': row[0],  # Include users_interaction.id
            'user_id': row[1],
            'username': row[2],
            'movie_id': row[3],
            'users_rating': row[4],
            'comment': row[5],
            'timestamp': row[6]
        }
        interaction_list.append(interaction_dict)

    return interaction_list

def get_interaction_of_self(user_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Retrieve interactions of the current user
    cursor.execute("""
        SELECT users_interaction.id AS users_interaction_id, users.id AS user_id, users.username, users_interaction.movie_id, users_interaction.users_rating, users_interaction.comment, users_interaction.timestamp
        FROM users
        LEFT JOIN users_interaction ON users.id = users_interaction.user_id
        WHERE users.id = ?
        ORDER BY timestamp DESC
    """, (user_id,))

    interactions = cursor.fetchall()
    conn.close()

    # Transform the result into a list of dictionaries
    interaction_list = []
    for row in interactions:
        interaction_dict = {
            'users_interaction_id': row[0],  # Include users_interaction.id
            'user_id': row[1],
            'username': row[2],
            'movie_id': row[3],
            'users_rating': row[4],
            'comment': row[5],
            'timestamp': row[6]
        }
        interaction_list.append(interaction_dict)

    return interaction_list



def get_interaction_of_self_and_friends_of_movie(user_id, movie_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Retrieve interactions for the current user and their friends for the specified movie_id
    cursor.execute("""
        SELECT users_interaction.id, users.id, users.username, users_interaction.movie_id, users_interaction.users_rating, users_interaction.comment, users_interaction.timestamp
        FROM users_interaction
        JOIN users ON users_interaction.user_id = users.id
        WHERE users.id = ? AND users_interaction.movie_id = ?
        UNION
        SELECT users_interaction.id, users.id, users.username, users_interaction.movie_id, users_interaction.users_rating, users_interaction.comment, users_interaction.timestamp
        FROM users_interaction
        JOIN users ON users_interaction.user_id = users.id
        JOIN friendships ON (users.id = friendships.user_id OR users.id = friendships.friend_id)
        WHERE (friendships.user_id = ? OR friendships.friend_id = ?) AND users_interaction.movie_id = ?
        ORDER BY timestamp DESC
    """, (user_id, movie_id, user_id, user_id, movie_id))

    interaction_data = cursor.fetchall()
    conn.close()

    interactions = []

    for row in interaction_data:
        interaction = {
            'users_interaction_id': row[0],  # Include users_interaction.id
            'user_id': row[1],
            'username': row[2],
            'movie_id': row[3],
            'users_rating': row[4],
            'comment': row[5],
            'timestamp': row[6]
        }
        interactions.append(interaction)

    return interactions

def delete_interaction(users_interaction_id):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Delete the interaction with the given users_interaction_id
    cursor.execute("DELETE FROM users_interaction WHERE id = ?", (users_interaction_id,))

    conn.commit()
    conn.close()



def search_friend(query):
    conn = sqlite3.connect("movieApp.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username LIKE ?", ('%' + query + '%',))
    users_list = [{"user_id": row[0], "username": row[1]} for row in cursor.fetchall()]
    conn.close()


    return users_list


def get_user_stats(username):
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()

    # Get the user's ID using the provided username
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    
    if not user_id:
        return None  # User not found

    user_id = user_id[0]

    # Count the number of friends for the user
    cursor.execute("""
        SELECT COUNT(*) FROM friendships
        WHERE user_id = ?
    """, (user_id,))
    friend_count = cursor.fetchone()[0]

    # Count the number of interactions for the user
    cursor.execute("SELECT COUNT(*) FROM users_interaction WHERE user_id = ?", (user_id,))
    interaction_count = cursor.fetchone()[0]

    # Get the last interaction (movie_id and users_rating) for the user
    cursor.execute("""
        SELECT movie_id, users_rating
        FROM users_interaction
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (user_id,))
    last_interaction = cursor.fetchone()

    conn.close()

    if last_interaction:
        movie_id, users_rating = last_interaction
    else:
        movie_id, users_rating = None, None

    return {
        'friend_count': friend_count,
        'interaction_count': interaction_count,
        'last_interaction_movie_id': movie_id,
        'last_interaction_users_rating': users_rating
    }




@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
