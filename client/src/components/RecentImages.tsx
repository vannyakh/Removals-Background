import { useState, useRef, useEffect } from 'react';
import type { RecentImage } from '../utils/localStorage';

interface RecentImagesProps {
  recentImages: RecentImage[];
  onSelect: (image: RecentImage) => void;
  onDelete: (id: string) => void;
  selectedId?: string | null;
  onAddClick?: () => void;
}

export const RecentImages = ({
  recentImages,
  onSelect,
  onDelete,
  selectedId,
  onAddClick,
}: RecentImagesProps) => {
  const [contextMenu, setContextMenu] = useState<{
    id: string;
    x: number;
    y: number;
  } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setContextMenu(null);
      }
    };

    if (contextMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [contextMenu]);

  const handleContextMenu = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({ id, x: e.clientX, y: e.clientY });
  };

  const handleDelete = (id: string) => {
    onDelete(id);
    setContextMenu(null);
  };

  return (
    <div className="relative" ref={containerRef}>
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
        {/* Add Button */}
        {onAddClick && (
          <button
            onClick={onAddClick}
            className="flex-shrink-0 w-20 h-20 rounded-xl bg-gray-100 hover:bg-gray-200 border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500"
            title="Add new image"
          >
            <svg
              className="w-8 h-8 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </button>
        )}

        {/* Recent Images */}
        {recentImages.map((image) => (
          <div
            key={image.id}
            className="relative flex-shrink-0 group"
            onContextMenu={(e) => handleContextMenu(e, image.id)}
          >
            <button
              onClick={() => onSelect(image)}
              className={`relative w-20 h-20 rounded-xl overflow-hidden border-2 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                selectedId === image.id
                  ? 'border-blue-500 shadow-lg'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <img
                src={image.result}
                alt={image.fileName || 'Recent image'}
                className="w-full h-full object-cover"
              />
              {selectedId === image.id && (
                <div className="absolute top-1 right-1 w-5 h-5 bg-gray-800 bg-opacity-75 rounded-full flex items-center justify-center">
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 15l7-7 7 7"
                    />
                  </svg>
                </div>
              )}
            </button>
          </div>
        ))}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="fixed bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50 min-w-[180px]"
          style={{
            left: `${contextMenu.x}px`,
            top: `${contextMenu.y}px`,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => {
              // Report result functionality
              setContextMenu(null);
            }}
            className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center gap-3 transition-colors"
          >
            <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
              <span className="text-xs font-semibold text-gray-600">i</span>
            </div>
            <span>Report result</span>
          </button>
          <button
            onClick={() => handleDelete(contextMenu.id)}
            className="w-full px-4 py-2 text-left text-red-600 hover:bg-red-50 flex items-center gap-3 transition-colors"
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            <span>Delete</span>
          </button>
        </div>
      )}
    </div>
  );
};
