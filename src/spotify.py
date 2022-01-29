from loguru import logger
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Spotify:
    def __init__(self) -> None:
        self.client: spotipy.Spotify = None

    def authenticate_oauth(self, scopes: str) -> bool:
        """
        Authenticate to Spotify
        :param scopes: comma separated string of scopes
        :type scopes: str
        :return: None
        """
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))
        logger.info("Successfully authenticated!")
        return True

    def get_playlist_tracks_by_uri(self, uri: str) -> list:
        """
        Get playlist by uri
        :param uri: playlist uri
        :type uri: str
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
        :type uri: str
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

    def update_playlist_cover_image(self, uri: str, image) -> None:
        """
        Update the cover image of a playlist
        :param uri: playlist uri
        :type uri: str
        :param image: image to replace
        """
        playlist_id = uri.split("/")[-1]
        if "?" in playlist_id:
            playlist_id = playlist_id.split("?")[0]

        self.client.playlist_upload_cover_image(playlist_id=playlist_id, image_b64=image)
