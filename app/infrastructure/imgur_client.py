from imgurpython import ImgurClient as IC

import requests


class ImgurClient:

    def __init__(self):
        pass

    def upload(self, url: str):

        client_id = ''
        client_secret = ''
        access_token = ''
        refresh_token = ''

        client = IC(client_id, client_secret, access_token, refresh_token)

        client.upload_from_url(url)

    def upload_image_from_url(self, image_url):
        access_token = ''
        refresh_token = ''

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        data = {
            "image": image_url,
            "type": "url",
            "title": "Uploaded via API",
            "description": "From a Python script"
        }

        response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)
        response.raise_for_status()

        result = response.json()
        link = result["data"]["link"]
        print("Image uploaded to:", link)

        print("Image ID:", result["data"]["id"])

        # Optional: Check account associated with the image
        info_url = f"https://api.imgur.com/3/image/{result['data']['id']}"
        info_res = requests.get(info_url, headers=headers)
        print("Image info:", info_res.json())

        return link

if __name__ == '__main__':
    client = ImgurClient()
    client.upload_image_from_url("https://images.ctfassets.net/kftzwdyauwt9/4kSOjNUoQbwtFxwr5Arer4/27008d923fdcee81834048e92c3ebe43/IMG_6112.png")