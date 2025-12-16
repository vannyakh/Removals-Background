import { useState, useRef, useEffect } from 'react';

interface ToolbarProps {
  bgColor: string;
  onBgColorChange: (color: string) => void;
  onDownload: () => void;
  hasResult: boolean;
  resultImage: string | null;
}

export const Toolbar = ({
  bgColor,
  onBgColorChange,
  onDownload,
  hasResult,
  resultImage,
}: ToolbarProps) => {
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const downloadMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (downloadMenuRef.current && !downloadMenuRef.current.contains(event.target as Node)) {
        setShowDownloadMenu(false);
      }
    };

    if (showDownloadMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showDownloadMenu]);

  const handleCopy = async () => {
    if (resultImage) {
      try {
        const response = await fetch(resultImage);
        const blob = await response.blob();
        await navigator.clipboard.write([
          new ClipboardItem({ [blob.type]: blob })
        ]);
        // You could show a toast notification here
      } catch (err) {
        console.error('Failed to copy image:', err);
      }
    }
  };

  const handleDownloadPNG = () => {
    onDownload();
    setShowDownloadMenu(false);
  };

  const handleDownloadJPG = () => {
    if (resultImage) {
      const link = document.createElement('a');
      link.href = resultImage;
      link.download = 'removed-background.jpg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setShowDownloadMenu(false);
    }
  };

  return (
    <div className="fixed top-0 left-0 right-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-900">
              Remove Image Background
            </h1>
            
            {hasResult && (
              <>
                <div className="h-6 w-px bg-gray-300"></div>
                
                {/* Action Icons */}
                <div className="flex items-center gap-3">
                  {/* Copy Icon */}
                  <button
                    onClick={handleCopy}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Copy image"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      />
                    </svg>
                  </button>

                  {/* Undo Icon */}
                  <button
                    className="p-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Undo"
                    disabled
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                      />
                    </svg>
                  </button>

                  {/* Redo Icon */}
                  <button
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors cursor-not-allowed"
                    title="Redo"
                    disabled
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6"
                      />
                    </svg>
                  </button>
                </div>

                <div className="h-6 w-px bg-gray-300"></div>

                {/* Background Preview Options */}
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-gray-700">
                    Preview Background:
                  </label>
                  <div className="flex gap-2 items-center">
                    {['transparent', 'white', 'black', 'custom'].map((bg) => (
                      <button
                        key={bg}
                        onClick={() => {
                          if (bg === 'transparent') {
                            onBgColorChange('transparent');
                          } else if (bg === 'white') {
                            onBgColorChange('#ffffff');
                          } else if (bg === 'black') {
                            onBgColorChange('#000000');
                          }
                        }}
                        className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-colors ${
                          (bg === 'transparent' && bgColor === 'transparent') ||
                          (bg === 'white' && bgColor === '#ffffff') ||
                          (bg === 'black' && bgColor === '#000000')
                            ? 'bg-primary-100 border-primary-500 text-primary-700'
                            : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400'
                        }`}
                      >
                        {bg.charAt(0).toUpperCase() + bg.slice(1)}
                      </button>
                    ))}
                    <input
                      type="color"
                      value={bgColor === 'transparent' ? '#ffffff' : bgColor}
                      onChange={(e) => onBgColorChange(e.target.value)}
                      className="w-10 h-10 rounded border border-gray-300 cursor-pointer"
                    />
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Download Button with Dropdown */}
          {hasResult && (
            <div className="relative" ref={downloadMenuRef}>
              <button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="btn-primary text-sm py-2 px-4 flex items-center gap-2"
              >
                <span>Download</span>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {showDownloadMenu && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <button
                    onClick={handleDownloadPNG}
                    className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    Download as PNG
                  </button>
                  <button
                    onClick={handleDownloadJPG}
                    className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    Download as JPG
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
