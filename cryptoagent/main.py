import os
import requests
from typing import List, Dict, Union
from swarms import Agent
from swarm_models import OpenAIChat
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class CryptoAnalysis:
    def __init__(self, agent: Agent, currency: str = 'usd'):
        self.agent = agent
        self.currency = currency
        self.coingecko_url = "https://api.coingecko.com/api/v3/coins/markets"
        self.coinmarketcap_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        self.cmc_api_key = os.getenv("COINMARKETCAP_API_KEY")

    def get_crypto_data_coingecko(self, coin_id: str) -> Union[Dict, str]:
        """
        Fetch crypto data from CoinGecko.
        """
        try:
            params = {
                'vs_currency': self.currency,
                'ids': coin_id
            }
            response = requests.get(self.coingecko_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]  # Return the first result
            else:
                logger.warning(f"No data found for {coin_id} on CoinGecko.")
                return {"error": f"No data found for {coin_id} on CoinGecko."}
        except requests.RequestException as e:
            logger.error(f"Error fetching data from CoinGecko for {coin_id}: {e}")
            return {"error": str(e)}

    def get_crypto_data_coinmarketcap(self, coin_id: str) -> Union[Dict, str]:
        """
        Fetch crypto data from CoinMarketCap as a fallback.
        """
        try:
            headers = {
                'X-CMC_PRO_API_KEY': self.cmc_api_key
            }
            params = {
                'symbol': coin_id.upper(),
                'convert': self.currency.upper()
            }
            response = requests.get(self.coinmarketcap_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "data" in data and coin_id.upper() in data["data"]:
                coin_data = data["data"][coin_id.upper()]["quote"][self.currency.upper()]
                return coin_data
            else:
                logger.warning(f"No data found for {coin_id} on CoinMarketCap.")
                return {"error": f"No data found for {coin_id} on CoinMarketCap."}
        except requests.RequestException as e:
            logger.error(f"Error fetching data from CoinMarketCap for {coin_id}: {e}")
            return {"error": str(e)}

    def get_crypto_data(self, coin_id: str) -> Dict:
        """
        Fetch crypto data, prioritizing CoinGecko and using CoinMarketCap as a fallback.
        """
        logger.info(f"Fetching data for {coin_id} from CoinGecko.")
        data = self.get_crypto_data_coingecko(coin_id)
        if "error" in data:
            logger.info(f"Fallback to CoinMarketCap for {coin_id}.")
            data = self.get_crypto_data_coinmarketcap(coin_id)
        return data

    def fetch_and_summarize(self, coin_id: str) -> str:
        """
        Fetch crypto data and generate a summary using the input agent.
        """
        crypto_data = self.get_crypto_data(coin_id)
        
        if "error" in crypto_data:
            return f"Error fetching {coin_id} data: {crypto_data['error']}"
        
        # Prepare data for the agent
        crypto_info = f"""
        Coin: {crypto_data.get('name', coin_id)} ({crypto_data.get('symbol', coin_id).upper()})
        Current Price: ${crypto_data.get('current_price', crypto_data.get('price', 'N/A'))}
        Market Cap: ${crypto_data.get('market_cap', 'N/A')}
        24h Trading Volume: ${crypto_data.get('total_volume', crypto_data.get('volume_24h', 'N/A'))}
        Circulating Supply: {crypto_data.get('circulating_supply', 'N/A')}
        Total Supply: {crypto_data.get('total_supply', 'N/A')}
        Price Change (24h): {crypto_data.get('price_change_percentage_24h', 'N/A')}%
        All-Time High: ${crypto_data.get('ath', 'N/A')}
        All-Time Low: ${crypto_data.get('atl', 'N/A')}
        Market Rank: {crypto_data.get('market_cap_rank', 'N/A')}
        Fully Diluted Valuation: ${crypto_data.get('fully_diluted_valuation', 'N/A')}
        """
        
        prompt = f"{self.agent.system_prompt}\n\nHere is the live data for {crypto_data.get('name', coin_id)}:\n{crypto_info}\n\nPlease provide an analysis for {crypto_data.get('name', coin_id)}."

        # Run the agent to summarize the coin data
        logger.info(f"Summarizing data for {coin_id}.")
        summary = self.agent.llm.run(prompt)
        return summary

    def run(self, coin_ids: List[str]) -> List[str]:
        """
        Summarize multiple coins in parallel using ThreadPoolExecutor.
        """
        summaries = []
        with ThreadPoolExecutor() as executor:
            future_to_coin = {executor.submit(self.fetch_and_summarize, coin_id): coin_id for coin_id in coin_ids}
            
            for future in as_completed(future_to_coin):
                coin_id = future_to_coin[future]
                try:
                    summary = future.result()
                    summaries.append(summary)
                    logger.info(f"Completed summary for {coin_id}.")
                except Exception as exc:
                    logger.error(f"Error summarizing {coin_id}: {exc}")
                    summaries.append(f"Error summarizing {coin_id}")
        return summaries
