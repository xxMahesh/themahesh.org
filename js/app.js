// Using localStorage for storage since we can't use a backend with GitHub Pages
const STORAGE_KEY = 'sharenotes';

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function saveToStorage(note) {
    const notes = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    notes[note.id] = note;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
}

function getFromStorage(id) {
    const notes = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    return notes[id];
}

function showMessage(message, isError = false) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.style.backgroundColor = isError ? '#ff4444' : '#00C851';
    statusDiv.style.color = 'white';
    statusDiv.style.display = 'block';
    
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

function shareNote() {
    const content = document.getElementById('note-content').value;
    const title = document.getElementById('note-title').value;
    const tags = document.getElementById('note-tags').value;

    if (!content.trim()) {
        showMessage('Please write something before sharing!', true);
        return;
    }

    const noteId = generateId();
    const note = {
        id: noteId,
        content,
        title,
        tags,
        created: new Date().toISOString(),
        modified: new Date().toISOString()
    };

    saveToStorage(note);

    // Generate share URL
    const shareUrl = `${window.location.origin}?note=${noteId}`;
    document.getElementById('share-url').value = shareUrl;

    // Generate QR Code
    const qrContainer = document.getElementById('qr-code');
    qrContainer.innerHTML = '';
    new QRCode(qrContainer, shareUrl);

    // Show share modal
    document.getElementById('share-modal').style.display = 'flex';
}

function closeShareModal() {
    document.getElementById('share-modal').style.display = 'none';
}

function copyShareLink() {
    const shareUrl = document.getElementById('share-url');
    shareUrl.select();
    document.execCommand('copy');
    showMessage('Link copied to clipboard!');
}

// Load note if ID is in URL
window.addEventListener('load', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const noteId = urlParams.get('note');
    
    if (noteId) {
        const note = getFromStorage(noteId);
        if (note) {
            document.getElementById('note-title').value = note.title || '';
            document.getElementById('note-content').value = note.content || '';
            document.getElementById('note-tags').value = note.tags || '';
        }
    }
});

// Event listeners
document.getElementById('share-btn').addEventListener('click', shareNote);

// Function to save note to localStorage
function saveNote() {
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const tags = document.getElementById('note-tags').value;
    
    const note = {
        id: Date.now(), // Unique ID based on timestamp
        title: title,
        content: content,
        tags: tags,
        lastModified: new Date().toLocaleString()
    };

    // Get existing notes or initialize empty array
    let savedNotes = JSON.parse(localStorage.getItem('savedNotes') || '[]');
    savedNotes.push(note);
    
    // Save to localStorage
    try {
        localStorage.setItem('savedNotes', JSON.stringify(savedNotes));
        showMessage('Note saved successfully!');
    } catch (e) {
        showMessage('Error saving note: Storage might be full', true);
    }
}

// Function to load saved notes
function loadSavedNotes() {
    const savedNotes = JSON.parse(localStorage.getItem('savedNotes') || '[]');
    
    // Create dropdown for saved notes
    const notesList = document.createElement('select');
    notesList.className = 'form-control mb-3';
    notesList.id = 'saved-notes';
    
    // Add default option
    notesList.add(new Option('Select a saved note...', ''));
    
    // Add saved notes to dropdown
    savedNotes.forEach(note => {
        notesList.add(new Option(`${note.title || 'Untitled'} - ${note.lastModified}`, note.id));
    });
    
    // Add change event listener
    notesList.addEventListener('change', loadSelectedNote);
    
    // Insert dropdown before the title input
    const editorContainer = document.querySelector('.editor-container');
    editorContainer.insertBefore(notesList, editorContainer.firstChild);
}

// Function to load selected note
function loadSelectedNote(e) {
    const noteId = parseInt(e.target.value);
    if (!noteId) return;
    
    const savedNotes = JSON.parse(localStorage.getItem('savedNotes') || '[]');
    const note = savedNotes.find(n => n.id === noteId);
    
    if (note) {
        document.getElementById('note-title').value = note.title || '';
        document.getElementById('note-content').value = note.content || '';
        document.getElementById('note-tags').value = note.tags || '';
    }
}

// Load saved notes when page loads
window.addEventListener('load', loadSavedNotes);

// Add event listener for save button
document.getElementById('save-btn').addEventListener('click', saveNote);
