import re
import json
from typing import List, Dict, Tuple
from healthcare_tokenizer import HealthcareTokenizer

class HealthcareEntityExtractor:
    def __init__(self, config_path: str = 'config/extraction_rules.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.tokenizer = HealthcareTokenizer(config_path)
        self.entity_types = self.config['healthcare_entities']
    
    def extract_entities(self, text: str, selected_types: List[str] = None) -> List[Dict]:
        if selected_types is None:
            selected_types = list(self.entity_types.keys())
        
        entities = []
        text_lower = text.lower()
        
        for entity_type in selected_types:
            if entity_type not in self.entity_types:
                continue
                
            patterns = self.entity_types[entity_type]['patterns']
            context_words = self.entity_types[entity_type].get('context_words', [])
            
            for pattern in patterns:
                matches = list(re.finditer(r'\b' + pattern + r'\b', text_lower, re.IGNORECASE))
                
                for match in matches:
                    start, end = match.span()
                    entity_text = text[start:end]
                    
                    confidence = self._calculate_confidence(text_lower, start, end, context_words)
                    
                    entities.append({
                        'text': entity_text,
                        'start': start,
                        'end': end,
                        'type': entity_type,
                        'confidence': confidence,
                        'pattern_matched': pattern
                    })
        
        dosages = self.tokenizer.extract_dosage_info(text)
        entities.extend(dosages)
        
        entities = self._remove_overlapping_entities(entities)
        entities.sort(key=lambda x: x['start'])
        
        return entities
    
    def _calculate_confidence(self, text: str, start: int, end: int, context_words: List[str]) -> float:
        base_confidence = 0.6
        
        context_window = 50
        context_start = max(0, start - context_window)
        context_end = min(len(text), end + context_window)
        context = text[context_start:context_end]
        
        context_boost = 0
        for word in context_words:
            if word.lower() in context:
                context_boost += 0.1
        
        final_confidence = min(1.0, base_confidence + context_boost)
        return round(final_confidence, 2)
    
    def _remove_overlapping_entities(self, entities: List[Dict]) -> List[Dict]:
        entities.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))
        
        filtered = []
        for entity in entities:
            overlapping = False
            for existing in filtered:
                if (entity['start'] < existing['end'] and entity['end'] > existing['start']):
                    overlapping = True
                    break
            
            if not overlapping:
                filtered.append(entity)
        
        return filtered
    
    def get_entity_statistics(self, entities: List[Dict]) -> Dict:
        stats = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in stats:
                stats[entity_type] = {'count': 0, 'entities': []}
            stats[entity_type]['count'] += 1
            stats[entity_type]['entities'].append(entity['text'])
        
        return stats
    
    def filter_entities_by_confidence(self, entities: List[Dict], min_confidence: float = 0.5) -> List[Dict]:
        return [entity for entity in entities if entity.get('confidence', 0) >= min_confidence]