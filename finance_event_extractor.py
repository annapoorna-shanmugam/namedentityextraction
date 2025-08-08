import re
import json
from typing import List, Dict

class FinanceEventExtractor:
    def __init__(self, config_path: str = 'config/extraction_rules.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.event_types = self.config['finance_events']

    def extract_events(self, text: str, entities: List[Dict]) -> List[Dict]:
        events = []
        text_lower = text.lower()
        for event_type, event_info in self.event_types.items():
            triggers = event_info.get('triggers', [])
            attributes = event_info.get('attributes', [])
            for trigger in triggers:
                for match in re.finditer(r'\b' + re.escape(trigger) + r'\b', text_lower, re.IGNORECASE):
                    start, end = match.span()
                    event = {
                        'type': event_type,
                        'trigger': text[start:end],
                        'start': start,
                        'end': end,
                        'confidence': 1.0,
                        'attributes': {}
                    }
                    # Simple attribute extraction: look for entities of attribute type nearby
                    for attr in attributes:
                        attr_values = [e['text'] for e in entities if e['type'].lower() == attr.lower() and abs(e['start'] - start) < 100]
                        if attr_values:
                            event['attributes'][attr] = attr_values
                    events.append(event)
        return events

    def get_event_statistics(self, events: List[Dict]) -> Dict:
        stats = {}
        for event in events:
            event_type = event['type']
            if event_type not in stats:
                stats[event_type] = {'count': 0, 'triggers': []}
            stats[event_type]['count'] += 1
            stats[event_type]['triggers'].append(event['trigger'])
        return stats
