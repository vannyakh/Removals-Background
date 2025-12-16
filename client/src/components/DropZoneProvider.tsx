import { useState } from 'react';
import type { ReactNode } from 'react';
import { useDropzone } from 'react-dropzone';
import type { DropzoneOptions } from 'react-dropzone';
import { DropZoneContext } from './DropZoneContext';

interface DropZoneProviderProps {
  children: ReactNode;
  onDrop: (acceptedFiles: File[]) => void;
  accept?: DropzoneOptions['accept'];
  maxSize?: number;
  multiple?: boolean;
}

export const DropZoneProvider = ({
  children,
  onDrop,
  accept = {
    'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
  },
  maxSize = 22 * 1024 * 1024, // 22MB
  multiple = false,
}: DropZoneProviderProps) => {
  const [acceptedFiles, setAcceptedFiles] = useState<File[]>([]);

  const handleDrop = (files: File[]) => {
    setAcceptedFiles(files);
    onDrop(files);
  };

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop: handleDrop,
    accept,
    maxSize,
    multiple,
    noClick: false, // Allow click to select files
    noKeyboard: true,
  });

  return (
    <DropZoneContext.Provider
      value={{
        isDragActive,
        open,
        getRootProps,
        getInputProps,
        acceptedFiles,
      }}
    >
      {children}
    </DropZoneContext.Provider>
  );
};

