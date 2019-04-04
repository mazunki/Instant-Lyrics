import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk

import signal
import threading

from src.windows import LyricsWindow, PreferenceWindow
from . import utils
from src.settings import APPINDICATOR_ID, CONFIG_PATH


class AppIndicator():

    def __init__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        indicator = appindicator.Indicator.new(APPINDICATOR_ID, utils.get_icon_path(
            '../icons/instant-lyrics-24.png'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.build_menu())

        self.alive = True
        self.listener = threading.Thread(target=self.socket_listener)
        self.listener.start()

        self.Config = utils.get_config()
        Gtk.main()

    def socket_listener(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        sock.bind(("localhost", 55555))
        sock.listen(1)
        # sock.setblocking(0)

        try:
            while self.alive:
                print("a")
                try:
                    print("b")
                    connection, src_address = sock.accept()
                    print("c")

                    if self.alive:
                        self.spotify_lyrics(None) # Triggers a Fatal IO error
                except Exception as e:    
                    connection.close()
                    print(e)
                finally:
                    try:
                        connection.close()
                    except:
                        pass
        except:
            pass
        sock.close()

    def build_menu(self):
        menu = Gtk.Menu()

        get_lyrics = Gtk.MenuItem('Get Lyrics')
        get_lyrics.connect('activate', self.fetch_lyrics)

        global spotify_lyrics

        spotify_lyrics = Gtk.MenuItem('Spotify Lyrics')
        spotify_lyrics.connect('activate', self.spotify_lyrics)
        print(spotify_lyrics)

        preferences = Gtk.MenuItem('Preferences')
        preferences.connect('activate', self.preferences)

        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)

        menu.append(get_lyrics)
        menu.append(spotify_lyrics)
        menu.append(preferences)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def fetch_lyrics(self, source):
        win = LyricsWindow("get", self)

    def spotify_lyrics(self, source):
        print(source)
        win = LyricsWindow("spotify", self)
        thread = threading.Thread(target=win.get_spotify)
        thread.daemon = True
        thread.start()

    def preferences(self, source):
        win = PreferenceWindow(self)

    def quit(self, source):
        self.alive = False

        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 55555))  # closes sock.accept()

        Gtk.main_quit()