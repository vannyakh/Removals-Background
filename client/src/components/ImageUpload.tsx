import { useRef } from 'react';
import { useDropZone } from './useDropZone';

type ImageSource = 'upload' | 'url' | 'base64';

interface ImageUploadProps {
  imageSource: ImageSource;
  onSourceChange: (source: ImageSource) => void;
  selectedFile: File | null;
  onFileSelect: (file: File) => void;
  imageUrl: string;
  onUrlChange: (url: string) => void;
  base64Image: string;
  onBase64Change: (base64: string) => void;
}

export const ImageUpload = ({
  imageSource,
  onSourceChange,
  selectedFile,
  onFileSelect,
  imageUrl,
  onUrlChange,
  base64Image,
  onBase64Change,
}: ImageUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { open, getInputProps } = useDropZone();

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  const handleDropZoneClick = () => {
    if (imageSource === 'upload') {
      open();
    } else {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Upload Image</h2>

      {/* Source Selection */}
      <div className="mb-6">
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => onSourceChange('upload')}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              imageSource === 'upload'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Upload File
          </button>
          <button
            onClick={() => onSourceChange('url')}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              imageSource === 'url'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            From URL
          </button>
          <button
            onClick={() => onSourceChange('base64')}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              imageSource === 'base64'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Base64
          </button>
        </div>
      </div>

      {/* Upload File */}
      {imageSource === 'upload' && (
        <div className="mb-6">
          <label className="block mb-2 text-sm font-medium text-gray-700">
            Select Image
          </label>
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 transition-colors"
            onClick={handleDropZoneClick}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInputChange}
              className="hidden"
            />
            <input {...getInputProps()} />
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="text-gray-600 mb-2">
              Click to upload or drag and drop
            </p>
            <p className="text-sm text-gray-500">
              PNG, JPG, WebP up to 22MB
            </p>
          </div>
          {selectedFile && (
            <p className="mt-2 text-sm text-gray-600">
              Selected: {selectedFile.name}
            </p>
          )}
        </div>
      )}

      {/* URL Input */}
      {imageSource === 'url' && (
        <div className="mb-6">
          <label className="block mb-2 text-sm font-medium text-gray-700">
            Image URL
          </label>
          <input
            type="url"
            value={imageUrl}
            onChange={(e) => onUrlChange(e.target.value)}
            placeholder="https://example.com/image.jpg"
            className="input-field"
          />
        </div>
      )}

      {/* Base64 Input */}
      {imageSource === 'base64' && (
        <div className="mb-6">
          <label className="block mb-2 text-sm font-medium text-gray-700">
            Base64 Encoded Image
          </label>
          <textarea
            value={base64Image}
            onChange={(e) => onBase64Change(e.target.value)}
            placeholder="data:image/jpeg;base64,..."
            rows={6}
            className="input-field font-mono text-sm"
          />
        </div>
      )}
    </div>
  );
};

