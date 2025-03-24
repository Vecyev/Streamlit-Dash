from strategy.volatility_model import VolatilityRegime
from strategy.trade_filter import TradeFilter
from strategy.execution import TradeExecutor
from config import *
from utils.earnings import is_near_earnings

class CoveredCallStrategy:
    def __init__(self, ibkr_client, symbol, cost_basis=650):
        self.symbol = symbol
        self.ibkr = ibkr_client
        self.vol_model = VolatilityRegime(self.symbol)
        self.filter = TradeFilter(self.symbol, cost_basis)
        self.executor = TradeExecutor(self.ibkr)
        self.model = TradeModel()
        self.signal_engine = TradeSignalFeatures(symbol)
        self.scorer = TradeScorer(symbol)

    def run(self):
        if is_near_earnings(self.symbol):
            print("[EARNINGS] Skipping covered call due to upcoming earnings.")
            return

        vol_regime = self.vol_model.detect_regime()
        if not self.ibkr.has_underlying(self.symbol):
            self.ibkr.buy_underlying(self.symbol)

        open_call = self.ibkr.get_open_calls(self.symbol)
        if open_call and open_call.days_to_expiry > ROLL_DTE_THRESHOLD:
            return

        chain = self.ibkr.get_option_chain(self.symbol)
        selected = self.filter.select_strikes(chain)

        if selected:
            self.executor.write_calls(self.symbol, selected)
            for opt in selected:
                signal = self.signal_engine.get_features(opt, side="CALL")
                score = self.model.predict_score(signal)
                if score is None or score < 0.15:
                    continue
                premium = round(opt.strike * opt.yield_, 2)
                self.scorer.score_and_log_trade(opt, premium, side="CALL")
                send_slack_alert(f'[CALL] Sold NVDA call {opt.strike} exp {opt.expiry}')