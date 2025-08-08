import re
import json
from typing import List, Dict, Tuple
from datetime import datetime

class HealthcareEventExtractor:
    def __init__(self, config_path: str = 'config/extraction_rules.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.event_types = self.config['healthcare_events']
        
        self.date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}',
            r'yesterday|today|tomorrow',
            r'last\s+(week|month|year)',
            r'next\s+(week|month|year)'
        ]
        
        self.time_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm|AM|PM)?',
            r'morning|afternoon|evening|night'
        ]
    
    def extract_events(self, text: str, entities: List[Dict] = None) -> List[Dict]:
        events = []
        text_lower = text.lower()
        
        if entities is None:
            entities = []
        
        for event_type, event_config in self.event_types.items():
            triggers = event_config['triggers']
            attributes = event_config['attributes']
            
            for trigger in triggers:
                matches = list(re.finditer(r'\b' + trigger + r'\b', text_lower))
                
                for match in matches:
                    start, end = match.span()
                    event_text = text[start:end]
                    
                    event = {
                        'type': event_type,
                        'trigger': event_text,
                        'start': start,
                        'end': end,
                        'attributes': {},
                        'confidence': 0.7,
                        'context': self._extract_context(text, start, end)
                    }
                    
                    event['attributes'] = self._extract_event_attributes(
                        text, start, end, attributes, entities
                    )
                    
                    events.append(event)
        
        events.sort(key=lambda x: x['start'])
        return events
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _extract_event_attributes(self, text: str, start: int, end: int, 
                                attributes: List[str], entities: List[Dict]) -> Dict:
        extracted_attributes = {}
        
        context_window = 150
        context_start = max(0, start - context_window)
        context_end = min(len(text), end + context_window)
        context = text[context_start:context_end]
        
        for attr in attributes:
            if attr == 'date':
                date_info = self._extract_dates(context)
                if date_info:
                    extracted_attributes['date'] = date_info
            
            elif attr == 'time':
                time_info = self._extract_times(context)
                if time_info:
                    extracted_attributes['time'] = time_info
            
            elif attr == 'patient':
                patient_info = self._find_related_entities(entities, 'PATIENT', start, end)
                if patient_info:
                    extracted_attributes['patient'] = patient_info
            
            elif attr == 'medication':
                med_info = self._find_related_entities(entities, 'MEDICATION', start, end)
                if med_info:
                    extracted_attributes['medication'] = med_info
            
            elif attr == 'disease':
                disease_info = self._find_related_entities(entities, 'DISEASE', start, end)
                if disease_info:
                    extracted_attributes['disease'] = disease_info
            
            elif attr == 'treatment' or attr == 'procedure':
                treatment_info = self._find_related_entities(entities, 'TREATMENT', start, end)
                if treatment_info:
                    extracted_attributes[attr] = treatment_info
            
            elif attr == 'dosage':
                dosage_info = self._find_related_entities(entities, 'DOSAGE', start, end)
                if dosage_info:
                    extracted_attributes['dosage'] = dosage_info
            
            elif attr == 'hospital' or attr == 'location':
                location_info = self._extract_locations(context)
                if location_info:
                    extracted_attributes[attr] = location_info
        
        return extracted_attributes
    
    def _extract_dates(self, text: str) -> List[str]:
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return dates
    
    def _extract_times(self, text: str) -> List[str]:
        times = []
        for pattern in self.time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            times.extend(matches)
        return times
    
    def _find_related_entities(self, entities: List[Dict], entity_type: str, 
                             event_start: int, event_end: int, proximity: int = 200) -> List[str]:
        related = []
        for entity in entities:
            if entity['type'] == entity_type:
                distance = min(
                    abs(entity['start'] - event_end),
                    abs(entity['end'] - event_start)
                )
                if distance <= proximity:
                    related.append(entity['text'])
        return related
    
    def _extract_locations(self, text: str) -> List[str]:
        location_patterns = [
            r'\b\w+\s+hospital\b',
            r'\b\w+\s+medical\s+center\b',
            r'\b\w+\s+clinic\b',
            r'\bemergency\s+room\b',
            r'\ber\b',
            r'\bicu\b',
            r'\bintensive\s+care\s+unit\b'
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            locations.extend(matches)
        return locations
    
    def get_event_timeline(self, events: List[Dict]) -> List[Dict]:
        timeline = []
        for event in events:
            if 'date' in event['attributes']:
                timeline.append({
                    'event': event,
                    'date': event['attributes']['date'],
                    'type': event['type']
                })
        
        timeline.sort(key=lambda x: x.get('date', ''))
        return timeline
    
    def get_event_statistics(self, events: List[Dict]) -> Dict:
        stats = {}
        for event in events:
            event_type = event['type']
            if event_type not in stats:
                stats[event_type] = {'count': 0, 'events': []}
            stats[event_type]['count'] += 1
            stats[event_type]['events'].append(event['trigger'])
        
        return stats