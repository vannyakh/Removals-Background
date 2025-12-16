import { useState, useRef } from 'react';
import { removeBackground } from './services/api';
import type { RemoveBgResponse, RemoveBgError, RemoveBgRequest } from './services/api';

type ImageSource = 'upload' | 'url' | 'base64';

function App() {
  const [imageSource, setImageSource] = useState<ImageSource>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState('');
  const [base64Image, setBase64Image] = useState('');
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [size, setSize] = useState('preview');
  const [bgColor, setBgColor] = useState('#ffffff');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setOriginalImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const convertFileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  const handleProcess = async () => {
    setLoading(true);
    setError(null);
    setResultImage(null);

    try {
      const requestData: RemoveBgRequest = {
        size,
      };

      if (imageSource === 'upload' && selectedFile) {
        const base64 = await convertFileToBase64(selectedFile);
        requestData.image_file_b64 = base64;
      } else if (imageSource === 'url' && imageUrl) {
        requestData.image_url = imageUrl;
      } else if (imageSource === 'base64' && base64Image) {
        requestData.image_file_b64 = base64Image;
      } else {
        setError('Please provide an image');
        setLoading(false);
        return;
      }

      const response: RemoveBgResponse = await removeBackground(requestData);
      
      // Convert base64 result to data URL
      const resultDataUrl = `data:image/png;base64,${response.data.result_b64}`;
      setResultImage(resultDataUrl);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: RemoveBgError } };
        if (axiosError.response?.data?.errors) {
          const errorData = axiosError.response.data;
          setError(errorData.errors[0]?.title || 'An error occurred');
        } else {
          setError('Failed to process image');
        }
      } else if (err instanceof Error) {
        setError(err.message || 'Failed to process image');
      } else {
        setError('Failed to process image');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setImageUrl('');
    setBase64Image('');
    setOriginalImage(null);
    setResultImage(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDownload = () => {
    if (resultImage) {
      const link = document.createElement('a');
      link.href = resultImage;
      link.download = 'removed-background.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Remove Image Background
          </h1>
          <p className="text-xl text-gray-600">
            100% Automatically and <span className="font-bold text-primary-600">Free</span>
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Side - Upload/Input */}
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-semibold mb-6 text-gray-800">Upload Image</h2>
              
              {/* Source Selection */}
              <div className="mb-6">
                <div className="flex gap-2 mb-4">
                  <button
                    onClick={() => setImageSource('upload')}
                    className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                      imageSource === 'upload'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Upload File
                  </button>
                  <button
                    onClick={() => setImageSource('url')}
                    className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                      imageSource === 'url'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    From URL
                  </button>
                  <button
                    onClick={() => setImageSource('base64')}
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
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
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
                    onChange={(e) => {
                      setImageUrl(e.target.value);
                      if (e.target.value) {
                        setOriginalImage(e.target.value);
                      }
                    }}
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
                    onChange={(e) => setBase64Image(e.target.value)}
                    placeholder="data:image/jpeg;base64,..."
                    rows={6}
                    className="input-field font-mono text-sm"
                  />
                </div>
              )}

              {/* Size Selection */}
              <div className="mb-6">
                <label className="block mb-2 text-sm font-medium text-gray-700">
                  Output Size
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {['preview', 'full', '50mp'].map((s) => (
                    <button
                      key={s}
                      onClick={() => setSize(s)}
                      className={`py-2 px-4 rounded-lg font-medium transition-colors ${
                        size === s
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  onClick={handleProcess}
                  disabled={loading}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg
                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    'Remove Background'
                  )}
                </button>
                {(originalImage || resultImage) && (
                  <button onClick={handleReset} className="btn-secondary">
                    Reset
                  </button>
                )}
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Side - Preview/Result */}
          <div className="space-y-6">
            {/* Original Image */}
            {originalImage && (
              <div className="card">
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Original</h3>
                <div className="checkered-bg rounded-lg p-4">
                  <img
                    src={originalImage}
                    alt="Original"
                    className="max-w-full h-auto rounded-lg shadow-md"
                  />
                </div>
              </div>
            )}

            {/* Result Image */}
            {resultImage && (
              <div className="card">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Result</h3>
                  <button
                    onClick={handleDownload}
                    className="btn-primary text-sm py-2 px-4"
                  >
                    Download
                  </button>
                </div>
                
                {/* Background Preview Options */}
                <div className="mb-4">
                  <label className="block mb-2 text-sm font-medium text-gray-700">
                    Preview Background
                  </label>
                  <div className="flex gap-2 flex-wrap">
                    {['transparent', 'white', 'black', 'custom'].map((bg) => (
                      <button
                        key={bg}
                        onClick={() => {
                          if (bg === 'custom') {
                            // Toggle custom color picker
                          }
                        }}
                        className="px-4 py-2 rounded-lg border border-gray-300 hover:border-primary-500 transition-colors text-sm"
                      >
                        {bg.charAt(0).toUpperCase() + bg.slice(1)}
                      </button>
                    ))}
                    <input
                      type="color"
                      value={bgColor}
                      onChange={(e) => setBgColor(e.target.value)}
                      className="w-12 h-10 rounded border border-gray-300 cursor-pointer"
                    />
                  </div>
                </div>

                <div
                  className="checkered-bg rounded-lg p-4"
                  style={{
                    background: bgColor !== 'transparent' ? bgColor : undefined,
                  }}
                >
                  <img
                    src={resultImage}
                    alt="Result"
                    className="max-w-full h-auto rounded-lg shadow-md"
                  />
                </div>
              </div>
            )}

            {/* Placeholder */}
            {!originalImage && !resultImage && (
              <div className="card">
                <div className="text-center py-16 text-gray-400">
                  <svg
                    className="mx-auto h-24 w-24 mb-4 opacity-50"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <p className="text-lg">Upload an image to see the result</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
