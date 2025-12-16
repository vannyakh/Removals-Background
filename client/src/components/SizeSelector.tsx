interface SizeSelectorProps {
  size: string;
  onSizeChange: (size: string) => void;
}

export const SizeSelector = ({ size, onSizeChange }: SizeSelectorProps) => {
  return (
    <div className="mb-6">
      <label className="block mb-2 text-sm font-medium text-gray-700">
        Output Size
      </label>
      <div className="grid grid-cols-3 gap-2">
        {['preview', 'full', '50mp'].map((s) => (
          <button
            key={s}
            onClick={() => onSizeChange(s)}
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
  );
};

