import os

from swarm_models import OpenAIChat
from swarms import Agent

from cryptoagent.main import CryptoAgent
from cryptoagent.prompts import CRYPTO_AGENT_SYS_PROMPT

# Create an instance of the OpenAIChat class for LLM integration
api_key = os.getenv("OPENAI_API_KEY")
model = OpenAIChat(
    openai_api_key=api_key, model_name="gpt-4o-mini", temperature=0.1
)

# Create the input agent
input_agent = Agent(
    agent_name="Crypto-Analysis-Agent",
    system_prompt=CRYPTO_AGENT_SYS_PROMPT,
    llm=model,
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    dynamic_temperature_enabled=True,
    saved_state_path="crypto_agent.json",
    user_name="swarms_corp",
    retry_attempts=1,
    context_length=10000,
)

# Create CryptoAgent instance and pass the input agent
crypto_analyzer = CryptoAgent(agent=input_agent, autosave=True)

# Example coin IDs to summarize multiple coins
coin_ids = ["bitcoin", "ethereum"]

# Fetch and summarize crypto data for multiple coins in parallel
summaries = crypto_analyzer.run(
    coin_ids,
    "Conduct a thorough analysis of the following coins:",
    # real_time=True,
)

# # Print the summaries
print(summaries)
