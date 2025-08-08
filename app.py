from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import csv
import io
from entity_extractor import HealthcareEntityExtractor
from event_extractor import HealthcareEventExtractor

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

entity_extractor = HealthcareEntityExtractor()
event_extractor = HealthcareEventExtractor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_entities_and_events():
    try:
        data = request.get_json()
        text = data.get('text', '')
        selected_entities = data.get('entity_types', [])
        min_confidence = data.get('min_confidence', 0.5)
        domain = data.get('domain', 'healthcare')

        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400

        # Pass domain to entity extractor if supported, else use logic to select config
        entities = entity_extractor.extract_entities(text, selected_entities, domain=domain) if 'domain' in entity_extractor.extract_entities.__code__.co_varnames else entity_extractor.extract_entities(text, selected_entities)
        entities = entity_extractor.filter_entities_by_confidence(entities, min_confidence)
        events = event_extractor.extract_events(text, entities)
        entity_stats = entity_extractor.get_entity_statistics(entities)
        event_stats = event_extractor.get_event_statistics(events)
        response = {
            'entities': entities,
            'events': events,
            'statistics': {
                'entities': entity_stats,
                'events': event_stats,
                'total_entities': len(entities),
                'total_events': len(events)
            },
            'processed_text': text
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not file.filename.endswith(('.txt', '.csv')):
            return jsonify({'error': 'Only .txt and .csv files are supported'}), 400
        content = file.read().decode('utf-8')
        selected_entities = request.form.getlist('entity_types')
        min_confidence = float(request.form.get('min_confidence', 0.5))
        domain = request.form.get('domain', 'healthcare')
        entities = entity_extractor.extract_entities(content, selected_entities, domain=domain) if 'domain' in entity_extractor.extract_entities.__code__.co_varnames else entity_extractor.extract_entities(content, selected_entities)
        entities = entity_extractor.filter_entities_by_confidence(entities, min_confidence)
        events = event_extractor.extract_events(content, entities)
        entity_stats = entity_extractor.get_entity_statistics(entities)
        event_stats = event_extractor.get_event_statistics(events)
        response = {
            'entities': entities,
            'events': events,
            'statistics': {
                'entities': entity_stats,
                'events': event_stats,
                'total_entities': len(entities),
                'total_events': len(events)
            },
            'processed_text': content,
            'filename': file.filename
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format_type>', methods=['POST'])
def export_results(format_type):
    try:
        data = request.get_json()
        entities = data.get('entities', [])
        events = data.get('events', [])
        
        if format_type == 'json':
            export_data = {
                'entities': entities,
                'events': events,
                'exported_at': datetime.now().isoformat()
            }
            
            output = io.StringIO()
            json.dump(export_data, output, indent=2)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'healthcare_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(['Type', 'Category', 'Text', 'Start', 'End', 'Confidence', 'Attributes'])
            
            for entity in entities:
                writer.writerow([
                    'Entity',
                    entity.get('type', ''),
                    entity.get('text', ''),
                    entity.get('start', ''),
                    entity.get('end', ''),
                    entity.get('confidence', ''),
                    ''
                ])
            
            for event in events:
                writer.writerow([
                    'Event',
                    event.get('type', ''),
                    event.get('trigger', ''),
                    event.get('start', ''),
                    event.get('end', ''),
                    event.get('confidence', ''),
                    json.dumps(event.get('attributes', {}))
                ])
            
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'healthcare_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# New endpoint to get available domains
@app.route('/api/domains')
def get_domains():
    with open('config/extraction_rules.json', 'r') as f:
        config = json.load(f)
    domains = []
    for key in config.keys():
        if key.endswith('_entities'):
            domains.append(key.replace('_entities', ''))
    return jsonify({'domains': domains})

# Updated endpoint to get entity types for a domain
@app.route('/api/entity-types')
def get_entity_types():
    domain = request.args.get('domain', 'healthcare')
    with open('config/extraction_rules.json', 'r') as f:
        config = json.load(f)
    key = f"{domain}_entities"
    entity_types = list(config.get(key, {}).keys())
    return jsonify({'entity_types': entity_types})

@app.route('/api/sample-data')
def get_sample_data():
    sample_texts = [
        "Patient John Doe was admitted to General Hospital on March 15, 2024, with complaints of chest pain and shortness of breath. He was diagnosed with acute myocardial infarction and started on aspirin 81mg daily and metoprolol 25mg twice daily. Blood tests showed elevated troponin levels. The patient underwent cardiac catheterization and was discharged on March 20, 2024, with instructions for follow-up in cardiology clinic.",
        
        "Mrs. Sarah Johnson, a 65-year-old female, presented to the emergency room with severe abdominal pain. CT scan revealed appendicitis. She underwent emergency appendectomy on April 3, 2024. Post-operative recovery was uncomplicated. She was prescribed ibuprofen 400mg for pain management and discharged home the following day.",
        
        "The patient was diagnosed with Type 2 diabetes mellitus during routine screening. HbA1c was 8.2%. Started on metformin 500mg twice daily. Patient education on diet and exercise was provided. Follow-up appointment scheduled in 3 months to monitor blood glucose levels and medication effectiveness."
    ]
    
    return jsonify({'sample_texts': sample_texts})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)