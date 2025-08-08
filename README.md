# Healthcare Named Entity and Event Extraction System

## Overview

This web-based application demonstrates the process of named entity recognition and event extraction within the healthcare domain. The system identifies and extracts healthcare-specific named entities and events using configurable extraction rules tailored to medical terminology.

## Features

### Web Interface
- **Intuitive Interface**: Clean, responsive design using HTML, CSS, and JavaScript
- **Multiple Input Methods**: 
  - Direct text input
  - File upload (supports .txt and .csv files)
  - Pre-loaded sample healthcare data
- **Entity Type Selection**: Choose specific healthcare entity types for extraction
- **Real-time Processing**: Interactive extraction with confidence scoring
- **Results Visualization**: Color-coded highlighting of entities and events

### Healthcare Domain Extraction
- **Named Entity Recognition**: Extracts 6 main entity types:
  - **PATIENT**: Patient names and references
  - **MEDICATION**: Drugs, dosages, and pharmaceutical information
  - **DISEASE**: Medical conditions and diagnoses
  - **TREATMENT**: Medical procedures and treatments
  - **SYMPTOM**: Clinical symptoms and manifestations
  - **BODY_PART**: Anatomical references
  - **DOSAGE**: Medication dosages and administration details

- **Event Extraction**: Identifies 6 healthcare event types:
  - **ADMISSION**: Hospital admissions
  - **DISCHARGE**: Patient discharges
  - **DIAGNOSIS**: Medical diagnoses
  - **PRESCRIPTION**: Medication prescriptions
  - **SURGERY**: Surgical procedures
  - **TEST_RESULT**: Laboratory and diagnostic test results

### Advanced Features
- **Custom Tokenization**: Domain-specific tokenization for medical terminology
- **Configurable Rules**: JSON-based configuration for extraction patterns
- **Confidence Scoring**: Adjustable confidence thresholds for extraction quality
- **Filtering and Search**: Filter results by entity/event types and search terms
- **Export Functionality**: Export results in JSON or CSV formats
- **Statistical Analysis**: Comprehensive statistics on extracted entities and events

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone/Download the project**:
   ```bash
   cd healthcare_ner_system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   - Open your web browser and navigate to: `http://localhost:5000`

## Usage Instructions

### 1. Text Input Method
- Click on the "Text Input" tab
- Paste or type healthcare text in the textarea
- Select desired entity types from the checkboxes
- Adjust confidence threshold using the slider
- Click "Extract Entities & Events"

### 2. File Upload Method
- Click on the "File Upload" tab
- Choose a .txt or .csv file containing healthcare text
- Configure entity types and confidence as above
- Click "Extract Entities & Events"

### 3. Sample Data Method
- Click on the "Sample Data" tab
- Choose from pre-loaded healthcare texts
- The selected text will be loaded into the text input
- Proceed with extraction as normal

### 4. Viewing Results
- **Highlighted Text**: View original text with color-coded entity highlights
- **Entities Tab**: Detailed list of extracted entities with confidence scores
- **Events Tab**: Extracted events with attributes and context
- **Statistics Tab**: Summary statistics and counts

### 5. Filtering and Export
- Use filter boxes to search through results
- Filter by entity/event types using dropdown menus
- Export results in JSON or CSV format using export buttons

## Technical Architecture

### Backend (Flask)
- **app.py**: Main Flask application with REST API endpoints
- **entity_extractor.py**: Healthcare NER extraction logic
- **event_extractor.py**: Healthcare event extraction logic  
- **healthcare_tokenizer.py**: Custom tokenization for medical text

### Frontend
- **templates/index.html**: Main web interface
- **static/css/style.css**: Responsive styling and animations
- **static/js/script.js**: Interactive functionality and API communication

### Configuration
- **config/extraction_rules.json**: Configurable patterns and rules for entities and events

## Domain Selection Justification

### Why Healthcare?
Healthcare was chosen as the domain for this NER and event extraction system due to several compelling reasons:

1. **Rich Entity Diversity**: Healthcare texts contain diverse entity types (patients, medications, diseases, treatments, symptoms, body parts) that demonstrate the complexity of domain-specific NER.

2. **Critical Event Sequences**: Healthcare involves temporal events (admissions, diagnoses, treatments, discharges) that are essential for understanding patient care workflows.

3. **Specialized Terminology**: Medical texts include domain-specific terminology, abbreviations, and compound terms that require custom tokenization approaches.

4. **Real-world Impact**: Automated extraction from healthcare texts has practical applications in clinical decision support, medical research, and electronic health record processing.

5. **Regulatory Requirements**: Healthcare documentation follows specific formats and standards, making it ideal for rule-based extraction approaches.

### Healthcare Domain Challenges

1. **Medical Abbreviations**: Extensive use of acronyms (ECG, MRI, BP) requiring expansion and normalization
2. **Dosage Patterns**: Complex medication dosing patterns (e.g., "25mg twice daily", "400mg every 6 hours")
3. **Temporal References**: Various date and time formats in medical records
4. **Context Sensitivity**: Same terms can have different meanings in different contexts
5. **Compound Medical Terms**: Multi-word medical concepts (e.g., "acute myocardial infarction")

## Dataset Information

### Primary Dataset
The application includes custom-created sample healthcare data specifically designed for this demonstration:

**File**: `data/sample_healthcare_data.txt`

**Content**: Three realistic medical records covering:
1. Cardiovascular case (MI/heart attack)
2. Surgical case (appendectomy)  
3. Chronic disease management (heart failure)

**Characteristics**:
- Realistic medical terminology and workflow
- Diverse entity types across all categories
- Multiple event types with temporal sequences
- Various medical specialties represented

### Dataset Sources and Recreation

To recreate similar results, you can use:

1. **Medical Literature**: PubMed abstracts and medical case studies
   - Link: https://pubmed.ncbi.nlm.nih.gov/
   - Use: Search for case reports and clinical studies

2. **Clinical Text Corpora**: 
   - i2b2 NLP Research Data Sets: https://www.i2b2.org/NLP/DataSets/
   - MIMIC-III Clinical Database: https://mimic.physionet.org/

3. **Medical Education Resources**:
   - Medical case study databases from educational institutions
   - Clinical scenario examples from medical textbooks

**Note**: All sample data in this application is anonymized and created for educational purposes only.

## Design Choices and Implementation Details

### 1. Rule-Based Approach
**Choice**: Used pattern-matching and rule-based extraction instead of machine learning models
**Rationale**: 
- Provides interpretable and configurable results
- No training data requirements
- Easy to modify and extend rules
- Suitable for educational demonstration

### 2. Custom Tokenization
**Implementation**: Healthcare-specific tokenizer with medical abbreviation expansion
**Benefits**:
- Handles medical compound terms
- Expands common medical abbreviations
- Preserves dosage patterns as single tokens

### 3. Confidence Scoring
**Method**: Context-based confidence calculation using surrounding words
**Formula**: Base confidence + context boost from relevant keywords
**Purpose**: Allows filtering of low-quality extractions

### 4. Event-Entity Linking
**Approach**: Proximity-based linking of events to related entities
**Window**: 200-character context window for attribute extraction
**Benefit**: Provides rich event context and attributes

### 5. Web-Based Interface
**Technology Stack**: Flask + HTML/CSS/JavaScript
**Advantages**:
- Cross-platform accessibility
- Real-time interaction
- Easy deployment and sharing
- Responsive design for various devices

## Challenges Faced and Solutions

### 1. Challenge: Overlapping Entity Recognition
**Problem**: Multiple patterns matching the same text span
**Solution**: Implemented overlap resolution algorithm that prioritizes longer matches and higher confidence scores

### 2. Challenge: Context-Sensitive Extraction
**Problem**: Same terms having different meanings in different contexts
**Solution**: Added context-aware confidence scoring using surrounding keywords

### 3. Challenge: Complex Medical Terminology
**Problem**: Handling compound medical terms and abbreviations
**Solution**: Created custom tokenizer with medical abbreviation dictionary and compound term detection

### 4. Challenge: Event-Entity Association
**Problem**: Linking events to relevant entities
**Solution**: Implemented proximity-based attribute extraction with configurable window sizes

### 5. Challenge: Performance with Large Texts
**Problem**: Processing large medical documents efficiently
**Solution**: Optimized pattern matching algorithms and added progress indicators

## Future Enhancements

1. **Machine Learning Integration**: Add pre-trained biomedical NER models (BioBERT, ClinicalBERT)
2. **Advanced Event Extraction**: Implement temporal relationship extraction between events
3. **Multi-language Support**: Extend to support medical texts in other languages
4. **Database Integration**: Add persistent storage for extracted data
5. **API Enhancement**: RESTful API for programmatic access
6. **Visualization**: Add timeline views and relationship graphs
7. **Batch Processing**: Support for processing multiple files simultaneously

## File Structure
```
healthcare_ner_system/
├── app.py                          # Main Flask application
├── entity_extractor.py             # NER extraction logic
├── event_extractor.py              # Event extraction logic
├── healthcare_tokenizer.py         # Custom tokenization
├── requirements.txt                 # Python dependencies
├── README.md                        # This documentation
├── config/
│   └── extraction_rules.json       # Configurable extraction rules
├── data/
│   └── sample_healthcare_data.txt  # Sample healthcare dataset
├── static/
│   ├── css/
│   │   └── style.css               # Application styling
│   └── js/
│       └── script.js               # Frontend functionality
└── templates/
    └── index.html                  # Main web interface
```

## API Endpoints

- `GET /` - Main application interface
- `POST /api/extract` - Extract entities and events from text
- `POST /api/upload` - Upload and process files
- `POST /api/export/<format>` - Export results (JSON/CSV)
- `GET /api/entity-types` - Get available entity types
- `GET /api/sample-data` - Get sample healthcare texts

## License

This project is created for educational purposes as part of an NLP Applications assignment. The code is available for academic use and modification.

## Contact

For questions or issues with this application, please refer to the assignment guidelines or contact the course instructor.