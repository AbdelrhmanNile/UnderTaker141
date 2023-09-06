# UnderTaker141

This project is for educational purposes only, do not use it against any law or to harm anyone, I will not be responsible for any misuse of this project.

<img src="https://i.imgur.com/mGkRVa2.jpg">

<h1 align="center">UnderTaker141 (very creative name)</h1>

UnderTaker is a free and opensource game-center and qbittorrent client for Linux, UnderTaker141 fetches all the repacks uploaded by [johncena141](https://1337x.to/user/johncena141/) on 1337x, then fetch their summary and cover art from [IGDB](igdb.com) and displayes them in a "nice" UI :3.

just download the game and run it! everything is pre-configuired for you thank's to  johncena141 repacks! <br />


# IMPORTANT

please read [johncena141's documents](https://github.com/jc141x/jc141-bash/tree/master/setup) to understand more about how their repacks work, and double check the dependencies for their repacks

# Improvements over steaL
- Better UI
    - uses kivymd instead of plain kivy
- Better code (I think)
    - not the cleanest code but structured better than steaL
- uses qbittorent webui api
    - better contorl over downloads
- local database for games
    - sqlite database with 2 tables, one for games (to be displayed on ui) and one as an archive for games cover art and summary (no need to        re-fetch them all over again from igdb every time) when you update the database
- packaged as an AppImage

# Dependencies
- appimage launcher
- latest qbitorent with webui enabled
- all the dependencies for johncena141's repacks (check their [documents](https://github.com/jc141x/jc141-bash/blob/master/setup/en/readme.md)

# Installation
- download the latest release from [here](https://github.com/AbdelrhmanNile/UnderTaker141/releases)
- run the appimage and enjoy!

# Configuration
after you run the appimage head to the settings tab.

## qbittorent
- enter your qbittorent webui host (default is localhost)
- enter your qbittorent webui port (default is 8080)
- enter your qbittorent webui username (default is admin)
- enter your qbittorent webui password (default is adminadmin)

## Igdb
- create a twitch api app and get a client id and from [here](https://dev.twitch.tv/console/apps/create)

# Updating the database
to update the database and fetch new releases by jc141 head to the settings tab and click on the "update database" button, this will take a few minutes and will freeze the app, just wait until it finishes.

# TODO
- [X] better design for the Library tab
- [ ] add a search bar to the Library tab
- [ ] fix deleting games from the library

