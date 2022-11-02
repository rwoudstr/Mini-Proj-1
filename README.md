# Mini-Proj-1
291 Mini Project 1
>  using python3
> due Thurs Nov 3, 5pm

---LOGIN---
+ ~~Users and artists can login~~
+ ~~Both user and artist? Ask for clarification~~
+ ~~Artist? Go to artist menu~~
+ ~~User? Go to user menu~~
+ ~~Register with unique uid, name, password (not encrypted)~~
    + ~~Go to user menu~~
- Logout → first login screen
- Directly exit program
    - Automatically close session

---USER FUNCTIONALITIES---
+ ~~Start a session~~
    - ~~Program assigns session number unique to user~~
    - ~~Session start date = current date/time~~
    - ~~Session end = null~~
+ Search for songs, playlists using >= 1 keyword(s)
    - Retrieve all songs, playlists with keywords in title
        - SONG: return id, title, duration 
        - PLAYLIST: id, title, total duration of songs
    - Indicate if row is song or playlist
    - Order by greatest number matching keywords (desc)
    - Show 5 matches at once
        - User can select one row
        - User can see more pages of results (paginated downward)
    - User can select a song
+ Search for artists using >= 1 keyword(s)
    - Retrieve artists with keywords in name or song title
    - Display name, nationality, number of songs of matching artists
    - Order by greatest number matching keywords (desc)
    - Show 5 matches at once
        - User can select one row
        - User can see more pages of results (paginated downward)
    - User can select artist to see id, title, duration of ALL artist's songs
        - Can select a song
+ ~~End the session~~
    - ~~Set session end to current date/time~~

---SONG ACTIONS---
+ Listen to song
    - Add listen to current session (increment listen count or add new row)
    - OR start a new session
- See more info about song
     - Name(s) of performing artist(s), id, title, duration, playlists song is in
- Add song to existing or new playlist
     - If new playlist: system creates unique playlist id, get uid and title from input

---ARTIST ACTIONS---
+ ~~Add song~~
     + ~~System creates unique id (if same title & duration doesn't already exist)~~
     - ~~Get additional artist ids from input~~
     - ~~update perform table~~
+ Find top fans and playlists
     + Lists top 3 users who listen to songs for the longest time
     - Lists top 3 playlists with largest # of artist's songs
