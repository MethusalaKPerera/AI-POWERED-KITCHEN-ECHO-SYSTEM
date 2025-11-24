"""
Currency Conversion Module
Uses forex-python for real-time currency conversion
"""
from forex_python.converter import CurrencyRates, CurrencyCodes
from typing import Optional, Dict
from datetime import datetime


class CurrencyConverter:
    """Handles currency conversion for product prices"""
    
    def __init__(self):
        try:
            self.currency_rates = CurrencyRates()
            self.currency_codes = CurrencyCodes()
        except Exception as e:
            print(f"Currency converter initialization error: {str(e)}")
            self.currency_rates = None
            self.currency_codes = None
    
    def convert_price(
        self,
        amount: float,
        from_currency: str = 'USD',
        to_currency: str = 'USD'
    ) -> Dict:
        """
        Convert price from one currency to another
        Returns: {
            'original_amount': float,
            'converted_amount': float,
            'from_currency': str,
            'to_currency': str,
            'rate': float,
            'symbol': str
        }
        """
        if from_currency == to_currency:
            return {
                'original_amount': amount,
                'converted_amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': 1.0,
                'symbol': self._get_symbol(to_currency)
            }
        
        if not self.currency_rates:
            # Fallback to mock rates if forex-python not available
            return self._mock_convert(amount, from_currency, to_currency)
        
        try:
            rate = self.currency_rates.get_rate(from_currency, to_currency)
            converted = amount * rate
            
            return {
                'original_amount': amount,
                'converted_amount': round(converted, 2),
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': round(rate, 4),
                'symbol': self._get_symbol(to_currency)
            }
        except Exception as e:
            print(f"Currency conversion error: {str(e)}")
            return self._mock_convert(amount, from_currency, to_currency)
    
    def convert_product_prices(
        self,
        products: list,
        target_currency: str = 'USD'
    ) -> list:
        """Convert prices for a list of products"""
        converted_products = []
        
        for product in products:
            product_currency = product.get('currency', 'USD')
            original_price = product.get('price', 0)
            
            conversion = self.convert_price(
                original_price,
                product_currency,
                target_currency
            )
            
            product_copy = product.copy()
            product_copy['price'] = conversion['converted_amount']
            product_copy['original_price'] = original_price
            product_copy['original_currency'] = product_currency
            product_copy['currency'] = target_currency
            product_copy['currency_symbol'] = conversion['symbol']
            product_copy['conversion_rate'] = conversion['rate']
            
            converted_products.append(product_copy)
        
        return converted_products
    
    def _get_symbol(self, currency_code: str) -> str:
        """Get currency symbol"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'LKR': 'Rs',
            'JPY': '¥',
            'CNY': '¥',
            'AUD': 'A$',
            'CAD': 'C$'
        }
        return symbols.get(currency_code, currency_code)
    
    def _mock_convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Dict:
        """Mock currency conversion (fallback)"""
        # Mock exchange rates (approximate)
        mock_rates = {
            'USD': {'EUR': 0.92, 'GBP': 0.79, 'INR': 83.0, 'LKR': 325.0},
            'EUR': {'USD': 1.09, 'GBP': 0.86, 'INR': 90.0, 'LKR': 353.0},
            'GBP': {'USD': 1.27, 'EUR': 1.16, 'INR': 105.0, 'LKR': 411.0},
            'INR': {'USD': 0.012, 'EUR': 0.011, 'GBP': 0.0095, 'LKR': 3.9},
            'LKR': {'USD': 0.0031, 'EUR': 0.0028, 'GBP': 0.0024, 'INR': 0.26}
        }
        
        if from_currency == to_currency:
            rate = 1.0
        elif from_currency in mock_rates and to_currency in mock_rates[from_currency]:
            rate = mock_rates[from_currency][to_currency]
        elif to_currency in mock_rates and from_currency in mock_rates[to_currency]:
            rate = 1 / mock_rates[to_currency][from_currency]
        else:
            rate = 1.0  # Default if currency not in mock rates
        
        converted = amount * rate
        
        return {
            'original_amount': amount,
            'converted_amount': round(converted, 2),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': round(rate, 4),
            'symbol': self._get_symbol(to_currency)
        }

