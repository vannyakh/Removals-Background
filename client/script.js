// API Configuration
const API_URL = 'http://localhost:8000';

// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const processingSection = document.getElementById('processingSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const originalImage = document.getElementById('originalImage');
const resultImage = document.getElementById('resultImage');
const downloadBtn = document.getElementById('downloadBtn');
const newImageBtn = document.getElementById('newImageBtn');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const errorMessage = document.getElementById('errorMessage');
const bgOptions = document.querySelectorAll('.bg-option');
const customColorPicker = document.getElementById('customColorPicker');

// State
let currentFile = null;
let resultBlob = null;
let originalImageData = null;

// Event Listeners
uploadBox.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadResult);
newImageBtn.addEventListener('click', resetApp);
tryAgainBtn.addEventListener('click', resetApp);

// Drag and Drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Background color options
bgOptions.forEach(option => {
    option.addEventListener('click', function() {
        bgOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');
        
        const bg = this.dataset.bg;
        const resultWrapper = resultImage.parentElement;
        
        // Remove all background classes
        resultWrapper.classList.remove('checkered-bg');
        resultWrapper.style.background = '';
        
        switch(bg) {
            case 'transparent':
                resultWrapper.classList.add('checkered-bg');
                break;
            case 'white':
                resultWrapper.style.background = 'white';
                break;
            case 'black':
                resultWrapper.style.background = 'black';
                break;
            case 'blue':
                resultWrapper.style.background = '#3b82f6';
                break;
            case 'green':
                resultWrapper.style.background = '#10b981';
                break;
            case 'custom':
                resultWrapper.style.background = customColorPicker.value;
                break;
        }
    });
});

customColorPicker.addEventListener('input', (e) => {
    const customOption = document.querySelector('[data-bg="custom"]');
    if (customOption.classList.contains('active')) {
        resultImage.parentElement.style.background = e.target.value;
    }
});

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB');
        return;
    }
    
    currentFile = file;
    
    // Show original image
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImageData = e.target.result;
        originalImage.src = originalImageData;
    };
    reader.readAsDataURL(file);
    
    // Process image
    processImage(file);
}

// Image Processing
async function processImage(file) {
    showProcessing();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_URL}/remove-background`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to process image');
        }
        
        const blob = await response.blob();
        resultBlob = blob;
        
        const imageUrl = URL.createObjectURL(blob);
        resultImage.src = imageUrl;
        
        showResult();
    } catch (error) {
        console.error('Error processing image:', error);
        showError(error.message || 'Failed to process image. Please try again.');
    }
}

// UI State Management
function showProcessing() {
    uploadSection.classList.add('hidden');
    processingSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

function showResult() {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultSection.classList.remove('hidden');
    errorSection.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
}

function resetApp() {
    uploadSection.classList.remove('hidden');
    processingSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    fileInput.value = '';
    currentFile = null;
    resultBlob = null;
    originalImageData = null;
    originalImage.src = '';
    resultImage.src = '';
    
    // Reset background to transparent
    bgOptions.forEach(opt => opt.classList.remove('active'));
    document.querySelector('[data-bg="transparent"]').classList.add('active');
    resultImage.parentElement.classList.add('checkered-bg');
    resultImage.parentElement.style.background = '';
}

// Download Result
function downloadResult() {
    if (!resultBlob) return;
    
    const url = URL.createObjectURL(resultBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `removed_bg_${currentFile.name.split('.')[0]}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Check API Status on Load
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/`);
        const data = await response.json();
        console.log('API Status:', data);
    } catch (error) {
        console.error('API is not accessible:', error);
        showError('Cannot connect to the backend server. Please make sure it is running on port 8000.');
    }
}

// Initialize
checkAPIStatus();

