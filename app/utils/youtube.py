# Rewrite of https://github.com/joetats/youtube_search/blob/master/youtube_search/__init__.py
# Modules
import json
import requests
import urllib.parse

# Main search class
class YoutubeSearch:

    def __init__(self, search_terms: str, max_results = None, page = 1):
        self.search_terms = search_terms
        self.max_results = max_results

        self.page = page
        self.videos = self.search()

    def search(self):

        # Query encoding
        encoded_search = urllib.parse.quote(self.search_terms)

        # Locate our base url
        base = "https://youtube.com"
        url = f"{base}/results?search_query={encoded_search}&page={self.page}"

        # Make request
        response = requests.get(url).text
        while "ytInitialData" not in response:
            response = requests.get(url).text

        # Parse HTML
        results = self.parse_html(response)
        if self.max_results is not None and len(results) > self.max_results:
            return results[: self.max_results]

        return results

    def parse_html(self, response):

        # Initialization
        results = []
        start = (
            response.index("ytInitialData") +
            len("ytInitialData") +
            3
        )

        end = response.index("};", start) + 1
        json_str = response[start:end]

        data = json.loads(json_str)
        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]

        # Loop through videos
        for video in videos:

            res = {}

            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})
                res["id"] = video_data.get("videoId", None)
                res["thumbnails"] = [thumb.get("url", None) for thumb in video_data.get("thumbnail", {}).get("thumbnails", [{}])]
                res["title"] = video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)
                res["long_desc"] = video_data.get("descriptionSnippet", {}).get("runs", [{}])[0].get("text", None)
                res["channel"] = video_data.get("longBylineText", {}).get("runs", [[{}]])[0].get("text", None)
                res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
                res["url_suffix"] = video_data.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", None)

                results.append(res)

        # Return our search results
        return results

    def to_dict(self):
        return self.videos

    def to_json(self):
        return json.dumps({"videos": self.videos})
