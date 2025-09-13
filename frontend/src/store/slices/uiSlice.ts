import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ThemeMode, Language } from '@types/common';

interface UiState {
  // Theme and appearance
  themeMode: ThemeMode;
  language: Language;
  
  // Navigation
  sidebarOpen: boolean;
  currentPage: string;
  
  // Loading states
  globalLoading: boolean;
  loadingMessage: string;
  
  // Notifications
  notifications: Notification[];
  
  // Modals and dialogs
  activeModal: string | null;
  modalData: any;
  
  // Map state
  mapLoaded: boolean;
  mapError: string | null;
  
  // Mobile responsiveness
  isMobile: boolean;
  screenSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}

const initialState: UiState = {
  themeMode: 'light',
  language: 'es',
  
  sidebarOpen: true,
  currentPage: '/',
  
  globalLoading: false,
  loadingMessage: '',
  
  notifications: [],
  
  activeModal: null,
  modalData: null,
  
  mapLoaded: false,
  mapError: null,
  
  isMobile: window.innerWidth < 768,
  screenSize: 'md',
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Theme and appearance
    setThemeMode: (state, action: PayloadAction<ThemeMode>) => {
      state.themeMode = action.payload;
      localStorage.setItem('themeMode', action.payload);
    },
    
    setLanguage: (state, action: PayloadAction<Language>) => {
      state.language = action.payload;
      localStorage.setItem('language', action.payload);
    },
    
    // Navigation
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    setCurrentPage: (state, action: PayloadAction<string>) => {
      state.currentPage = action.payload;
    },
    
    // Loading states
    setGlobalLoading: (state, action: PayloadAction<{ loading: boolean; message?: string }>) => {
      state.globalLoading = action.payload.loading;
      state.loadingMessage = action.payload.message || '';
    },
    
    // Notifications
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp' | 'read'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date(),
        read: false,
      };
      state.notifications.unshift(notification);
      
      // Keep only last 50 notifications
      if (state.notifications.length > 50) {
        state.notifications = state.notifications.slice(0, 50);
      }
    },
    
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    
    markAllNotificationsAsRead: (state) => {
      state.notifications.forEach(n => n.read = true);
    },
    
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    // Modals and dialogs
    openModal: (state, action: PayloadAction<{ modal: string; data?: any }>) => {
      state.activeModal = action.payload.modal;
      state.modalData = action.payload.data || null;
    },
    
    closeModal: (state) => {
      state.activeModal = null;
      state.modalData = null;
    },
    
    // Map state
    setMapLoaded: (state, action: PayloadAction<boolean>) => {
      state.mapLoaded = action.payload;
    },
    
    setMapError: (state, action: PayloadAction<string | null>) => {
      state.mapError = action.payload;
    },
    
    // Mobile responsiveness
    setIsMobile: (state, action: PayloadAction<boolean>) => {
      state.isMobile = action.payload;
    },
    
    setScreenSize: (state, action: PayloadAction<'xs' | 'sm' | 'md' | 'lg' | 'xl'>) => {
      state.screenSize = action.payload;
    },
  },
});

export const {
  setThemeMode,
  setLanguage,
  setSidebarOpen,
  toggleSidebar,
  setCurrentPage,
  setGlobalLoading,
  addNotification,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  removeNotification,
  clearNotifications,
  openModal,
  closeModal,
  setMapLoaded,
  setMapError,
  setIsMobile,
  setScreenSize,
} = uiSlice.actions;

export default uiSlice.reducer;