import base64
from collections import Counter
from io import BytesIO
import os
import time
from spotify import Spotify
from dotenv import load_dotenv
from loguru import logger
from PIL import Image
import requests

load_dotenv()


SPOTIFY_PLAYLISTS_URIS = [
    "https://open.spotify.com/playlist/0JP3smzah2mTnxIZIVjVX0?si=e33aaca9d1334dc6"
]
ARTIST_IMAGE_SIZE = 640
scopes = "user-library-read playlist-modify-public playlist-modify-private playlist-read-private ugc-image-upload"


def main():
    sp = Spotify()
    sp.authenticate_oauth(scopes)

    for playlist_uri in SPOTIFY_PLAYLISTS_URIS:
        playlist_name = sp.get_playlist_name_by_uri(playlist_uri)
        logger.info(f"Playlist: {playlist_name}")

        # Get the tracks from the playlist
        tracks = sp.get_playlist_tracks_by_uri(playlist_uri)

        artists = []
        for track in tracks:
            for artist in track["artists"]:
                artists.append(
                    {
                        "id": artist["id"],
                        "name": artist["name"]
                    }
                )

        playlist_cover = Image.new("RGB", (ARTIST_IMAGE_SIZE * 2, ARTIST_IMAGE_SIZE * 2))

        counter = Counter([artist["name"] for artist in artists])
        four_most_common = counter.most_common(4)
        for index, (artist_name, occurence) in enumerate(four_most_common):
            logger.info(f"{index} - Found {occurence} song(s) from {artist_name}")
            current_artist = next(artist for artist in artists if artist["name"] == artist_name)
            image_url = sp.get_artist_image_by_id(current_artist["id"])

            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))
            img.thumbnail((ARTIST_IMAGE_SIZE, ARTIST_IMAGE_SIZE), Image.ANTIALIAS)
            x = index // 2 * ARTIST_IMAGE_SIZE
            y = index % 2 * ARTIST_IMAGE_SIZE
            w, h = img.size
            playlist_cover.paste(img, (x, y, x + w, y + h))

        logger.info("Saving image...")
        playlist_cover.save(os.path.expanduser(f"{playlist_name}.jpg"))

        logger.info("Updating playlist cover...")
        buffered = BytesIO()
        playlist_cover.save(buffered, format="JPEG")
        playlist_cover_string = base64.b64encode(buffered.getvalue())
        sp.update_playlist_cover_image(playlist_uri, playlist_cover_string)


if __name__ == "__main__":
    start_time = time.time()
    main()
    duration = round(time.time() - start_time, 2)
    logger.info(f"Execution: {duration} seconds")
