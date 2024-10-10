import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Union

import requests
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from swarms import Agent, create_file_in_folder

load_dotenv()


class TokenUsage(BaseModel):
    """
    Schema for logging token usage by the LLM.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class CryptoAgentSchema(BaseModel):
    """
    Pydantic schema for the final crypto analysis output.
    """
    id: str = Field(
        default_factory=lambda: uuid.uuid4().hex
    )  # Ensure ID is generated
    coin_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    summary: str = "No summary available"
    raw_data: Dict = Field(default_factory=dict)


class CryptoAgentSchemaLog(BaseModel):
    id: str = Field(
        default_factory=lambda: uuid.uuid4().hex
    )  # Ensure ID is generated
    logs: List[CryptoAgentSchema] = Field(default_factory=list)
    time_stamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class CryptoAgent:
    def __init__(
        self,
        name: str = "crypto-price-agent-01",
        description: str = "Fetches real-time crypto data for a specific coin",
        agent: Agent = None,
        currency: str = "usd",
        log_tokens: bool = True,
        log_level: str = "INFO",
        autosave: bool = True,
        workspace_folder: str = "crypto-agent-runs",
    ):
        """
        Initialize the CryptoAgent with an agent, currency, and logging options.

        Args:
        - agent (Agent): The agent instance for generating summaries.
        - currency (str, optional): The currency to use for crypto data. Defaults to "usd".
        - log_tokens (bool, optional): Flag to enable or disable token usage logging. Defaults to True.
        - log_level (str, optional): The log level to use. Defaults to "INFO".
        """
        self.name = name
        self.description = description
        self.agent = agent
        self.currency = currency
        self.autosave = autosave
        self.workspace_folder = workspace_folder
        self.coingecko_url = (
            "https://api.coingecko.com/api/v3/coins/markets"
        )
        self.log_tokens = log_tokens
        self.logs = CryptoAgentSchemaLog(
            logs=[],
        )
        logger.add("crypto_agent.log", rotation="10 MB")
        logger.level = log_level
        self.log_file_name = f"crypto-agent-run-time-{uuid.uuid4().hex}"

    def get_crypto_data_coingecko(
        self, coin_id: str
    ) -> Union[Dict, str]:
        """
        Fetch crypto data from CoinGecko.

        Args:
        - coin_id (str): The ID of the coin to fetch data for.

        Returns:
        - Union[Dict, str]: The fetched crypto data or an error message.
        """
        try:
            params = {"vs_currency": self.currency, "ids": coin_id}
            response = requests.get(self.coingecko_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]  # Return the first result
            else:
                logger.warning(
                    f"No data found for {coin_id} on CoinGecko."
                )
                return {
                    "error": f"No data found for {coin_id} on CoinGecko."
                }
        except requests.RequestException as e:
            logger.error(
                f"Error fetching data from CoinGecko for {coin_id}: {e}"
            )
            return {"error": str(e)}

    def get_crypto_data(self, coin_id: str) -> Dict:
        """
        Fetch crypto data, prioritizing CoinGecko and using CoinMarketCap as a fallback.

        Args:
        - coin_id (str): The ID of the coin to fetch data for.

        Returns:
        - Dict: The fetched crypto data.
        """
        logger.info(f"Fetching data for {coin_id} from CoinGecko.")
        data = self.get_crypto_data_coingecko(coin_id)
        return data

    def fetch_and_summarize(
        self, coin_id: str, task: str = None
    ) -> CryptoAgentSchema:
        """
        Fetch crypto data and generate a summary using the input agent.

        Args:
        - coin_id (str): The ID of the coin to summarize.
        - task (str, optional): The task to perform on the coin data. Defaults to None.

        Returns:
        - CryptoAgentSchema: The summary of the crypto data.
        """
        crypto_data = self.get_crypto_data(coin_id)

        # Prepare data for the agent
        crypto_info = f"""
        Coin: {crypto_data.get('name', coin_id)} ({crypto_data.get('symbol', coin_id).upper()})
        Current Price: ${crypto_data.get('current_price', crypto_data.get('price', 'N/A'))}
        Market Cap: ${crypto_data.get('market_cap', 'N/A')}
        24h Trading Volume: ${crypto_data.get('total_volume', crypto_data.get('volume_24h', 'N/A'))}
        Circulating Supply: {crypto_data.get('circulating_supply', 'N/A')}
        Total Supply: {crypto_data.get('total_supply', 'N/A')}
        All-Time High: ${crypto_data.get('ath', 'N/A')}
        All-Time Low: ${crypto_data.get('atl', 'N/A')}
        Market Rank: {crypto_data.get('market_cap_rank', 'N/A')}
        Fully Diluted Valuation: ${crypto_data.get('fully_diluted_valuation', 'N/A')}
        """

        prompt = f"{self.agent.system_prompt}\n\nHere is the live data for {crypto_data.get('name', coin_id)}:\n{crypto_info}\n\nPlease provide an analysis for {crypto_data.get('name', coin_id)}."

        # Run the agent to summarize the coin data
        logger.info(f"Summarizing data for {coin_id}.")
        result = self.agent.run(task + prompt)

        # Return analysis with Pydantic schema
        self.logs.logs.append(
            CryptoAgentSchema(
                coin_id=coin_id,
                timestamp=datetime.utcnow().isoformat(),
                summary=result,
                raw_data=crypto_data,
            )
        )

        return result

    def run(
        self,
        coin_ids: List[str],
        task: str = None,
        real_time: bool = False,
    ) -> str:
        """
        Summarize multiple coins in parallel using ThreadPoolExecutor and return JSON format. Optionally, fetches data in real-time or every 1 second.

        Args:
        - coin_ids (List[str]): A list of coin IDs to summarize.
        - task (str, optional): The task to perform on the coin data. Defaults to None.
        - real_time (bool, optional): If True, fetches data in real-time or every 1 second. Defaults to False.

        Returns:
        - str: The summaries of the crypto data in JSON format.
        """
        if real_time:
            while True:
                with ThreadPoolExecutor() as executor:
                    future_to_coin = {
                        executor.submit(
                            self.fetch_and_summarize, coin_id, task
                        ): coin_id
                        for coin_id in coin_ids
                    }

                    for future in as_completed(future_to_coin):
                        coin_id = future_to_coin[future]
                        try:
                            future.result()
                            logger.info(
                                f"Completed summary for {coin_id}."
                            )
                        except KeyboardInterrupt:
                            logger.info(
                                "KeyboardInterrupt detected. Auto-saving logs before exiting."
                            )
                            if self.autosave:
                                create_file_in_folder(
                                    self.workspace_folder,
                                    self.log_file_name,
                                    self.logs.model_dump_json(
                                        indent=4
                                    ),
                                )
                            raise
                        except Exception as exc:
                            logger.error(
                                f"Error summarizing {coin_id}: {exc}"
                            )
                            error_summary = CryptoAgentSchema(
                                coin_id=coin_id,
                                timestamp=datetime.utcnow().isoformat(),
                                summary=f"Error summarizing {coin_id}",
                                raw_data={},
                            )
                            self.logs.logs.append(error_summary)
                            if self.autosave:
                                create_file_in_folder(
                                    self.workspace_folder,
                                    self.log_file_name,
                                    self.logs.model_dump_json(
                                        indent=4
                                    ),
                                )
                time.sleep(
                    1
                )  # Sleep for 1 second before fetching again
        else:
            with ThreadPoolExecutor() as executor:
                future_to_coin = {
                    executor.submit(
                        self.fetch_and_summarize, coin_id, task
                    ): coin_id
                    for coin_id in coin_ids
                }

                for future in as_completed(future_to_coin):
                    coin_id = future_to_coin[future]
                    try:
                        future.result()
                        logger.info(
                            f"Completed summary for {coin_id}."
                        )
                    except KeyboardInterrupt:
                        logger.info(
                            "KeyboardInterrupt detected. Auto-saving logs before exiting."
                        )
                        if self.autosave:
                            create_file_in_folder(
                                self.workspace_folder,
                                self.log_file_name,
                                self.logs.model_dump_json(indent=4),
                            )
                        raise
                    except Exception as exc:
                        logger.error(
                            f"Error summarizing {coin_id}: {exc}"
                        )
                        error_summary = CryptoAgentSchema(
                            coin_id=coin_id,
                            timestamp=datetime.utcnow().isoformat(),
                            summary=f"Error summarizing {coin_id}",
                            raw_data={},
                        )
                        self.logs.logs.append(error_summary)
                        if self.autosave:
                            create_file_in_folder(
                                self.workspace_folder,
                                self.log_file_name,
                                self.logs.model_dump_json(indent=4),
                            )

        if self.autosave is True:
            create_file_in_folder(
                self.workspace_folder,
                self.log_file_name,
                self.logs.model_dump_json(indent=4),
            )
        
        # Return the result as a JSON string
        return self.logs.model_dump_json(indent=4)
