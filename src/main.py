import base64
from collections import Counter
from io import BytesIO
import os
import time
from spotify import Spotify
from dotenv import load_dotenv
from loguru import logger
from PIL import Image, ImageFont, ImageDraw
import requests

load_dotenv()


SPOTIFY_PLAYLISTS_URIS = [
    "https://open.spotify.com/playlist/0JP3smzah2mTnxIZIVjVX0?si=e33aaca9d1334dc6"
]
ARTIST_IMAGE_SIZE = 640
IMAGE_SIZE = ARTIST_IMAGE_SIZE * 2
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

        playlist_cover = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE))

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

        # Converting back to RGBA to apply gradient
        playlist_cover = playlist_cover.convert('RGBA')
        gradient = Image.new('L', (1, IMAGE_SIZE), color=0xFF)
        current_color = 255
        for y in range(IMAGE_SIZE):
            if y % 2 == 0:
                current_color -= 1
            current_y = IMAGE_SIZE - y - 1
            gradient.putpixel((0, current_y), current_color)
        alpha = gradient.resize(playlist_cover.size)
        black_im = Image.new('RGBA', (IMAGE_SIZE, IMAGE_SIZE), color=0)
        black_im.putalpha(alpha)
        playlist_cover = Image.alpha_composite(playlist_cover, black_im)

        # Adding the text
        draw = ImageDraw.Draw(playlist_cover)
        font = ImageFont.truetype('./fonts/Montserrat-Bold.ttf', 120)
        draw.text(xy=(ARTIST_IMAGE_SIZE, IMAGE_SIZE - 50), text=playlist_name, fill=(255, 255, 255), anchor="ms", font=font, align="center")

        # Converting back to RGB
        playlist_cover = playlist_cover.convert('RGB')

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
