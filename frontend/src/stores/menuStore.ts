import { create } from 'zustand';
import type { Menu } from '@/types';
import { menuApi } from '@/lib/api';

interface MenuState {
  menus: Menu[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchMenus: () => Promise<void>;
  setMenus: (menus: Menu[]) => void;
  clearError: () => void;
}

export const useMenuStore = create<MenuState>()((set) => ({
  menus: [],
  isLoading: false,
  error: null,

  fetchMenus: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await menuApi.getMenuTree();
      set({ menus: response.menus, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : '메뉴를 불러오는데 실패했습니다.';
      set({ error: message, isLoading: false });
    }
  },

  setMenus: (menus: Menu[]) => {
    set({ menus });
  },

  clearError: () => set({ error: null }),
}));
