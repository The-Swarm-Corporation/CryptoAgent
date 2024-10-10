

# CryptoAgent: Real-Time Cryptocurrency Data Analysis Agent

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)


CryptoAgent is a professional, enterprise-grade solution designed to fetch, analyze, and summarize real-time cryptocurrency data. It integrates with CoinGecko's API to retrieve the latest crypto metrics and leverages OpenAI's advanced language model to generate insightful, concise reports tailored for crypto investors and financial analysts.

## Key Features

- **Real-Time Data Fetching**: Retrieves live cryptocurrency data, including current price, market capitalization, trading volume, supply details, and recent price changes.
- **Advanced Analysis**: Summarizes complex crypto data into clear, actionable insights, allowing users to stay informed on key market trends.
- **Enterprise-Grade Reliability**: Built with robust error handling, retries, and logging to ensure uninterrupted data retrieval and analysis.
- **Customizable Reports**: Designed to provide tailored insights based on user requirements, making it suitable for investors, traders, and analysts.

## Use Cases

- **Market Monitoring**: Track real-time prices and key metrics for any cryptocurrency.
- **Investment Research**: Generate comprehensive reports on specific coins, including trends, market sentiment, and price changes.
- **Financial Analysis**: Use CryptoAgent to analyze large volumes of crypto data, summarize trends, and provide strategic insights.

## Installation

```bash
$ pip3 install -U cryptoagent
```

## Usage

```python
import os

from swarm_models import OpenAIChat
from swarms import Agent

from cryptoagent.main import CryptoAgent

# Create an instance of the OpenAIChat class for LLM integration
api_key = os.getenv("OPENAI_API_KEY")
model = OpenAIChat(
    openai_api_key=api_key, model_name="gpt-4o-mini", temperature=0.1
)

# Create the input agent
input_agent = Agent(
    agent_name="Crypto-Analysis-Agent",
    system_prompt="You are a financial analysis agent that provides crypto analysis with live data.",
    llm=model,
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    dynamic_temperature_enabled=True,
    saved_state_path="crypto_agent.json",
    user_name="swarms_corp",
    retry_attempts=2,
    context_length=10000,
)

# Create CryptoAgent instance and pass the input agent
crypto_analyzer = CryptoAgent(agent=input_agent)

# Example coin IDs to summarize multiple coins
coin_ids = ["bitcoin", "ethereum"]

# Fetch and summarize crypto data for multiple coins in parallel
summaries = crypto_analyzer.run(
    coin_ids, "Conduct a thorough analysis of the following coins:", #real_time=True # Make it real-time where it will fetch the results in real-time
)

# # Print the summaries
print(summaries)


```

## System Architecture
CryptoAgent follows a modular architecture:

- **CryptoAgentAgent** performs the crypto analysis by combining data fetched from the API with OpenAI's powerful language models.
- **Agent Framework**: The agent architecture, powered by `swarms`, ensures flexibility, scalability, and reliability for enterprise deployments.

## Enterprise-Grade Features

- **Scalability**: Easily integrates into larger infrastructures for monitoring hundreds of cryptocurrencies simultaneously.
- **Error Handling and Retries**: Built-in mechanisms for handling API failures and retrying failed requests ensure uninterrupted service.
- **Customization**: Modify the system prompt to tailor the analysis to specific use cases, whether it’s for a hedge fund, a financial institution, or individual investors.
- **Security**: Sensitive API keys and environment variables are securely managed via `.env` and best practices for API management.

## Getting Started

1. **Prerequisites**: Ensure you have Python 3.8+ installed.
2. **API Access**: You’ll need an OpenAI API key to interact with the model.
3. **Run the Agent**: Follow the instructions in the [Installation](#installation) section to set up and run CryptoAgent.

## Sample Output

```text
Coin: Bitcoin (BTC)
Current Price: $45,320.12
Market Cap: $853,000,000,000
24h Trading Volume: $32,000,000,000
Circulating Supply: 18,700,000 BTC
Total Supply: N/A
Price Change (24h): +4.2%

Analysis: Bitcoin has seen a significant price increase of 4.2% over the past 24 hours, driven by increased trading volume. The market cap remains strong, reflecting continued investor confidence.
```

## Future Enhancements

- **Multi-Coin Analysis**: Enable simultaneous analysis of multiple cryptocurrencies for portfolio managers.
- **Sentiment Analysis**: Incorporate social media and news sentiment analysis into the crypto reports.
- **Predictive Analytics**: Add a layer of predictive insights using historical data to forecast market trends.
  
## Contributing

We welcome contributions from the community! Please follow our [contribution guidelines](CONTRIBUTING.md) and submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For enterprise inquiries, custom deployments, or support, please contact [kye@swarms.world](mailto:kye@swarms.world).
