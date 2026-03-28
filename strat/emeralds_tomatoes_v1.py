from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def run(self, state: TradingState) -> tuple[dict[str, list[Order]], int, str]:
        result = {}
        
        # This will automatically run for both EMERALDS and TOMATOES
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Safety check: skip if the market data is empty for this tick
            if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
                continue
                
            # 1. Dynamically read the real market prices right now
            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())
            
            current_position = state.position.get(product, 0)
            POSITION_LIMIT = 80 # Limit is 80 for Prosperity 4 assets
            
            # 2. Join the Best Bid to buy
            buy_volume = POSITION_LIMIT - current_position
            if buy_volume > 0:
                orders.append(Order(product, best_bid, buy_volume))
                
            # 3. Join the Best Ask to sell
            sell_volume = -POSITION_LIMIT - current_position
            if sell_volume < 0:
                orders.append(Order(product, best_ask, sell_volume))
                
            result[product] = orders
            
        return result, 0, ""
        
