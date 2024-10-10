import requests
from loguru import logger
from typing import Tuple, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

def format_dict_row_by_row(data: dict) -> str:
    """
    Format a dictionary such that each key and value is printed on a separate line.

    Args:
        data (dict): The dictionary to format.

    Returns:
        str: A formatted string with each key and value on separate lines.
    """
    formatted_lines = []
    for key, value in data.items():
        formatted_lines.append(f"Key: {key}")
        formatted_lines.append(f"Value: {value}")
    return "\n".join(formatted_lines)

def fetch_and_analyze_ethereum_transaction(
    tx_hash: str,
    return_type: str = "both"
) -> Tuple[str, Dict[str, Any]] or str or Dict[str, Any]:
    """
    Fetch and analyze Ethereum blockchain transaction data.

    Args:
        tx_hash (str): The transaction hash of the Ethereum transaction.
        api_key (str): The API key to authenticate with the Ethereum node or Etherscan.
        return_type (str, optional): Specify the return type. Defaults to "both". Options: "both", "string", "dict".

    Returns:
        Tuple[str, Dict[str, Any]] or str or Dict[str, Any]: Depending on the return_type, returns a tuple containing a status message (str) and
                                    a dictionary with the fetched and analyzed transaction data (Dict[str, Any]), or only the status message (str), or only the transaction data (Dict[str, Any]).

    Raises:
        ValueError: If the transaction data cannot be fetched or analyzed.
    """
    api_key = os.getenv("ETHERSCAN_KEY")
    logger.info(
        f"Fetching Ethereum transaction data for hash: {tx_hash}"
    )

    # API URL template, assuming Etherscan for this example
    etherscan_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={api_key}"

    try:
        # Make the request to the API
        response = requests.get(etherscan_url)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Extract transaction data from the response
        transaction_data = response.json()

        # Check if the transaction data was fetched successfully
        if transaction_data.get("result") is None:
            logger.error(
                f"Transaction data not found for hash: {tx_hash}"
            )
            if return_type == "both":
                return "Transaction data not found.", {}
            elif return_type == "string":
                return "Transaction data not found."
            elif return_type == "dict":
                return {}
            else:
                raise ValueError("Invalid return_type specified.")

        logger.info(
            f"Successfully fetched transaction data for hash: {tx_hash}"
        )

        # Format the transaction data as a string for string return type
        formatted_transaction_data = str(transaction_data["result"])

        # Return a success message and the transaction data based on return_type
        if return_type == "both":
            return (
                "Transaction data fetched and analyzed successfully.",
                transaction_data["result"],
            )
        elif return_type == "string":
            return f"####################### ETH TX Transaction #####################" + "\n" + "Transaction data fetched and analyzed successfully for the tx hash: {tx_hash} || Data Available:" + "\n" + format_dict_row_by_row(transaction_data)
        elif return_type == "dict":
            return transaction_data["result"]
        else:
            raise ValueError("Invalid return_type specified.")

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        if return_type == "both":
            return (
                f"HTTP error occurred while fetching data: {http_err}",
                {},
            )
        elif return_type == "string":
            return f"HTTP error occurred while fetching data: {http_err}"
        elif return_type == "dict":
            return {}
        else:
            raise ValueError("Invalid return_type specified.")

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        if return_type == "both":
            return (
                f"Request error occurred while fetching data: {req_err}",
                {},
            )
        elif return_type == "string":
            return f"Request error occurred while fetching data: {req_err}"
        elif return_type == "dict":
            return {}
        else:
            raise ValueError("Invalid return_type specified.")

    except ValueError as val_err:
        logger.error(
            f"Value error while processing transaction data: {val_err}"
        )
        if return_type == "both":
            return f"Error processing the transaction data: {val_err}", {}
        elif return_type == "string":
            return f"Error processing the transaction data: {val_err}"
        elif return_type == "dict":
            return {}
        else:
            raise ValueError("Invalid return_type specified.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if return_type == "both":
            return f"Unexpected error: {e}", {}
        elif return_type == "string":
            return f"Unexpected error: {e}"
        elif return_type == "dict":
            return {}
        else:
            raise ValueError("Invalid return_type specified.")

# out = fetch_and_analyze_ethereum_transaction("0xa55de4c4362ac656ee0d82a16c4332d5e93e2818b896d411e2b9f79c61f8a217", return_type="string")
# print(out)