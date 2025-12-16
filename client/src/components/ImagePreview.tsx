interface ImagePreviewProps {
  originalImage: string | null;
  resultImage: string | null;
  onDownload: () => void;
  bgColor: string;
  onBgColorChange: (color: string) => void;
}

export const ImagePreview = ({
  originalImage,
  resultImage,
  onDownload,
  bgColor,
  onBgColorChange,
}: ImagePreviewProps) => {
  if (!resultImage) return null;

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Result</h3>
        <button
          onClick={onDownload}
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
                if (bg === 'transparent') {
                  onBgColorChange('transparent');
                } else if (bg === 'white') {
                  onBgColorChange('#ffffff');
                } else if (bg === 'black') {
                  onBgColorChange('#000000');
                }
              }}
              className={`px-4 py-2 rounded-lg border border-gray-300 hover:border-primary-500 transition-colors text-sm ${
                (bg === 'transparent' && bgColor === 'transparent') ||
                (bg === 'white' && bgColor === '#ffffff') ||
                (bg === 'black' && bgColor === '#000000')
                  ? 'bg-primary-100 border-primary-500'
                  : ''
              }`}
            >
              {bg.charAt(0).toUpperCase() + bg.slice(1)}
            </button>
          ))}
          <input
            type="color"
            value={bgColor === 'transparent' ? '#ffffff' : bgColor}
            onChange={(e) => onBgColorChange(e.target.value)}
            className="w-12 h-10 rounded border border-gray-300 cursor-pointer"
          />
        </div>
      </div>

      <div
        className="checkered-bg rounded-lg p-4 flex items-center justify-center"
        style={{
          background: bgColor !== 'transparent' ? bgColor : undefined,
        }}
      >
        <img
          src={resultImage}
          alt="Result"
          className="max-w-full max-h-[600px] h-auto rounded-lg shadow-md"
        />
      </div>
    </div>
  );
};

