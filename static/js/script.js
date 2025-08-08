let currentResults = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    await loadDomains();
    await loadEntityTypes();
    loadSampleTexts();
    setupEventListeners();
    updateConfidenceDisplay();
}

function setupEventListeners() {
    document.getElementById('extract-btn').addEventListener('click', extractEntitiesAndEvents);
    document.getElementById('export-json').addEventListener('click', () => exportResults('json'));
    document.getElementById('export-csv').addEventListener('click', () => exportResults('csv'));
    document.getElementById('file-input').addEventListener('change', handleFileUpload);
    document.getElementById('confidence-range').addEventListener('input', updateConfidenceDisplay);
    document.getElementById('entity-filter').addEventListener('input', filterEntities);
    document.getElementById('entity-type-filter').addEventListener('change', filterEntities);
    document.getElementById('event-filter').addEventListener('input', filterEvents);
    document.getElementById('event-type-filter').addEventListener('change', filterEvents);
    document.getElementById('domain-select').addEventListener('change', async function() {
        await loadEntityTypes();
    });
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName + '-tab').classList.add('active');
}

function switchResultTab(tabName) {
    document.querySelectorAll('.result-tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.result-tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName + '-tab').classList.add('active');
}

function updateConfidenceDisplay() {
    const slider = document.getElementById('confidence-range');
    const display = document.getElementById('confidence-value');
    display.textContent = slider.value;
}

async function loadDomains() {
    try {
        const response = await fetch('/api/domains');
        const data = await response.json();
        const domainSelect = document.getElementById('domain-select');
        domainSelect.innerHTML = '';
        data.domains.forEach(domain => {
            const option = document.createElement('option');
            option.value = domain;
            option.textContent = domain.charAt(0).toUpperCase() + domain.slice(1);
            domainSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading domains:', error);
    }
}

async function loadEntityTypes() {
    try {
        const domain = document.getElementById('domain-select').value || 'healthcare';
        const response = await fetch(`/api/entity-types?domain=${domain}`);
        const data = await response.json();
        const container = document.getElementById('entity-checkboxes');
        container.innerHTML = '';
        data.entity_types.forEach(type => {
            const div = document.createElement('div');
            div.className = 'checkbox-item';
            div.innerHTML = `
                <input type="checkbox" id="entity-${type}" value="${type}" checked>
                <label for="entity-${type}">${type}</label>
            `;
            container.appendChild(div);
        });
        populateEntityTypeFilters(data.entity_types);
    } catch (error) {
        console.error('Error loading entity types:', error);
    }
}

function populateEntityTypeFilters(types) {
    const entityFilter = document.getElementById('entity-type-filter');
    entityFilter.innerHTML = '<option value="">All Types</option>';
    
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        entityFilter.appendChild(option);
    });
}

async function loadSampleTexts() {
    try {
        const response = await fetch('/api/sample-data');
        const data = await response.json();
        
        const container = document.getElementById('sample-texts');
        container.innerHTML = '';
        
        data.sample_texts.forEach((text, index) => {
            const div = document.createElement('div');
            div.className = 'sample-text-item';
            div.onclick = () => selectSampleText(text);
            
            const preview = text.length > 150 ? text.substring(0, 150) + '...' : text;
            div.innerHTML = `
                <div class="sample-text-preview">${preview}</div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading sample texts:', error);
    }
}

function selectSampleText(text) {
    document.getElementById('input-text').value = text;
    switchTab('text');
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    const fileInfo = document.getElementById('file-info');
    
    if (file) {
        fileInfo.innerHTML = `
            <i class="fas fa-file"></i>
            Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)
        `;
    } else {
        fileInfo.innerHTML = '';
    }
}

async function extractEntitiesAndEvents() {
    const activeTab = document.querySelector('.tab-button.active').textContent.includes('Text') ? 'text' : 'file';
    let text = '';
    let selectedEntityTypes = [];
    let minConfidence = parseFloat(document.getElementById('confidence-range').value);
    const domain = document.getElementById('domain-select').value || 'healthcare';
    const checkboxes = document.querySelectorAll('#entity-checkboxes input[type="checkbox"]:checked');
    checkboxes.forEach(cb => selectedEntityTypes.push(cb.value));
    showLoading();
    try {
        if (activeTab === 'text') {
            text = document.getElementById('input-text').value.trim();
            if (!text) {
                alert('Please enter some text to analyze.');
                hideLoading();
                return;
            }
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    entity_types: selectedEntityTypes,
                    min_confidence: minConfidence,
                    domain: domain
                })
            });
            const data = await response.json();
            displayResults(data);
        } else {
            const fileInput = document.getElementById('file-input');
            if (!fileInput.files[0]) {
                alert('Please select a file to upload.');
                hideLoading();
                return;
            }
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            selectedEntityTypes.forEach(type => formData.append('entity_types', type));
            formData.append('min_confidence', minConfidence);
            formData.append('domain', domain);
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            displayResults(data);
        }
    } catch (error) {
        console.error('Error during extraction:', error);
        alert('An error occurred during extraction. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayResults(data) {
    currentResults = data;
    
    if (data.error) {
        alert('Error: ' + data.error);
        return;
    }
    
    displayHighlightedText(data.processed_text, data.entities, data.events);
    displayEntities(data.entities);
    displayEvents(data.events);
    displayStatistics(data.statistics);
    
    document.getElementById('export-json').disabled = false;
    document.getElementById('export-csv').disabled = false;
    
    populateEventTypeFilter(data.events);
}

function displayHighlightedText(text, entities, events) {
    const container = document.getElementById('highlighted-text');
    
    let annotatedText = text;
    let offset = 0;
    
    const allAnnotations = [
        ...entities.map(e => ({...e, type: 'entity'})),
        ...events.map(e => ({...e, type: 'event', text: e.trigger}))
    ].sort((a, b) => a.start - b.start);
    
    allAnnotations.forEach(annotation => {
        const start = annotation.start + offset;
        const end = annotation.end + offset;
        const currentText = annotatedText.substring(start, end);
        
        let highlightClass, tooltip;
        if (annotation.type === 'entity') {
            highlightClass = `entity-highlight entity-${annotation.type || annotation.entity_type}`;
            tooltip = `${annotation.type || annotation.entity_type} (${annotation.confidence || 'N/A'})`;
        } else {
            highlightClass = 'event-highlight';
            tooltip = `Event: ${annotation.event_type || annotation.type}`;
        }
        
        const highlightedSpan = `<span class="${highlightClass}" title="${tooltip}">${currentText}</span>`;
        
        annotatedText = annotatedText.substring(0, start) + highlightedSpan + annotatedText.substring(end);
        offset += highlightedSpan.length - currentText.length;
    });
    
    container.innerHTML = annotatedText;
}

function displayEntities(entities) {
    const container = document.getElementById('entities-list');
    container.innerHTML = '';
    
    if (entities.length === 0) {
        container.innerHTML = '<p>No entities found.</p>';
        return;
    }
    
    entities.forEach(entity => {
        const div = document.createElement('div');
        div.className = 'entity-item';
        div.innerHTML = `
            <div class="entity-header">
                <span class="entity-type">${entity.type}</span>
                <span class="confidence-score">${(entity.confidence || 0).toFixed(2)}</span>
            </div>
            <div class="entity-text">"${entity.text}"</div>
            <div class="entity-position">Position: ${entity.start}-${entity.end}</div>
            ${entity.pattern_matched ? `<div class="entity-pattern">Pattern: ${entity.pattern_matched}</div>` : ''}
        `;
        container.appendChild(div);
    });
}

function displayEvents(events) {
    const container = document.getElementById('events-list');
    container.innerHTML = '';
    
    if (events.length === 0) {
        container.innerHTML = '<p>No events found.</p>';
        return;
    }
    
    events.forEach(event => {
        const div = document.createElement('div');
        div.className = 'event-item';
        
        let attributesHtml = '';
        if (event.attributes && Object.keys(event.attributes).length > 0) {
            attributesHtml = '<div class="event-attributes">';
            for (const [key, value] of Object.entries(event.attributes)) {
                if (Array.isArray(value) && value.length > 0) {
                    attributesHtml += `
                        <div class="attribute-item">
                            <span class="attribute-label">${key}:</span>
                            <span>${value.join(', ')}</span>
                        </div>
                    `;
                } else if (value && !Array.isArray(value)) {
                    attributesHtml += `
                        <div class="attribute-item">
                            <span class="attribute-label">${key}:</span>
                            <span>${value}</span>
                        </div>
                    `;
                }
            }
            attributesHtml += '</div>';
        }
        
        div.innerHTML = `
            <div class="event-header">
                <span class="event-type">${event.type}</span>
                <span class="confidence-score">${(event.confidence || 0).toFixed(2)}</span>
            </div>
            <div class="event-trigger">"${event.trigger}"</div>
            <div class="event-position">Position: ${event.start}-${event.end}</div>
            ${attributesHtml}
        `;
        container.appendChild(div);
    });
}

function displayStatistics(stats) {
    const container = document.getElementById('statistics-content');
    container.innerHTML = '';
    
    const statisticsGrid = document.createElement('div');
    statisticsGrid.className = 'statistics-grid';
    
    if (stats.entities && Object.keys(stats.entities).length > 0) {
        const entityCard = document.createElement('div');
        entityCard.className = 'stat-card';
        entityCard.innerHTML = `
            <div class="stat-header">Entity Statistics</div>
            ${Object.entries(stats.entities).map(([type, data]) => `
                <div class="stat-item">
                    <span class="stat-label">${type}</span>
                    <span class="stat-count">${data.count}</span>
                </div>
            `).join('')}
            <div class="stat-item">
                <span class="stat-label"><strong>Total Entities</strong></span>
                <span class="stat-count">${stats.total_entities || 0}</span>
            </div>
        `;
        statisticsGrid.appendChild(entityCard);
    }
    
    if (stats.events && Object.keys(stats.events).length > 0) {
        const eventCard = document.createElement('div');
        eventCard.className = 'stat-card';
        eventCard.innerHTML = `
            <div class="stat-header">Event Statistics</div>
            ${Object.entries(stats.events).map(([type, data]) => `
                <div class="stat-item">
                    <span class="stat-label">${type}</span>
                    <span class="stat-count">${data.count}</span>
                </div>
            `).join('')}
            <div class="stat-item">
                <span class="stat-label"><strong>Total Events</strong></span>
                <span class="stat-count">${stats.total_events || 0}</span>
            </div>
        `;
        statisticsGrid.appendChild(eventCard);
    }
    
    container.appendChild(statisticsGrid);
}

function populateEventTypeFilter(events) {
    const eventFilter = document.getElementById('event-type-filter');
    eventFilter.innerHTML = '<option value="">All Types</option>';
    
    const eventTypes = [...new Set(events.map(event => event.type))];
    eventTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        eventFilter.appendChild(option);
    });
}

function filterEntities() {
    const searchTerm = document.getElementById('entity-filter').value.toLowerCase();
    const selectedType = document.getElementById('entity-type-filter').value;
    
    const entityItems = document.querySelectorAll('.entity-item');
    entityItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        const typeElement = item.querySelector('.entity-type');
        const entityType = typeElement ? typeElement.textContent : '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesType = !selectedType || entityType === selectedType;
        
        item.style.display = (matchesSearch && matchesType) ? 'block' : 'none';
    });
}

function filterEvents() {
    const searchTerm = document.getElementById('event-filter').value.toLowerCase();
    const selectedType = document.getElementById('event-type-filter').value;
    
    const eventItems = document.querySelectorAll('.event-item');
    eventItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        const typeElement = item.querySelector('.event-type');
        const eventType = typeElement ? typeElement.textContent : '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesType = !selectedType || eventType === selectedType;
        
        item.style.display = (matchesSearch && matchesType) ? 'block' : 'none';
    });
}

async function exportResults(format) {
    if (!currentResults) {
        alert('No results to export. Please run extraction first.');
        return;
    }
    
    try {
        const response = await fetch(`/api/export/${format}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                entities: currentResults.entities,
                events: currentResults.events
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `healthcare_extraction.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Export failed. Please try again.');
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Export failed. Please try again.');
    }
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}