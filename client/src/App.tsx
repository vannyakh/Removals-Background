import { useState, useEffect } from 'react';
import { removeBackground } from './services/api';
import type { RemoveBgResponse, RemoveBgError, RemoveBgRequest } from './services/api';
import {
  DropZoneProvider,
  useDropZone,
  FullScreenDropZone,
  RecentImages,
  Toolbar,
} from './components';
import { saveRecentImage, getRecentImages, deleteRecentImage, type RecentImage } from './utils/localStorage';

function App() {
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bgColor, setBgColor] = useState('#ffffff');
  const [recentImages, setRecentImages] = useState<RecentImage[]>([]);
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null);

  // Load recent images on mount
  useEffect(() => {
    setRecentImages(getRecentImages());
  }, []);

  const convertFileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  const processImage = async (file: File) => {
    setLoading(true);
    setError(null);
    setResultImage(null);

    try {
      // Create preview first
      const originalDataUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          resolve(e.target?.result as string);
        };
        reader.readAsDataURL(file);
      });

      // Process image
      const base64 = await convertFileToBase64(file);
      const requestData: RemoveBgRequest = {
        image_file_b64: base64,
        size: 'preview',
      };

      const response: RemoveBgResponse = await removeBackground(requestData);
      
      // Convert base64 result to data URL
      const resultDataUrl = `data:image/png;base64,${response.data.result_b64}`;
      setResultImage(resultDataUrl);

      // Save to recent images
      saveRecentImage(originalDataUrl, resultDataUrl, file.name);
      const updated = getRecentImages();
      setRecentImages(updated);
      // Select the newly processed image
      if (updated.length > 0) {
        setSelectedImageId(updated[0].id);
      }
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

  const handleDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedImageId(null); // Clear selection when new image is dropped
      await processImage(acceptedFiles[0]);
    }
  };

  const handleSelectRecent = (image: RecentImage) => {
    setResultImage(image.result);
    setSelectedImageId(image.id);
    setError(null);
  };

  const handleAddClick = () => {
    // Trigger file input click
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (input) {
      input.click();
    }
  };

  const handleDeleteRecent = (id: string) => {
    deleteRecentImage(id);
    const updated = getRecentImages();
    setRecentImages(updated);
    // Clear selection if deleted image was selected
    if (selectedImageId === id) {
      setSelectedImageId(null);
      setResultImage(null);
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
    <DropZoneProvider onDrop={handleDrop}>
      <AppContent
        resultImage={resultImage}
        loading={loading}
        error={error}
        bgColor={bgColor}
        setBgColor={setBgColor}
        onDownload={handleDownload}
        recentImages={recentImages}
        onSelectRecent={handleSelectRecent}
        onDeleteRecent={handleDeleteRecent}
        selectedImageId={selectedImageId}
        onAddClick={handleAddClick}
      />
    </DropZoneProvider>
  );
}

function AppContent({
  resultImage,
  loading,
  error,
  bgColor,
  setBgColor,
  onDownload,
  recentImages,
  onSelectRecent,
  onDeleteRecent,
  selectedImageId,
  onAddClick,
}: {
  resultImage: string | null;
  loading: boolean;
  error: string | null;
  bgColor: string;
  setBgColor: (color: string) => void;
  onDownload: () => void;
  recentImages: RecentImage[];
  onSelectRecent: (image: RecentImage) => void;
  onDeleteRecent: (id: string) => void;
  selectedImageId: string | null;
  onAddClick: () => void;
}) {
  const { getRootProps, getInputProps } = useDropZone();

  return (
    <div
      {...getRootProps()}
      className="h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50 relative overflow-hidden"
    >
      <input {...getInputProps()} />
      <FullScreenDropZone />
      
      {/* Fixed Toolbar at Top */}
      <Toolbar
        bgColor={bgColor}
        onBgColorChange={setBgColor}
        onDownload={onDownload}
        hasResult={!!resultImage}
        resultImage={resultImage}
      />

      {/* Main Content Area - Full Height */}
      <div className="flex-1 flex items-center justify-center pt-16 pb-24 px-4 overflow-hidden">
        {loading ? (
          <div className="text-center">
            <svg
              className="animate-spin h-16 w-16 text-primary-600 mx-auto mb-4"
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
            <p className="text-gray-600 text-lg">Processing image...</p>
          </div>
        ) : resultImage ? (
          <div
            className="checkered-bg rounded-lg p-4 w-full h-full flex items-center justify-center"
            style={{
              background: bgColor !== 'transparent' ? bgColor : undefined,
            }}
          >
            <img
              src={resultImage}
              alt="Result"
              className="max-w-full max-h-full w-auto h-auto object-contain rounded-lg shadow-md"
            />
          </div>
        ) : (
          <div className="text-center text-gray-400 pointer-events-none">
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
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="text-xl mb-2">Drop image anywhere to process</p>
            <p className="text-sm">or click to select a file</p>
          </div>
        )}

        {error && (
          <div className="absolute top-20 left-1/2 transform -translate-x-1/2 p-4 bg-red-50 border border-red-200 rounded-lg z-50">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Fixed Recent Images at Bottom */}
      <div className="fixed bottom-0 left-0 right-0 z-30 bg-white border-t border-gray-200 shadow-lg">
        <div className="container mx-auto px-4 py-3">
          <RecentImages
            recentImages={recentImages}
            onSelect={onSelectRecent}
            onDelete={onDeleteRecent}
            selectedId={selectedImageId}
            onAddClick={onAddClick}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
