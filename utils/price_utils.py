#!/usr/bin/env python3
"""
Price Utilities
Handles proper price rounding to eliminate floating-point precision errors
"""

from decimal import Decimal, ROUND_HALF_UP
import math

def round_to_cent(price: float) -> float:
    """
    Properly round a price to the nearest cent to avoid sub-penny precision errors.
    
    Args:
        price (float): The price to round
        
    Returns:
        float: Price rounded to nearest cent (2 decimal places)
    """
    if price is None:
        return None
        
    # Convert to Decimal for precise arithmetic, then round to 2 decimal places
    decimal_price = Decimal(str(price))
    rounded_decimal = decimal_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(rounded_decimal)

def round_to_penny(price: float) -> float:
    """
    Alternative method using math.floor/ceil for cent rounding.
    
    Args:
        price (float): The price to round
        
    Returns:
        float: Price rounded to nearest cent
    """
    if price is None:
        return None
        
    # Multiply by 100, round to integer, then divide by 100
    return math.floor(price * 100 + 0.5) / 100

def validate_price_precision(price: float, symbol: str = "") -> bool:
    """
    Validate that a price doesn't have sub-penny precision errors.
    
    Args:
        price (float): Price to validate
        symbol (str): Symbol for logging purposes
        
    Returns:
        bool: True if price is properly rounded to cents
    """
    if price is None:
        return False
        
    # Check if price has more than 2 decimal places of precision
    rounded_price = round_to_cent(price)
    precision_diff = abs(price - rounded_price)
    
    # If difference is greater than 1e-10, we have precision issues
    if precision_diff > 1e-10:
        print(f"WARNING: {symbol} price {price} has sub-penny precision. Rounded: {rounded_price}")
        return False
        
    return True

def calculate_stop_loss_price(current_price: float, stop_loss_pct: float) -> float:
    """
    Calculate stop loss price with proper rounding.
    
    Args:
        current_price (float): Current market price
        stop_loss_pct (float): Stop loss percentage (e.g., 0.005 for 0.5%)
        
    Returns:
        float: Properly rounded stop loss price
    """
    raw_stop_price = current_price * (1 - stop_loss_pct)
    return round_to_cent(raw_stop_price)

def calculate_take_profit_price(current_price: float, take_profit_pct: float) -> float:
    """
    Calculate take profit price with proper rounding.
    
    Args:
        current_price (float): Current market price
        take_profit_pct (float): Take profit percentage (e.g., 0.01 for 1%)
        
    Returns:
        float: Properly rounded take profit price
    """
    raw_profit_price = current_price * (1 + take_profit_pct)
    return round_to_cent(raw_profit_price)

def calculate_trailing_stop_price(highest_price: float, trailing_pct: float) -> float:
    """
    Calculate trailing stop price with proper rounding.
    
    Args:
        highest_price (float): Highest price achieved
        trailing_pct (float): Trailing distance percentage
        
    Returns:
        float: Properly rounded trailing stop price
    """
    raw_trailing_price = highest_price * (1 - trailing_pct)
    return round_to_cent(raw_trailing_price)
