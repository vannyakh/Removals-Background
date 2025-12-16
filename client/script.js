// API Configuration
const API_URL = 'http://localhost:8000';

// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const processingSection = document.getElementById('processingSection');
const resultSection = document.getElementById('resultSection');
const exampleSection = document.getElementById('exampleSection');
const errorSection = document.getElementById('errorSection');
const originalImage = document.getElementById('originalImage');
const resultImage = document.getElementById('resultImage');
const downloadBtn = document.getElementById('downloadBtn');
const newImageBtn = document.getElementById('newImageBtn');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const errorMessage = document.getElementById('errorMessage');
const bgOptions = document.querySelectorAll('.bg-option');
const customColorPicker = document.getElementById('customColorPicker');
const sampleItems = document.querySelectorAll('.sample-item');
const pasteUrlLink = document.getElementById('pasteUrlLink');

// State
let currentFile = null;
let resultBlob = null;
let originalImageData = null;

// Event Listeners
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadResult);
newImageBtn.addEventListener('click', resetApp);
tryAgainBtn.addEventListener('click', resetApp);

// Sample image click handlers
sampleItems.forEach(item => {
    item.addEventListener('click', () => {
        const sample = item.dataset.sample;
        loadSampleImage(sample);
    });
});

// Paste URL handler
pasteUrlLink.addEventListener('click', (e) => {
    e.preventDefault();
    const url = prompt('Enter image URL:');
    if (url) {
        loadImageFromUrl(url);
    }
});

// Drag and Drop on upload card
const uploadCard = document.querySelector('.upload-card');
uploadCard.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadCard.style.border = '2px dashed #3b82f6';
    uploadCard.style.background = '#eff6ff';
});

uploadCard.addEventListener('dragleave', () => {
    uploadCard.style.border = '';
    uploadCard.style.background = '';
});

uploadCard.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadCard.style.border = '';
    uploadCard.style.background = '';
    
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
        const resultWrapper = document.getElementById('resultWrapper');
        
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
        document.getElementById('resultWrapper').style.background = e.target.value;
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

// Load sample image
async function loadSampleImage(sample) {
    const sampleUrls = {
        woman: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&h=800&fit=crop',
        bear: 'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800&h=800&fit=crop',
        car: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=800&fit=crop',
        microphone: 'https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=800&h=800&fit=crop'
    };
    
    const url = sampleUrls[sample];
    if (url) {
        loadImageFromUrl(url);
    }
}

// Load image from URL
async function loadImageFromUrl(url) {
    try {
        showProcessing();
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load image');
        const blob = await response.blob();
        const file = new File([blob], 'image.jpg', { type: blob.type });
        handleFile(file);
    } catch (error) {
        showError('Failed to load image from URL. Please try a different URL.');
    }
}

// UI State Management
function showProcessing() {
    uploadSection.classList.add('d-none');
    processingSection.classList.remove('d-none');
    resultSection.classList.add('d-none');
    exampleSection.classList.add('d-none');
    errorSection.classList.add('d-none');
}

function showResult() {
    uploadSection.classList.add('d-none');
    processingSection.classList.add('d-none');
    resultSection.classList.remove('d-none');
    exampleSection.classList.add('d-none');
    errorSection.classList.add('d-none');
}

function showError(message) {
    errorMessage.textContent = message;
    uploadSection.classList.add('d-none');
    processingSection.classList.add('d-none');
    resultSection.classList.add('d-none');
    exampleSection.classList.add('d-none');
    errorSection.classList.remove('d-none');
}

function resetApp() {
    uploadSection.classList.remove('d-none');
    processingSection.classList.add('d-none');
    resultSection.classList.add('d-none');
    exampleSection.classList.remove('d-none');
    errorSection.classList.add('d-none');
    
    fileInput.value = '';
    currentFile = null;
    resultBlob = null;
    originalImageData = null;
    originalImage.src = '';
    resultImage.src = '';
    
    // Reset background to transparent
    bgOptions.forEach(opt => opt.classList.remove('active'));
    document.querySelector('[data-bg="transparent"]').classList.add('active');
    const resultWrapper = document.getElementById('resultWrapper');
    resultWrapper.classList.add('checkered-bg');
    resultWrapper.style.background = '';
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
        if (!data.model_loaded) {
            console.warn('Model is still loading...');
        }
    } catch (error) {
        console.error('API is not accessible:', error);
        // Don't show error on page load, just log it
    }
}

// Initialize
checkAPIStatus();

