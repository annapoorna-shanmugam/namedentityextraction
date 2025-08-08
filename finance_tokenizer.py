import re
from typing import List

class FinanceTokenizer:
    def __init__(self):
        self.finance_abbreviations = {
            'usd': 'us dollar',
            'eur': 'euro',
            'gbp': 'british pound',
            'inr': 'indian rupee',
            'llc': 'limited liability company',
            'ltd': 'limited',
            'inc': 'incorporated',
            'ipo': 'initial public offering',
            'txn': 'transaction',
            'acct': 'account',
        }
        self.finance_compounds = [
            'bank account', 'current account', 'savings account', 'stock market',
            'public offering', 'initial public offering', 'exchange rate', 'interest rate',
            'credit card', 'debit card', 'financial year', 'balance sheet', 'income statement',
            'cash flow', 'shareholder value', 'market cap', 'merger deal', 'acquisition deal'
        ]

    def custom_tokenize(self, text: str) -> List[str]:
        text = text.lower()
        for abbr, full in self.finance_abbreviations.items():
            text = re.sub(r'\b' + abbr + r'\b', full, text)
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        enhanced_tokens = []
        i = 0
        while i < len(tokens):
            current_token = tokens[i]
            if i < len(tokens) - 1:
                bigram = current_token + ' ' + tokens[i + 1]
                if bigram in self.finance_compounds:
                    enhanced_tokens.append(bigram)
                    i += 2
                    continue
            if i < len(tokens) - 2:
                trigram = current_token + ' ' + tokens[i + 1] + ' ' + tokens[i + 2]
                if trigram in self.finance_compounds:
                    enhanced_tokens.append(trigram)
                    i += 3
                    continue
            enhanced_tokens.append(current_token)
            i += 1
        return enhanced_tokens
