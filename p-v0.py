from os import system, name
import sqlite3
connection = None
cursor = None

def clean_up():
    ''' clear text from command line '''
    # windows
    if name == 'nt':
        _ = system('cls')
    # mac, linux
    else:
        _ = system('clear')
    return

def login():
    ''' 1st SCREEN OF INTERFACE
        - prompts for login info until successful login
        - option to register new user
        - identifies user vs artist '''
    global connection, cursor
    id_type = None  # indicates if logging in as user or artist
    clean_up()  # clear the screen
    
    # welcome message
    print("\x1b[6;30;42m"+"WELCOME"+"\x1b[0m")    
    # prompt user for uid/aid
    print("\x1b[1;32;40m"+"NEW users "+"\x1b[0m"+"- Press R")
    uid = input("\x1b[1;32;40m"+"RETURNING users "+
                "\x1b[0m"+"Log in with user ID: ")
    if uid in ["R","r"]:
        register()
        #return None, None
    
    # check that uid/aid exists in db
    cursor.execute('''SELECT * FROM users WHERE uid LIKE ?;''', (uid,))  # case-insensitive
    user_exists = cursor.fetchone()
    cursor.execute('''SELECT * FROM artists WHERE aid LIKE ?;''', (uid,))  # case-insensitive
    artist_exists = cursor.fetchone()
    
    if user_exists != None and artist_exists != None:
        # id exists as both user and artist, ask for clarification
        x = 'x'
        while x not in ["U", "u", "A", "a"]:
            x = input("Log In as "+"\x1b[1;34;40m"+"USER (U)"+
                      "\x1b[0m"+" or "+"\x1b[1;33;40m"+"ARTIST (A) "
                      +"\x1b[0m")
        if x in ["U","u"]:
            id_type = 'U'  # tag as user
        else:
            id_type = "A"  # tag as artist
    elif user_exists != None:
        # flag as user
        id_type = "U"
    elif artist_exists != None:
        # flag as artist
        id_type = "A"
    else:
        # uid/aid doesn't exist
        print("User ID does not exist - ", end='')
        failed_login()
        #return None, None
    
    # if id exists, prompt user for pwd
    pwd = input("Password: ")
    if id_type == "A":
        table = 'artists'
        field = 'aid'
    else:
        table = 'users'
        field = 'uid'
    check_pwd = 'SELECT * FROM '+table+' WHERE '+field+' LIKE ? AND pwd = ?;'
    cursor.execute(check_pwd, (uid,pwd))  # injection attacks???
    exists = cursor.fetchone()
    # check for match
    if exists == None:
        print("Incorrect Password - ", end='')
        failed_login()
        #return None, None
    
    # else, return uid/aid and artist/user flag
    return uid, id_type
    
def failed_login():
    ''' FAILED LOGIN ATTEMPT
        prompts user to login again or register '''
    
    print("Login Failed")
    # prompt user to choose login or register
    x = 0
    while x not in ["T", "t", "R", "r"]:
        x = input("Try again (T) or register as new user (R)? ")
    if x in ["R","r"]:
        register()    
    else:
        login()

def register():
    global connection, cursor
    ''' REGISTER NEW USER 
        - prompt for unique uid, name, password
        - add to database 
        - proceed to user operations menu '''
    
    # check that uid is not already in use
    check_id = '''SELECT uid FROM users WHERE uid LIKE ?;'''  # case-insensitive
    in_use = 1
    while in_use != None:
        # prompt for uid
        new_id = input("Create a user ID: ")[0:3]  # uid is 4 characters max
        cursor.execute(check_id, (new_id,))
        in_use = cursor.fetchone()
    # prompt for name
    name = input("Enter your name: ")
    # prompt for password
    pwd = input("Create a password: ")
    
    # add info to database
    add = '''INSERT INTO users VALUES (?, ?, ?);'''
    cursor.execute(add, (new_id, name, pwd))
    connection.commit()
    clean_up()  # clear the screen
    print("User Successfully Registered!\nUID: "+new_id+"\nNAME: "+name)
    
    # go to user operations menu
    user(new_id)
    return
        
def artist(aid):
    ''' ARTIST OPERATIONS MENU '''
    global connection, cursor
    clean_up()  # clear the screen
    print('\x1b[1;33;40m'+'---ARTIST MENU---'+'\x1b[0m')
    print('[1]  Add a song\n[2]  Find top fans & playlists')
    get_input = input('> ')
    while get_input not in ['1', '2']:
        get_input = input("Please choose a valid option (1 or 2)")
    if get_input == '1':
        add_song()
    else:
        top_songs()
    return

def add_song():
    pass
def top_songs():
    pass

def user(uid):
    ''' USER OPERATIONS MENU '''
    global connection, cursor
    clean_up()  # clear the screen
    print('\x1b[1;34;40m'+'---USER MENU---'+'\x1b[0m')
    print('[1]  Start a session\n[2]  Search for songs & playlists')
    print('[3]  Search for artists\n[4]  End current session')
    get_input = input('> ')
    
    while get_input not in ['1', '2', '3', '4']:
        get_input = input("Please choose a valid option (1, 2, 3, 4)")
    if get_input == '1':
        start_sess()
    elif get_input == '2':
        search_songs()
    elif get_input == '3':
        search_artists()
    else:
        end_sess()    
    return

def start_sess():
    pass
def search_songs():
    pass
def search_artists():
    pass
def end_sess():
    pass
    
def main():
    ''' MAIN FUNCTION 
        - connect to database
        - run the program
        - close database connection '''   
    
    global connection, cursor
    
    # get database name from user
    db = input('Please enter your database name ("file.db"): ' )
    # connect to database
    connection = sqlite3.connect('./'+db)
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    connection.commit()    
    
    # login/register, get type of user (artist or user)
    uid, id_type = login()
    if uid == None:
        return
    if id_type == "A":
        artist(uid)  # open artist operations menu
    else:
        user(uid)  # open user operations menu
        
    # close database connection
    connection.commit()
    connection.close()
    return 

#### RUN THE PROGRAM ####
main()