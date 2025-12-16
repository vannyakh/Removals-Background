import { createContext } from 'react';
import type { DropzoneRootProps, DropzoneInputProps } from 'react-dropzone';

export interface DropZoneContextType {
  isDragActive: boolean;
  open: () => void;
  getRootProps: <T extends HTMLElement = HTMLDivElement>(props?: React.HTMLAttributes<T>) => DropzoneRootProps;
  getInputProps: () => DropzoneInputProps;
  acceptedFiles: File[];
}

export const DropZoneContext = createContext<DropZoneContextType | undefined>(undefined);

