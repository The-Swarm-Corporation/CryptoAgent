import requests


def fetch_coinbase_crypto_data(crypto_symbol: str):
    """
    Fetch all the available data for a specific cryptocurrency from the Coinbase API.

    Args:
        crypto_symbol (str): The symbol of the cryptocurrency (e.g., BTC, ETH).

    Returns:
        dict: The data returned from the Coinbase API for the specified cryptocurrency.
    """

    # Coinbase API endpoint for specific cryptocurrency
    url = (
        f"https://api.coinbase.com/v2/prices/{crypto_symbol}-USD/spot"
    )

    try:
        # Sending the GET request to Coinbase API
        response = requests.get(url)

        # Raise an exception for any HTTP errors
        response.raise_for_status()

        # Parsing the response to JSON
        data = response.json()

        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# Example usage
crypto_data = fetch_coinbase_crypto_data("BTC")
print(crypto_data)
