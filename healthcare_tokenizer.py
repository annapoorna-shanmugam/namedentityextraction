import re
import json
from typing import List, Dict, Tuple

class HealthcareTokenizer:
    def __init__(self, config_path: str = 'config/extraction_rules.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.medical_abbreviations = {
            'mg': 'milligrams',
            'ml': 'milliliters',
            'bp': 'blood pressure',
            'hr': 'heart rate',
            'temp': 'temperature',
            'wbc': 'white blood cell',
            'rbc': 'red blood cell',
            'ecg': 'electrocardiogram',
            'mri': 'magnetic resonance imaging',
            'ct': 'computed tomography'
        }
        
        self.dose_patterns = [
            r'\d+\s*mg',
            r'\d+\s*ml',
            r'\d+\s*tablets?',
            r'\d+\s*capsules?',
            r'\d+\s*times?\s+daily',
            r'twice\s+daily',
            r'once\s+daily'
        ]
    
    def custom_tokenize(self, text: str) -> List[str]:
        text = text.lower()
        
        for abbr, full in self.medical_abbreviations.items():
            text = re.sub(r'\b' + abbr + r'\b', full, text)
        
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        
        enhanced_tokens = []
        i = 0
        while i < len(tokens):
            current_token = tokens[i]
            
            if i < len(tokens) - 1:
                bigram = current_token + ' ' + tokens[i + 1]
                if self._is_medical_compound(bigram):
                    enhanced_tokens.append(bigram)
                    i += 2
                    continue
            
            if i < len(tokens) - 2:
                trigram = current_token + ' ' + tokens[i + 1] + ' ' + tokens[i + 2]
                if self._is_medical_compound(trigram):
                    enhanced_tokens.append(trigram)
                    i += 3
                    continue
            
            enhanced_tokens.append(current_token)
            i += 1
        
        return enhanced_tokens
    
    def _is_medical_compound(self, phrase: str) -> bool:
        medical_compounds = [
            'heart disease', 'blood pressure', 'chest pain', 'shortness of breath',
            'abdominal pain', 'back pain', 'joint pain', 'ct scan', 'blood test',
            'heart rate', 'white blood cell', 'red blood cell'
        ]
        return phrase in medical_compounds
    
    def extract_dosage_info(self, text: str) -> List[Dict]:
        dosages = []
        for pattern in self.dose_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dosages.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'DOSAGE'
                })
        return dosages