import urllib
import json

from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs

from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "0.0.0.0"
serverPort = 28080
protocol_version = "https"

generate_embed_user_agents = [
    "facebookexternalhit/1.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/1596241936; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US; Valve Steam Client/default/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; Valve Steam FriendsUI Tenfoot/0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
    "TelegramBot (like TwitterBot)",
    "Mozilla/5.0 (compatible; January/1.0; +https://gitlab.insrt.uk/revolt/january)",
    "Synapse (bot; +https://github.com/matrix-org/synapse)"
]

embed = """
<meta content='text/html; charset=UTF-8' http-equiv='Content-Type' />
<meta content="#ff3333" name="theme-color" />
<meta property="og:site_name" content="vxYouTube">

<meta name="twitter:card" content="player" />
<meta name="twitter:title" content="{{ title }}" />
<meta name="twitter:image" content="{{ thumbnail }}" />
<meta name="twitter:player:width" content="{{ videoWidth }}" />
<meta name="twitter:player:height" content="{{ videoHeight }}" />
<meta name="twitter:player:stream" content="{{ videoURL }}" />
<meta name="twitter:player:stream:content_type" content="video/mp4" />

<meta property="og:url" content="{{ videoLink }}" />
<meta property="og:video" content="{{ videoURL }}" />
<meta property="og:video:secure_url" content="{{ videoURL }}" />
<meta property="og:video:type" content="video/mp4" />
<meta property="og:video:width" content="{{ videoWidth }}" />
<meta property="og:video:height" content="{{ videoHeight }}" />
<meta name="twitter:title" content="{{ title }}" />
<meta property="og:image" content="{{ thumbnail }}" />
<meta property="og:description" content="{{ user }}{{ is_verified }}" />

<link rel="alternate" href="{{ url_start }}/oembed.json?video_title={{ titleEncoded }}&video_url={{ videoURLEncoded }}&channel_name={{ userEncoded }}{{ is_verified }}&channel_id={{ uploader_idEncoded }}" type="application/json+oembed" title="{{ user }}{{ is_verified }}">
"""

known = {}


# noinspection PyBroadException
def extract_url(url):
    parsed_url = urlparse(url)

    data = {}

    try:
        if "/watch" in url:
            data["video_id"] = parse_qs(parsed_url.query)["v"][0]
        elif "/video_url" in url:
            data["video_id"] = parsed_url.path.split("/video_url")[1].replace("/", "").replace("%2F", "")
        else:
            data["video_id"] = parsed_url.path.replace("/", "").replace("%2F", "")
    except:
        data["video_id"] = ""

    try:
        data["timestamp"] = parse_qs(parsed_url.query)["t"][0]
    except:
        data["timestamp"] = ""

    data["video_id"] = data["video_id"].replace("shorts", "").replace("live", "")
    print("[DEBUG]", data["video_id"], "-", data["timestamp"])
    return data


class MyServer(BaseHTTPRequestHandler):
    # noinspection PyBroadException
    def do_GET(self):
        u_parse = urlparse(self.path)
        query = parse_qs(u_parse.query)
        url_start = protocol_version + "://" + self.headers['Host']
        if u_parse.path.replace("/", "").replace("%2F", "") == "":
            self.send_response(302)
            self.send_header("Location", "https://github.com/SomeRandom-Dev/vxyoutube")
            self.end_headers()
            return
        if u_parse.path.replace("/", "").replace("%2F", "") == "oembed.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # <!-- <link rel="alternate" href="{{ url }}/oembed.json?desc={{ urlUser }}&user={{ urlDesc }}&link={{ urlUserLink }}&ttype=video" type="application/json+oembed" title="{{ user }}"> -->
            if not query["channel_id"]: query["channel_id"] = ""
            if not query["video_title"]: query["video_title"] = ""
            if not query["channel_name"]: query["channel_name"] = ""

            self.wfile.write(bytes(json.dumps({
                "author_name": query["channel_name"][0],
                "author_url": "https://youtube.com/" + query["channel_id"][0],
                "provider_name": "vxYouTube",
                "provider_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": query["video_title"][0],
                "type": "video",
                "version": "1.0"
            }), "utf-8"))
            return

        data = extract_url(self.path)
        video_id = data["video_id"]
        timestamp = data["timestamp"]
        found_bot = False

        for agent in generate_embed_user_agents:
            if agent == self.headers["user-agent"]:
                found_bot = True
                break

        if not found_bot and "Discordbot" not in self.headers["user-agent"]:
            self.send_response(307)
            if timestamp != "":
                video_id = video_id + "&t=" + timestamp
            self.send_header("Location", "https://www.youtube.com/watch?v=" + video_id)
            self.end_headers()
        else:
            #if "/video_url" in self.path:
            #    self.send_response(307)
            #    self.send_header("Location", known[video_id]["url"])
            #    self.end_headers()
            if video_id == "" or video_id == "favicon.ico":
                self.send_response(404)
                self.end_headers()
            else:
                options = {"quiet": True, "simulate": True, "forceurl": True, "format": "best"}
                try:
                    info = None

                    try:
                        info = known[video_id]
                    except:
                        with YoutubeDL(options) as ytdlp:
                            info = ytdlp.extract_info("https://www.youtube.com/watch?v=" + video_id, download=False)
                            known[video_id] = info

                    if not info["channel"]: info["channel"] = ""
                    if not info["thumbnail"]: info["thumbnail"] = ""
                    if not info["url"]: info["url"] = ""
                    if not info["title"]: info["title"] = ""
                    if not info["uploader_id"]: info["uploader_id"] = " "

                    # .replace("{{ videoLink }}", "https://www.youtube.com/watch?v=" + video_id)
                    new_response = (embed
                    .replace("{{ user }}", info["channel"])
                    .replace("{{ thumbnail }}", info["thumbnail"])
                    .replace("{{ videoWidth }}", str(info["width"]))
                    .replace("{{ videoHeight }}", str(info["height"]))
                    .replace("{{ videoURL }}", info["url"])
                    .replace("{{ videoURLEncoded }}", urllib.parse.quote(info["url"], safe=''))
                    .replace("{{ videoLink }}", "https://www.youtube.com/watch?v=" + video_id)
                    .replace("{{ title }}", info["title"])
                    .replace("{{ url_start }}", url_start)
                    .replace("{{ uploader_id }}", info["uploader_id"])
                    .replace("{{ titleEncoded }}", urllib.parse.quote(info["title"], safe=''))
                    .replace("{{ userEncoded }}", urllib.parse.quote(info["channel"], safe=''))
                    .replace("{{ uploader_idEncoded }}", urllib.parse.quote(info["uploader_id"], safe=''))
                    )
                    try:
                        if info["channel_is_verified"]:
                            new_response = new_response.replace("{{ is_verified }}", " ☑️")
                        else:
                            new_response = new_response.replace("{{ is_verified }}", "")
                    except:
                        new_response = new_response.replace("{{ is_verified }}", "")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(new_response, "utf-8"))
                except Exception as ex:
                    print(ex)
                    self.send_response(404)
                    self.end_headers()


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
