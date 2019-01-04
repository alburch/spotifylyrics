import codecs
import re
import urllib

import requests
import unidecode  # to remove accents
from bs4 import BeautifulSoup

import lyrics as minilyrics

error = "Error: Could not find lyrics."
proxy = urllib.request.getproxies()


def _minilyrics(song):
    service_name = "Mini Lyrics"
    url = ""
    timed = False
    try:
        data = minilyrics.MiniLyrics(song.artist, song.name)
        for item in data:
            if item['url'].endswith(".lrc"):
                url = item['url']
                break
        lyrics = requests.get(url, proxies=proxy).text
        timed = True
    except Exception:
        lyrics = error
    if url == "":
        lyrics = error
    if song.artist.lower().replace(" ", "") not in lyrics.lower().replace(" ", ""):
        lyrics = error
        timed = False

    return lyrics, url, service_name, timed


def _wikia(song):
    service_name = "Wikia"
    url = ""
    try:
        lyrics = minilyrics.LyricWikia(song.artist, song.name)
        url = "http://lyrics.wikia.com/%s:%s" % (song.artist.replace(' ', '_'), song.name.replace(' ', '_'))
    except Exception:
        lyrics = error
    if "TrebleClef.png" in lyrics:
        lyrics = "(Instrumental)"
    if "Instrumental" in lyrics:
        lyrics = "(Instrumental)"
    if lyrics == "error":
        lyrics = error
    return lyrics, url, service_name


def _musixmatch(song):
    service_name = "Musixmatch"
    url = ""
    try:
        searchurl = "https://www.musixmatch.com/search/%s-%s/tracks" % (
            song.artist.replace(' ', '-'), song.name.replace(' ', '-'))
        header = {"User-Agent": "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)"}
        searchresults = requests.get(searchurl, headers=header, proxies=proxy)
        soup = BeautifulSoup(searchresults.text, 'html.parser')
        page = re.findall('"track_share_url":"([^"]*)', soup.text)
        url = codecs.decode(page[0], 'unicode-escape')
        lyricspage = requests.get(url, headers=header, proxies=proxy)
        soup = BeautifulSoup(lyricspage.text, 'html.parser')
        lyrics = soup.text.split('"body":"')[1].split('","language"')[0]
        lyrics = lyrics.replace("\\n", "\n")
        lyrics = lyrics.replace("\\", "")
        if lyrics.strip() == "":
            lyrics = error
    except Exception:
        lyrics = error
    return lyrics, url, service_name


def _songmeanings(song):
    service_name = "Songmeanings"
    url = ""
    try:
        searchurl = "http://songmeanings.com/m/query/?q=%s %s" % (song.artist, song.name)
        searchresults = requests.get(searchurl, proxies=proxy)
        soup = BeautifulSoup(searchresults.text, 'html.parser')
        url = ""
        for link in soup.find_all('a', href=True):
            if "songmeanings.com/m/songs/view/" in link['href']:
                url = "https:" + link['href']
                break
            elif "/m/songs/view/" in link['href']:
                result = "http://songmeanings.com" + link['href']
                lyricspage = requests.get(result, proxies=proxy)
                soup = BeautifulSoup(lyricspage.text, 'html.parser')
                url = "http://songmeanings.com" + link['href'][2:]
                break
            else:
                pass
        templyrics = soup.find_all("li")[4]
        lyrics = templyrics.getText()
        lyrics = lyrics.split("(r,s)};})();")[1]
    except Exception:
        lyrics = error
    if lyrics == "We are currently missing these lyrics.":
        lyrics = error

    # lyrics = lyrics.encode('cp437', errors='replace').decode('utf-8', errors='replace')
    return lyrics, url, service_name


def _songlyrics(song):
    service_name = "Songlyrics"
    url = ""
    try:
        artistm = song.artist.replace(" ", "-")
        songm = song.name.replace(" ", "-")
        url = "http://www.songlyrics.com/%s/%s-lyrics" % (artistm, songm)
        lyricspage = requests.get(url, proxies=proxy)
        soup = BeautifulSoup(lyricspage.text, 'html.parser')
        lyrics = soup.find(id="songLyricsDiv").get_text()
    except Exception:
        lyrics = error
    if "Sorry, we have no" in lyrics:
        lyrics = error
    if "We do not have" in lyrics:
        lyrics = error
    return lyrics, url, service_name


def _genius(song):
    service_name = "Genius"
    url = ""
    try:
        url = "http://genius.com/%s-%s-lyrics" % (song.artist.replace(' ', '-'), song.name.replace(' ', '-'))
        lyricspage = requests.get(url, proxies=proxy)
        soup = BeautifulSoup(lyricspage.text, 'html.parser')
        lyrics = soup.find("div", {"class": "lyrics"}).get_text()
        if song.artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
            lyrics = error
    except Exception:
        lyrics = error
    return lyrics, url, service_name


def _versuri(song):
    service_name = "Versuri"
    url = ""
    try:
        searchurl = "http://www.versuri.ro/q/%s+%s/" % (song.artist.replace(" ", "+"), song.name.replace(" ", "+"))
        searchresults = requests.get(searchurl, proxies=proxy)
        soup = BeautifulSoup(searchresults.text, 'html.parser')
        for x in soup.findAll('a'):
            if "/versuri/" in x['href']:
                url = "http://www.versuri.ro" + x['href']
                break
            else:
                pass
        if url is "":
            lyrics = error
        else:
            lyricspage = requests.get(url, proxies=proxy)
            soup = BeautifulSoup(lyricspage.text, 'html.parser')
            content = soup.find_all('div', {'id': 'pagecontent'})[0]
            lyrics = str(content)[str(content).find("</script><br/>") + 14:str(content).find("<br/><br/><center>")]
            lyrics = lyrics.replace("<br/>", "")
    except Exception:
        lyrics = error
    return lyrics, url, service_name


# tab/chord services

def _ultimateguitar(song):
    artist = unidecode.unidecode(song.artist)
    title = unidecode.unidecode(song.name)
    url_pt1 = 'https://www.ultimate-guitar.com/search.php?view_state=advanced&band_name='
    url_pt2 = '&song_name='
    url_pt3 = '&type%5B%5D=300&type%5B%5D=200&rating%5B%5D=5&version_la='
    # song = song.replace('-', '+')
    # artist = artist.replace('-', '+')
    url = url_pt1 + artist + url_pt2 + title + url_pt3
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    urls = []
    for a in soup.find_all(class_='song result-link js-search-spelling-link', href=True):
        urls.append(a['href'])

    return urls


def _cifraclub(song):
    artist = unidecode.unidecode(song.artist)
    title = unidecode.unidecode(song.name)
    url = 'https://www.cifraclub.com.br/{}/{}'.format(artist.replace(" ", "-").lower(), title.replace(" ", "-").lower())

    return [url]


# don't even get to this point, but it's an option for source
# just got to change services_list3 list order
def _songsterr(song):
    artist = unidecode.unidecode(song.artist)
    title = unidecode.unidecode(song.name)
    url = 'http://www.songsterr.com/a/wa/bestMatchForQueryString?s={}&a={}'.format(title, artist)
    return [url]


def _tanzmusikonline(song):
    try:
        token_request = requests.get('https://www.tanzmusik-online.de/search')
        search = BeautifulSoup(token_request.content, 'html.parser').find(id="page-wrapper")
        if search:
            token = ""
            for input_field in search.find("form").find_all("input"):
                if input_field.get("name") == "_token":
                    token = input_field.get("value")
                    break
            page = 1
            highest_page = 2
            song_urls = []
            base_result_url = 'https://www.tanzmusik-online.de/search/result'
            while page < highest_page:
                search_results = requests.post(base_result_url + "?page=" + str(page), proxies=proxy,
                                               cookies=token_request.cookies,
                                               data={"artist": song.artist, "song": song.name, "_token": token,
                                                     "searchMode": "extended", "genre": 0, "submit": "Suchen"})
                search_soup = BeautifulSoup(search_results.content, 'html.parser')
                for song_result in search_soup.find_all(class_="song"):
                    song_urls.append(song_result.find(class_="songTitle").a.get("href"))
                if page == 1:
                    pagination = search_soup.find(class_="pagination")
                    if pagination:
                        for page_number in pagination.find_all("a"):
                            t = page_number.getText()
                            if t.isdigit():
                                highest_page = int(t) + 1
                page += 1

            language = requests.get("https://www.tanzmusik-online.de/locale/en", proxies=proxy)
            for song_url in song_urls:
                page = requests.get(song_url, proxies=proxy, cookies=language.cookies)

                soup = BeautifulSoup(page.content, 'html.parser')

                for dance in soup.find(class_="dances").find_all("div"):
                    dance_name = dance.a.getText().strip().replace("Disco Fox", "Discofox")
                    if dance_name not in song.dances:
                        song.dances.append(dance_name)

                details = soup.find(class_="songDetails")
                if details:
                    for detail in details.find_all(class_="line"):
                        classes = detail.i.get("class")
                        typ, text = detail.div.getText().split(":", 1)
                        if "fa-dot-circle-o" in classes:
                            if typ.strip().lower() == "album":
                                song.album = text.strip()
                        elif "fa-calendar-o" in classes:
                            song.year = int(text)
                        elif "fa-flag" in classes:
                            song.genre = text.strip()
                        elif "fa-music" in classes:
                            song.cycles_per_minute = int(text)
                        elif "fa-tachometer" in classes:
                            song.beats_per_minute = int(text)
    except requests.exceptions.ConnectionError as e:
        print(e)


def _welchertanz(song):
    try:
        interpreter_request = requests.get("https://www.welcher-tanz.de/interpreten/", proxies=proxy)
        interpreter_soup = BeautifulSoup(interpreter_request.content, 'html.parser')
        interpreter_links = []
        for interpreter in interpreter_soup.find_all(class_="chip"):
            if song.artist.lower() in interpreter.getText().split("(", 1)[0].strip().lower():
                interpreter_links.append(interpreter.get("href"))
        for interpreter_link in interpreter_links:
            interpreter_songs = requests.get("https://www.welcher-tanz.de" + interpreter_link, proxies=proxy)
            interpreter_songs_soup = BeautifulSoup(interpreter_songs.content, 'html.parser')
            for interpreter_song in interpreter_songs_soup.find(class_="card-content").find_all("tr"):
                infos = interpreter_song.find_all("td")
                if len(infos) > 0 and song.name.lower() in infos[1].getText().strip().lower():
                    dances = infos[2].find_all("a")
                    for dance in dances:
                        dance_name = dance.getText().strip().replace("Cha-Cha-Cha", "Cha Cha Cha")
                        if dance_name != "---" and dance_name not in song.dances:
                            song.dances.append(dance_name)
    except requests.exceptions.ConnectionError as e:
        print(e)
