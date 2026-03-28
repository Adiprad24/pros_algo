from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        for product in state.order_depths.keys():
            if product == "EMERALDS":
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                
                # EMERALDS oscillate around a fair value of 10,000.
                # We are willing to buy at 9,998 (or lower) and sell at 10,002 (or higher).
                acceptable_buy_price = 9998
                acceptable_sell_price = 10002
                
                # Retrieve our current inventory to ensure we don't breach the limit.
                current_position = state.position.get(product, 0)
                POSITION_LIMIT = 80
                
                # 1. SNIPE MISPRICED ASKS (BUYING)
                # If someone is selling for cheap (<= 9998), we buy it from them.
                if len(order_depth.sell_orders) > 0:
                    for ask_price, ask_volume in list(order_depth.sell_orders.items()):
                        if ask_price <= acceptable_buy_price:
                            # Ask volumes are negative in the datamodel, so we use abs()
                            available_volume = abs(ask_volume)
                            # Only buy up to our strict position limit
                            trade_volume = min(available_volume, POSITION_LIMIT - current_position)
                            
                            if trade_volume > 0:
                                print(f"Buying {trade_volume} EMERALDS at {ask_price}")
                                orders.append(Order(product, ask_price, trade_volume))
                                current_position += trade_volume

                # 2. SNIPE MISPRICED BIDS (SELLING)
                # If someone is buying for a premium (>= 10002), we sell to them.
                if len(order_depth.buy_orders) > 0:
                    for bid_price, bid_volume in list(order_depth.buy_orders.items()):
                        if bid_price >= acceptable_sell_price:
                            # Bid volumes are positive, we calculate how much we can safely short/sell
                            trade_volume = min(bid_volume, POSITION_LIMIT + current_position)
                            
                            if trade_volume > 0:
                                print(f"Selling {trade_volume} EMERALDS at {bid_price}")
                                # We send a negative volume to indicate a SELL order
                                orders.append(Order(product, bid_price, -trade_volume))
                                current_position -= trade_volume

                result[product] = orders

        return result
