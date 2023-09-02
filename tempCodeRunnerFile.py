if response.status_code != 201:
        raise Exception(f"Request returned an error: {response.status_code}, {response.text}")
