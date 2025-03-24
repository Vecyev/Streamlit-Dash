from strategy.manager import StrategyManager
from utils.ibkr_interface import IBKRClient

if __name__ == "__main__":
    ibkr = IBKRClient()
    manager = StrategyManager(ibkr, symbol="NVDA", cost_basis=650)
    manager.run()