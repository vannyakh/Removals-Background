import { useDropZone } from './useDropZone';

export const FullScreenDropZone = () => {
  const { isDragActive, getRootProps } = useDropZone();

  if (!isDragActive) {
    return null;
  }

  return (
    <div
      {...getRootProps()}
      className="fixed inset-0 z-50 bg-primary-600 bg-opacity-90 backdrop-blur-sm flex items-center justify-center"
      style={{ pointerEvents: 'all' }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-center text-white">
        <svg
          className="mx-auto h-24 w-24 mb-6 animate-bounce"
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
        <h2 className="text-4xl font-bold mb-4">Drop image anywhere</h2>
        <p className="text-xl opacity-90">Release to upload and process</p>
      </div>
    </div>
  );
};

