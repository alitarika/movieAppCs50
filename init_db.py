import sqlite3

def create_tables():
    conn = sqlite3.connect('movieApp.db')
    cursor = conn.cursor()
    
    # Create the 'users' table # DEFAULT ''
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            bucket TEXT DEFAULT ''
        )
    ''')

    # Create the 'users_interaction' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_interaction (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            movie_id INTEGER,
            users_rating INTEGER,
            comment TEXT,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY,
            sender_id INTEGER,
            recipient_id INTEGER,
            status TEXT,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (recipient_id) REFERENCES users (id)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            user_id INTEGER,
            friend_id INTEGER,
            PRIMARY KEY (user_id, friend_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        );

    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()