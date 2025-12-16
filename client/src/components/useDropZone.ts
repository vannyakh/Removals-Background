import { useContext } from 'react';
import { DropZoneContext } from './DropZoneContext';

export const useDropZone = () => {
  const context = useContext(DropZoneContext);
  if (!context) {
    throw new Error('useDropZone must be used within DropZoneProvider');
  }
  return context;
};

