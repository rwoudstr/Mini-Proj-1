import time
from os import system, name
import sqlite3
connection = None
cursor = None

####################################################################
## TEXT COLOURS ----------------------------------------------------
class c:
    ''' CHANGE TEXT COLOURS
        - concatenate with text to change colour in the terminal
        - W is default white text '''
    TITLE = '\x1b[6;30;42m'
    GREEN = '\x1b[1;32;40m'
    USER = '\x1b[1;34;40m'
    ARTIST = '\x1b[1;33;40m'
    ERROR = '\x1b[1;31;40m'
    W = '\x1b[0m'

def clean_up():
    ''' clear text from command line '''
    # windows
    if name == 'nt':
        _ = system('cls')
    # mac, linux
    else:
        _ = system('clear')
    return

####################################################################
## LOGIN -----------------------------------------------------------
def login():
    ''' 1st SCREEN OF INTERFACE
        - prompts for login info until successful login
        - option to register new user
        - identifies user vs artist '''
    global connection, cursor
    id_type = None  # indicates if logging in as user or artist
    clean_up()  # clear the screen
    
    # welcome message
    print(c.TITLE+"WELCOME"+c.W)    
    # prompt user for uid/aid
    print(c.GREEN+"NEW users "+c.W+"- Press R")
    uid = input(c.GREEN+"RETURNING users "+
                c.W+"Log in with user ID: ")
    if uid in ["R","r"]:
        register()
        #return None, None
    
    # check that uid/aid exists in db
    cursor.execute("SELECT * FROM users WHERE uid LIKE ?;", (uid,))  # case-insensitive
    user_exists = cursor.fetchone()
    cursor.execute("SELECT * FROM artists WHERE aid LIKE ?;", (uid,))  # case-insensitive
    artist_exists = cursor.fetchone()
    
    if user_exists != None and artist_exists != None:
        # id exists as both user and artist, ask for clarification
        x = 'x'
        while x not in ["U", "u", "A", "a"]:
            x = input("Log In as "+c.USER+"USER (U)"+
                      c.W+" or "+c.ARTIST+"ARTIST (A) "
                      +c.W)
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
    check_id = "SELECT uid FROM users WHERE uid LIKE ?;"  # case-insensitive
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
    add = "INSERT INTO users VALUES (?, ?, ?);"
    cursor.execute(add, (new_id, name, pwd))
    connection.commit()
    clean_up()  # clear the screen
    print("User Successfully Registered!\nUID: "+new_id+"\nNAME: "+name)
    
    # go to user operations menu
    user(new_id)
    
    return

####################################################################
## ARTIST ----------------------------------------------------------
def artist(aid):
    ''' ARTIST OPERATIONS MENU '''
    global connection, cursor
    clean_up()  # clear the screen
    print(c.ARTIST+'---ARTIST MENU---'+c.W)
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
    input("")
    pass

def top_songs():
    pass

####################################################################
## USER ------------------------------------------------------------  
def user(uid):
    ''' USER OPERATIONS MENU '''
    global connection, cursor
    clean_up()  # clear the screen
    print(c.USER+'---USER MENU---'+c.W)
    print('[1]  Start a session\n[2]  Search for songs & playlists')
    print('[3]  Search for artists\n[4]  End current session')
    get_input = input('> ')
    
    while get_input not in ['1', '2', '3', '4']:
        get_input = input("Please choose a valid option (1, 2, 3, 4)")
    if get_input == '1':
        start_sess(uid)
    elif get_input == '2':
        search_songs()
    elif get_input == '3':
        search_artists()
    else:
        end_sess(uid)    
    return

def start_sess(uid):
    ''' START A NEW SESSION
        - checks that there is not already a session in progress
        - assign sno
        - set start date to current date, end to null '''
    global connection, cursor
    # check that there is not a session in progress
    check_sess = '''SELECT * FROM sessions WHERE uid = ? AND
                    end IS NULL;'''
    sessions = cursor.execute(check_sess, (uid,))
    exists = cursor.fetchone()
    if exists!= None:
        print(c.ERROR+"Uh Oh! "+c.W+
              "You already have a session in progress\n"+ 
              "Returning to "+c.USER+"USER MENU..."+c.W)
        time.sleep(3)  # wait for 3 seconds
        user(uid)
        return
    # get session numbers already used by user
    snos = "SELECT sno FROM sessions WHERE uid LIKE ?;" # case insensitive
    cursor.execute(snos, (uid,))
    get_sno = cursor.fetchall()
    all_sno = [0]  # list of session numbers currently in use
    for i in get_sno:
        all_sno.append(i[0])
    new_sno = max(all_sno)+1  # new unique session number
    # set session start date to current date, end to null
    new_sess = "INSERT INTO sessions VALUES (?, ?, CURRENT_DATE, NULL);"
    # add session to database
    cursor.execute(new_sess, (uid,new_sno))
    connection.commit()
    # confirmation message
    print("Successfully added session "+str(new_sno))
    action = "a"
    while action not in ["M", "m", "L", "l"]:
        action = input("Return to "+c.USER+"USER MENU (M)"+
                       c.W+" or "+c.GREEN+"LOGOUT (L) "+
                       c.W)
    if action in ["M", "m"]:
        user(uid)
    else:
        logout()
    return

def search_songs():
    pass
def search_artists():
    pass
def end_sess(uid):
    ''' END CURRENT SESSION '''
    return

####################################################################
## END PROGRAM -----------------------------------------------------
def logout():
    pass

def exit_program():
    pass

####################################################################
## MAIN ------------------------------------------------------------    
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