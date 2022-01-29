import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from loguru import logger


class Spotify:
    def __init__(self) -> None:
        self.client: spotipy.Spotify = None

    def authenticate_oauth(self) -> bool:
        """
        Authenticate to Spotify
        :return: None
        """
        self.client = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
        logger.info("Successfully authenticated!")
        return True

    def get_playlist_tracks_by_uri(self, uri: str) -> list:
        """
        Get playlist by uri
        :param uri: playlist uri
        :return: playlist
        """
        playlist_id = uri.split("/")[-1]
        if "?" in playlist_id:
            playlist_id = playlist_id.split("?")[0]

        tracks = []
        results = self.client.playlist_items(playlist_id=playlist_id)
        while results["next"]:
            for item in results["items"]:
                tracks.append(item["track"])
            results = self.client.next(results)

        # We do an extra for loop to get the last tracks
        for item in results["items"]:
            tracks.append(item["track"])
        return tracks

    def get_playlist_name_by_uri(self, uri: str) -> str:
        """
        Get playlist name by uri
        :param uri: playlist uri
        :return: playlist name
        """
        playlist_id = uri.split("/")[-1]
        if "?" in playlist_id:
            playlist_id = playlist_id.split("?")[0]

        result = self.client.playlist(playlist_id=playlist_id)
        return result["name"]

    def get_artist_image_by_id(self, artist_id: str) -> str:
        """
        Get artist image by id
        :param uri: artist id
        :return: artist image as url
        """
        result = self.client.artist(artist_id=artist_id)
        return result["images"][0]["url"]
