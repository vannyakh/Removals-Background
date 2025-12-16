export interface RecentImage {
  id: string;
  original: string; // base64 data URL
  result: string; // base64 data URL
  timestamp: number;
  fileName?: string;
}

const STORAGE_KEY = 'backgroundRemoval_recentImages';
const MAX_RECENT = 10;

export const saveRecentImage = (original: string, result: string, fileName?: string): void => {
  try {
    const recentImages = getRecentImages();
    const newImage: RecentImage = {
      id: Date.now().toString(),
      original,
      result,
      timestamp: Date.now(),
      fileName,
    };

    // Add to beginning and limit to MAX_RECENT
    const updated = [newImage, ...recentImages].slice(0, MAX_RECENT);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('Failed to save recent image:', error);
  }
};

export const getRecentImages = (): RecentImage[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    return JSON.parse(stored) as RecentImage[];
  } catch (error) {
    console.error('Failed to load recent images:', error);
    return [];
  }
};

export const deleteRecentImage = (id: string): void => {
  try {
    const recentImages = getRecentImages();
    const updated = recentImages.filter((img) => img.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('Failed to delete recent image:', error);
  }
};

export const clearRecentImages = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear recent images:', error);
  }
};

