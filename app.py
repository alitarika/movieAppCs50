from flask import Flask, render_template, g, redirect, url_for, request, jsonify, session, flash
from tmdb_api import fetch_movie_by_id, fetch_actor_by_id, fetch_movie_by_query, fetch_director_by_id, fetch_writer_by_id, fetch_person_details, fetch_person_movie_credits, fetch_poster_and_title_by_id
from omdb_api import omdb_by_imdb_id
from db_utils import add_user, login_user, change_password, add_to_bucket, get_movie_list_from_bucket, empty_bucket, get_user_data_by_username, get_username_by_user_id, send_friend_request, get_friend_requests, get_friends, get_user_id_from_username, get_pending_friend_request_id, accept_friend_request, decline_friend_request, already_friends, delete_movie_from_bucket, add_users_interaction, get_interaction_of_self_and_friends, get_interaction_of_self_and_friends_of_movie, get_interaction_of_self, search_friend, get_user_stats, delete_interaction, unfriend
from functools import wraps

app = Flask(__name__)
app.secret_key = "shadow"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

    
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("search_movie")) # CHANGE IT TO DEFAULT INDEX. 

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        error_message = add_user(username, password, confirmation)

        if error_message:
            flash(error_message)
            return render_template("register.html")
        else:
            return redirect(url_for("search_movie"))
        
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        error_message = login_user(username, password)

        if error_message:
            flash(error_message)
            return render_template("login.html")
        else:
            flash(f"Welcome {username}!")
            return redirect(url_for("home_route"))

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password_route():
    if request.method == "GET":
        return render_template("change_password.html")
    elif request.method == "POST":
        user_id = session["user_id"]
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        error_message = change_password(user_id, current_password, new_password, confirm_password)

        if error_message:
            flash(error_message)
            return render_template("change_password.html")
        else:
            flash("Password changed successfully.")
            return redirect(url_for("profile_route"))
        

@app.route("/add_to_bucket/<movie_id>", methods=["POST"])
@login_required
def add_to_bucket_route(movie_id):
    if request.method == "POST":
        user_id = session["user_id"]

        if user_id:
            add_to_bucket(user_id, movie_id)
            flash(f"Movie has been added to your bucket.")

        # Redirect back to the movie page or another suitable route
        return redirect(url_for("show_movie_route", movie_id=movie_id))
    
@app.route("/delete_interaction/<users_interaction_id>/<movie_id>", methods=["POST"])
@login_required
def delete_interaction_route(users_interaction_id, movie_id):
    delete_interaction(users_interaction_id)
    flash(f"Your comment and rating have been deleted.")

    # Redirect back to the movie page or another suitable route
    return redirect(url_for("show_movie_route", movie_id=movie_id))

    
@app.route("/bucket")
@login_required
def show_bucket():
    user_id = session["user_id"]
    movie_list = get_movie_list_from_bucket(user_id)
    movies_data_collection = []
    for movie_id in movie_list:
        movie_data = fetch_movie_by_id(movie_id)
        if movie_data:
            movies_data_collection.append(movie_data)
    return render_template("bucket.html", collection=movies_data_collection)

@app.route("/compare")
@login_required
def compare_route():
    user_id = session["user_id"]
    movie_list = get_movie_list_from_bucket(user_id)
    movies_data_collection = []
    for movie_id in movie_list:
        movie_data = fetch_movie_by_id(movie_id)
        if movie_data:
            movies_data_collection.append(movie_data)
    bucket_length = len(movies_data_collection)
    if bucket_length < 2:
        flash("You should have at least 2 movies in your bucket to compare movies.")
        return redirect(url_for("show_bucket"))
    return render_template("compare.html", collection=movies_data_collection)

@app.route("/compare/<movie_id1>")
@login_required
def compare_choose_second_movie_route(movie_id1):
    user_id = session["user_id"]
    movie_list = get_movie_list_from_bucket(user_id)
    movies_data_collection = []
    for movie_id in movie_list:
        movie_data = fetch_movie_by_id(movie_id)
        if movie_data:
            if movie_id != movie_id1:
                movies_data_collection.append(movie_data)
    return render_template("compare_choose_second_film.html", movie_id1=movie_id1, collection=movies_data_collection)

@app.route("/compare/<movie_id1>/<movie_id2>")
@login_required
def comparison_route(movie_id1, movie_id2):
    movie_data1 = fetch_movie_by_id(movie_id1)
    imdb_id1 = movie_data1["imdb_id"]
    omdb_data1 = omdb_by_imdb_id(imdb_id1)
    movie_data2 = fetch_movie_by_id(movie_id2)
    imdb_id2 = movie_data2["imdb_id"]
    omdb_data2 = omdb_by_imdb_id(imdb_id2)
    return render_template("comparison.html", movie_data1=movie_data1, movie_data2=movie_data2, omdb_data1=omdb_data1, omdb_data2=omdb_data2)

@app.route("/empty_bucket", methods=["POST"])
@login_required
def empty_bucket_route():
        user_id = session["user_id"]
        empty_bucket(user_id)
        flash("You have cleared your bucket.")
        return redirect(url_for("show_bucket"))
    
@app.route("/delete_from_bucket/<movie_id>", methods=["POST"])
@login_required
def delete_from_bucket_route(movie_id):
    user_id = session["user_id"]
    delete_movie_from_bucket(user_id, movie_id)
    return redirect(url_for("show_bucket"))
    
    

@app.route("/send_friend_request/<recipient_id>", methods=["POST"])
@login_required
def send_friend_request_route(recipient_id):
    if request.method == "POST":
        recipient_username = get_username_by_user_id(recipient_id)
        sender_id = session["user_id"]

        if already_friends(sender_id, recipient_id):
            flash(f"You are already friends with {recipient_username}")
            return redirect(url_for("user", username=recipient_username))

        if int(sender_id) != int(recipient_id):
            error_message = send_friend_request(sender_id, recipient_id)
            if error_message:
                flash(error_message)
                return redirect(url_for("user", username=recipient_username))
            else:
                flash("Friend request sent!")
                return redirect(url_for("user", username=recipient_username))
        else:
            flash("You can't send a friend request to yourself.")

        return redirect(url_for("user", username=recipient_username))
    
@app.route("/delete_friend/<friend_id>", methods=["POST"])
@login_required
def delete_friend_route(friend_id):
    if request.method == "POST":
        unfriended_username = get_username_by_user_id(friend_id)
        user_id = session["user_id"]
        unfriend(user_id, friend_id)
        flash(f"You have deleted {unfriended_username} from friends")
        return redirect(url_for("user", username=unfriended_username))
    
@app.route("/friends")
@login_required
def show_friends_route():
    user_id = session["user_id"]
    friend_requests = get_friend_requests(user_id)
    friends = get_friends(user_id)
    for friend in friends:
        user_stats = get_user_stats(friend["friend_username"])
        friend["friend_count"] = user_stats["friend_count"]
        friend["interaction_count"] = user_stats["interaction_count"]
        friend["last_interaction_movie_id"] = user_stats["last_interaction_movie_id"]
        friend["last_interaction_users_rating"] = user_stats["last_interaction_users_rating"]
    
    for friend in friends:
        if friend["last_interaction_movie_id"]:
            movie_poster_title = fetch_poster_and_title_by_id(friend["last_interaction_movie_id"])
            friend["last_interaction_poster_path"] = movie_poster_title["poster_path"]
            friend["last_interaction_movie_title"] = movie_poster_title["title"]
    return render_template("friends.html", friend_requests=friend_requests, friends=friends)


@app.route("/accept/<username>", methods=["POST"])
@login_required
def accept_friend_request_route(username):
    user_id = session["user_id"]
    sender_id = get_user_id_from_username(username)

    if sender_id:
        request_id = get_pending_friend_request_id(sender_id, user_id)
        if request_id:
            accept_friend_request(sender_id, user_id)
            flash(f"Friend request from {username} has been accepted.")
        else:
            flash(f"No pending friend request from {username}.")
            return redirect(url_for("show_friends_route"))
    else:
        flash(f"{username} is not a valid username.")
        return redirect(url_for("show_friends_route"))
    
    return redirect(url_for("show_friends_route"))

@app.route("/decline/<username>", methods=["POST"])
@login_required
def decline_friend_request_route(username):
    user_id = session["user_id"]
    sender_id = get_user_id_from_username(username)

    if sender_id:
        request_id = get_pending_friend_request_id(sender_id, user_id)
        if request_id:
            decline_friend_request(sender_id, user_id)
            flash(f"Friend request from {username} has been declined.")
        else:
            flash(f"No pending friend request from {username}.")
            return redirect(url_for("show_friends_route"))
    else:
        flash(f"{username} is not a valid username.")
        return redirect(url_for("show_friends_route"))
    
    return redirect(url_for("show_friends_route"))


@app.route('/search_movie', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST':
        # Get the user input from the form
        user_query = request.form['movie_title']
        
        # Call a function to fetch movie data based on the user query
        movie_data = fetch_movie_by_query(user_query)
 
        return render_template('show_movie.html', movie_data=movie_data, user_query=user_query)

    return render_template('search_movie.html')

@app.route("/layout")
def layout():
    return render_template("layout.html")

@app.route("/movie/<movie_id>", methods=['GET', 'POST'])
def show_movie_route(movie_id):
    if request.method == "GET":
        movie_data = fetch_movie_by_id(movie_id)
        if not movie_data:
            flash(f"There is no movie with the {movie_id} movie id.")
            return redirect(url_for("search_movie"))

        imdb_id = movie_data["imdb_id"]
        omdb_data = omdb_by_imdb_id(imdb_id)
        actors_data = fetch_actor_by_id(movie_id)
        directors = fetch_director_by_id(movie_id)
        writers = fetch_writer_by_id(movie_id)
        user_id = session.get("user_id")
        if user_id:
            interactions = get_interaction_of_self_and_friends_of_movie(user_id, movie_id)
            username = get_username_by_user_id(user_id)
        else:
            interactions = []
            username = None
        
        if interactions:
            for interaction in interactions:
                interaction["comment"] = interaction["comment"].split("\n")

        return render_template("movie.html", username=username, data=movie_data, omdb=omdb_data, interactions=interactions, actors=actors_data, writers=writers, directors=directors, movie_id=movie_id)
    elif request.method == "POST":
        user_id = session["user_id"]
        users_rating = request.form.get("users_rating")
        comment = request.form.get("comment")
        add_users_interaction(user_id, movie_id, users_rating, comment)
        flash("Your rating and comment have been processed.")
        return redirect(url_for("show_movie_route", movie_id=movie_id))
        
@app.route("/interactions/<movie_id>")
@login_required
def interactions_route(movie_id):
    user_id = session["user_id"]
    ints = get_interaction_of_self_and_friends_of_movie(user_id, movie_id)
    return ints


@app.route("/person/<person_id>")
def person(person_id):
    person_details = fetch_person_details(person_id)
    if not person_details:
        flash(f"There is no person with the {person_id} person id.")
        return redirect(url_for("search_movie"))

    if person_details is not None:
        biography_block = person_details.get("biography", "").split("\n")
    else:
        biography_block = []

    person_credits = fetch_person_movie_credits(person_id)

    return render_template("person.html", person_details=person_details, person_credits=person_credits, biography_block=biography_block)

@app.route("/user/<username>")
@login_required
def user(username):
    user_id = session["user_id"]
    user_data = get_user_data_by_username(username)
    if user_data:
        isSelf = user_id == user_data["user_id"]
        isFriends = already_friends(user_id, user_data["user_id"])
        movie_list = get_movie_list_from_bucket(user_data["user_id"])
        bucket_data_collection = []
        for movie_id in movie_list:
            movie_data = fetch_movie_by_id(movie_id)
            if movie_data:
                bucket_data_collection.append(movie_data)
        
        interaction_dicts = get_interaction_of_self(user_data["user_id"])
        interaction_data_collection = []
        if interaction_dicts[0]["comment"]:
            for interaction in interaction_dicts:
                    interaction["comment"] = interaction["comment"].split("\n")
                    movie_id = interaction["movie_id"]
                    # Fetch poster_path and title for the movie
                    movie_data = fetch_poster_and_title_by_id(movie_id)
                    if movie_data:
                        interaction["poster_path"] = movie_data["poster_path"]
                        interaction["title"] = movie_data["title"]
                    interaction_data_collection.append(interaction)

        return render_template("user.html", user_data=user_data, bucket_collection=bucket_data_collection, interaction_collection=interaction_data_collection, username=username, isFriends=isFriends, isSelf=isSelf)
    else:
        flash(f"No user is found with the username {username}. You can search for users here.")
        return redirect(url_for("search_friend_route"))
    
@app.route("/user/<username>/friends")
@login_required
def users_friends_route(username):
    user_id = get_user_id_from_username(username)
    friends = get_friends(user_id)
    for friend in friends:
        user_stats = get_user_stats(friend["friend_username"])
        friend["friend_count"] = user_stats["friend_count"]
        friend["interaction_count"] = user_stats["interaction_count"]
        friend["last_interaction_movie_id"] = user_stats["last_interaction_movie_id"]
        friend["last_interaction_users_rating"] = user_stats["last_interaction_users_rating"]
    
    for friend in friends:
        if friend["last_interaction_movie_id"]:
            movie_poster_title = fetch_poster_and_title_by_id(friend["last_interaction_movie_id"])
            friend["last_interaction_poster_path"] = movie_poster_title["poster_path"]
            friend["last_interaction_movie_title"] = movie_poster_title["title"]

    return render_template("show_users_friends.html", friends=friends, username=username)

@app.route("/")
@app.route("/home")
@login_required
def home_route():
    user_id = session["user_id"]
    interaction_dicts = get_interaction_of_self_and_friends(user_id)
    interaction_data_collection = []
    for interaction in interaction_dicts:
            movie_id = interaction["movie_id"]
            # Fetch poster_path and title for the movie
            movie_data = fetch_poster_and_title_by_id(movie_id)
            if interaction["comment"]:
                interaction["comment"] = interaction["comment"].split("\n")
            if movie_data:
                interaction["poster_path"] = movie_data["poster_path"]
                interaction["title"] = movie_data["title"]
            interaction_data_collection.append(interaction)
    return render_template("home.html", collection=interaction_data_collection)
    


@app.route("/profile")
@login_required
def profile_route():
    if "user_id" in session:
        # Get the current user's username based on session["user_id"]
        username = get_username_by_user_id(session["user_id"])  # Implement this function

        if username:
            # Redirect to the user's profile using their username
            return redirect(url_for("user", username=username))
    
    # Handle cases where the user is not authenticated or the username is not found
    return "User not found."

@app.route("/search_friend", methods=["GET", "POST"])
@login_required
def search_friend_route():
    if request.method == "POST":
        query = request.form.get("friend_query")
        users_list_data = search_friend(query)
        for user in users_list_data:
            user_stats = get_user_stats(user["username"])
            user["friend_count"] = user_stats["friend_count"]
            user["interaction_count"] = user_stats["interaction_count"]
            user["last_interaction_movie_id"] = user_stats["last_interaction_movie_id"]
            user["last_interaction_users_rating"] = user_stats["last_interaction_users_rating"]
        
        for user in users_list_data:
            if user["last_interaction_movie_id"]:
                movie_poster_title = fetch_poster_and_title_by_id(user["last_interaction_movie_id"])
                user["last_interaction_poster_path"] = movie_poster_title["poster_path"]
                user["last_interaction_movie_title"] = movie_poster_title["title"]

        return render_template("show_friend.html", users_list_data=users_list_data)
    elif request.method == "GET":
        return render_template("search_friend.html")


if __name__ == '__main__':
    app.run(debug=True)