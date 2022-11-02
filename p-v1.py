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
    I_GREEN = '\x1b[3;32;40m'  # italic green
    USER = '\x1b[1;34;40m'  # blue
    ARTIST = '\x1b[1;33;40m'  # yellow
    ERROR = '\x1b[1;31;40m'  # red
    W = '\x1b[0m'  # default text
    I_W = '\x1b[3;37;40m'  # italic white

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
    uid = None
    clean_up()  # clear the screen
    
    # welcome message
    print(c.TITLE+"WELCOME"+c.W)    
    # prompt user for uid/aid
    print(c.GREEN+"NEW users "+c.W+"- Press R to register")
    uid = input(c.GREEN+"RETURNING users "+
                c.W+"Log in with user ID: ")
    # register new user
    if uid in ["R","r"]:
        new_uid = register()
        id_type = "U"
        return new_uid, id_type
    
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
        print(c.ERROR+"Uh Oh! "+c.W+"User ID does not exist - ", end='')
        #failed_login()
        return None, None
    
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
        print(c.ERROR+"Uh Oh! "+c.W+"Incorrect Password - ", end='')
        #failed_login()
        #return None, None
        uid = None
        id_type = None
    
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
    #else:
        #login()

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
        new_id = input("Create a user ID: ")[0:4]  # uid is 4 characters max
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
    print(c.USER+"USER successfully registered!"+c.W
          +c.I_GREEN+"\nUID: "+c.W+new_id
          +c.I_GREEN+"\nNAME: "+c.W+name)
    x = input("Press [ENTER] to continue")
    if x or not x:    
        return new_id

####################################################################
## ARTIST ----------------------------------------------------------
def artist(aid):
    ''' ARTIST OPERATIONS MENU '''
    
    clean_up()  # clear the screen
    print(c.ARTIST+'---ARTIST MENU---'+c.W)
    print('[1]  Add a song\n[2]  Find top fans & playlists')
    get_input = input('> ')
    while get_input not in ['1', '2']:
        get_input = input("Please choose a valid option (1 or 2)")
    if get_input == '1':
        add_song(aid)
    else:
        top_songs()
    return

def a_options(aid):
    '''allow artist to logout or return to artist menu'''
    action = "a"
    while action not in ["M", "m", "L", "l"]:
        action = input("Return to "+c.ARTIST+"ARTIST MENU (M)"+
                       c.W+" or "+c.GREEN+"LOGOUT (L) "+ c.W)
    if action in ["M", "m"]:
        artist(aid)
    else:
        logout(aid, None) 

def add_song(aid):
    ''' ARTIST ADDS A SONG
        - get title and duration from user
        - get additional artists from user
        - if song doesn't exist, adds to db with unique song id
        - updates perform table '''
    
    global connection, cursor
    # get title and duration from artist
    artists = list(map(str, input("Enter additional artists: ").split()))
    artists.append(aid)
    title = input("Enter song title: ")
    try:
        dur = int(input("Enter song duration: "))
    except:
        print(c.ERROR+"ERROR! "+c.W+"please enter a numerical value")
        try:
            dur = int(input("Enter song duration: "))
        except:
            print(c.ERROR+"ERROR! "+c.W+"not a valid duration")
            a_options(aid)
            return
    # check if song exists
    get_song = '''SELECT * FROM songs
                  WHERE title LIKE ?
                  AND duration = ?'''
    cursor.execute(get_song, (title, dur))
    exists = cursor.fetchone()  
    if exists!= None:  # song already exists in db
        print(c.ERROR+"Uh Oh! "+c.W+"This song already exists")
        a_options(aid)
        return   
    # get song ids already in use
    cursor.execute("SELECT sid FROM songs;")
    get_sid = cursor.fetchall()
    all_sid = [0]  # list of song ids currently in use
    for i in get_sid:
        all_sid.append(i[0])
    new_sid = max(all_sid)+1  # new unique song id    
    # if there are additional artists, check that they exist
    if len(artists) > 1:
        cursor.execute("SELECT aid FROM artists;")
        get_aid = cursor.fetchall()
        for i in artists:
            if (i,) not in get_aid:
                print(c.ERROR+"ERROR! "+c.W+
                      "one or more artists do not exist")
                a_options(aid)
                return
    # add song to database
    add_song = "INSERT INTO songs VALUES (?, ?, ?);"
    cursor.execute(add_song, (new_sid, title, dur))    
    # add aid and sid to perform table
    for i in artists:
        cursor.execute("INSERT INTO perform VALUES (?, ?);", (i, new_sid))
    connection.commit()
    # confirmation message
    print("Song '"+title+"' successfully added")
    a_options(aid)
    return

def top_songs():
    pass

####################################################################
## USER ------------------------------------------------------------  
def user(uid, id_type):
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
        start_sess(uid, id_type)
    elif get_input == '2':
        search_songs(uid, id_type)
    elif get_input == '3':
        search_artists(uid, id_type)
    else:
        end_sess(uid, id_type)    
    return

def u_options(uid, id_type):
    '''allow user to logout or return to user menu'''
    action = "a"
    while action not in ["M", "m", "L", "l"]:
        action = input("Return to "+c.USER+"USER MENU (M)"+
                       c.W+" or "+c.GREEN+"LOGOUT (L) "+ c.W)
    if action in ["M", "m"]:
        user(uid, id_type)
    else:
        logout(uid, id_type)  
    
def start_sess(uid, id_type):
    ''' START SESSION FOR A USER
        - checks that there is not already a session in progress
        - set start date to current date/time, end to null '''
    
    global connection, cursor
    # check that there is not a session in progress
    check_sess = '''SELECT * FROM sessions WHERE uid LIKE ? AND
                    end IS NULL;'''
    sessions = cursor.execute(check_sess, (uid,))
    exists = cursor.fetchone()
    if exists!= None:  # session exists
        print(c.ERROR+"Uh Oh! "+c.W+
              "You already have a session in progress\n"+ 
              "Returning to "+c.USER+"USER MENU..."+c.W)
        time.sleep(3)  # wait for 3 seconds
        user(uid, id_type)
    else:  # create session
        new_sno = create_sess(uid)
        # confirmation message
        print("Successfully added session ", new_sno)
        u_options(uid, id_type)
    return

def listen_song(sid, uid, id_type):
    ''' ADD SONG TO CURRENT SESSION
        - checks for current session
        - if no session: creates a session
        - adds song to session or increments count (listen table)'''
    
    global connection, cursor
    # check if there is an ongoing session
    check_sess = '''SELECT sno FROM sessions
                    WHERE uid LIKE ? 
                    AND end IS NULL;'''
    sessions = cursor.execute(check_sess, (uid,))
    sess_exists = cursor.fetchone()
    if sess_exists != None:  # current session exists
        sno = sess_exists[0]
        # check if song is listened to in this session
        check_lis = '''SELECT cnt FROM listen 
                       WHERE uid LIKE ?
                       AND sno = ? AND sid = ?; '''
        cursor.execute(check_lis, (uid, sno, sid))
        lis_exists = cursor.fetchone()
        if lis_exists != None:  # song is already in session
            # increment listen count
            cnt = lis_exists[0]+1
            # update listen table
            incr = '''UPDATE listen SET cnt = ?
                      WHERE uid LIKE ?
                      AND sno = ? AND sid = ?;'''
            cursor.execute(incr, (cnt, uid, sno, sid))
        else:  # song is not in session, add new row
            add_lis = "INSERT INTO listen VALUES (?, ?, ?, 1);"
            cursor.execute(add_lis, (uid, sno, sid))            
    else:  # current session does not exist
        sno = create_sess(uid)  # create a new session
        # add new row to listen table
        cursor.execute(add_lis, (uid, sno, sid))    
    connection.commit()
    print("Song added to 'listen'")
    u_options(uid, id_type)
    return 

def search_songs():
    pass
def search_artists():
    pass

def end_sess(uid, id_type):
    ''' END CURRENT SESSION 
        - checks that there is an active session
        - sets end to current date/time '''
  
    # check that there is not a session in progress
    exists = check_sess(uid)    
    if exists==False:
        print(c.ERROR+"Uh Oh! "+c.W+
              "You have 0 sessions in progress\n"+ 
              "Returning to "+c.USER+"USER MENU..."+c.W)
        time.sleep(3)  # wait for 3 seconds
        user(uid, id_type)
        return
    # set end to current date/time
    update_sess(uid)
    # confirmation message
    print("Successfully ended session")
    u_options(uid, id_type)
    return   

def song_info(sid, uid, id_type):
    ''' DISPLAY INFO ABOUT SONG
        - name(s) of artist(s)
        - title
        - duration
        - playlists song is in 
        *** available to both users and artists ***'''
    
    global connection, cursor
    # get title and duration
    cursor.execute("SELECT * FROM songs WHERE sid LIKE ?;", (sid,))
    info = cursor.fetchone()
    print(f"{c.I_GREEN+'TITLE: '+c.W: >24}", end='')
    print(info[1])  # display title
    print(f"{c.I_GREEN+'DURATION: '+c.W: >24}", end='')
    print(info[2])  # display title
    # get all artists
    
    # get playlists
    
    connection.commit()
    u_options(uid, id_type)
    return     

## SESSION FUNCTIONS ##
def create_sess(uid):
    ''' CREATE A SESSION '''
    global connection, cursor
    # get session numbers already used by user
    snos = "SELECT sno FROM sessions WHERE uid LIKE ?;" # case insensitive
    cursor.execute(snos, (uid,))
    get_sno = cursor.fetchall()
    all_sno = [0]  # list of session numbers currently in use
    for i in get_sno:
        all_sno.append(i[0])
    new_sno = max(all_sno)+1  # new unique session number
    # set session start date to current date, end to null
    new_sess = "INSERT INTO sessions VALUES (?, ?, datetime(), NULL);"
    # add session to database
    cursor.execute(new_sess, (uid,new_sno))
    connection.commit()  
    return new_sno

def check_sess(uid):
    ''' checks if user has a session 
        - returns True if session in progress
        - returns False if no session in progress'''
    global connection, cursor
    # check that there is not a session in progress
    check_sess = '''SELECT * FROM sessions 
                    WHERE uid LIKE ? 
                    AND end IS NULL;'''
    sessions = cursor.execute(check_sess, (uid,))
    exists = cursor.fetchone()
    connection.commit()
    return (exists != None)

def update_sess(uid):
    ''' sets end time of current sessions to current date/time '''
    global connection, cursor
    update = '''UPDATE sessions SET end = datetime() 
                WHERE uid LIKE ? 
                AND end IS NULL;'''
    cursor.execute(update, (uid,))
    connection.commit()    
    return 

####################################################################
## END PROGRAM -----------------------------------------------------
def logout(uid, id_type):
    ''' LOGOUT 
        - close any active sessions
        - return to login screen '''

    clean_up()  # clear the screen
    # if user, close any active sessions
    if id_type == "U":
        exists = check_sess(uid)    
        if exists==True:  
            update_sess(uid) 
            print(c.I_W+"closing sessions...")
    # print log out message
    print("logging out..."+c.W)
    time.sleep(2)
    # return to main menu
    program()
    return

def exit_program(uid, id_type):
    ''' EXIT PROGRAM '''
    # if user, close any active sessions
    if id_type == "U":
        exists = check_sess(uid)    
        if exists==True:  
            update_sess(uid)     
    print('bye bye :)')
    pass

####################################################################
## MAIN ------------------------------------------------------------    
def connect():
    ''' CONNECT TO DATABASE '''
    
    global connection, cursor
    clean_up()  # clear screen
    # get database name from user
    db = input('Please enter your database name ("file.db"): ' )
    # connect to database
    connection = sqlite3.connect('./'+db)
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    connection.commit()  
    
def program():
    # login/register, get type of user (artist or user)
    uid = None
    while uid == None:
        uid, id_type = login()
        if uid == None: 
            failed_login()
    if id_type == "A":
        artist(uid)  # open artist operations menu
    else:
        user(uid, id_type)  # open user operations menu    

def main():
    ''' MAIN FUNCTION 
        - connect to database
        - run the program
        - close database connection '''   
    
    global connection, cursor
    # connect to database   
    connect()
    # run program 
    program()  
    # close database connection
    connection.commit()
    connection.close()
    return 

main()
