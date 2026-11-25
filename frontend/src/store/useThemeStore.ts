import { create } from 'zustand';

type ThemeMode = 'dark' | 'light' | 'system';

interface ThemeState {
  mode: ThemeMode;
  effectiveTheme: 'dark' | 'light';
  setMode: (mode: ThemeMode) => void;
}

const getSystemTheme = (): 'dark' | 'light' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'dark';
};

const applyThemeToDocument = (theme: 'dark' | 'light') => {
  if (typeof document !== 'undefined') {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }
};

export const useThemeStore = create<ThemeState>((set, get) => {
  const initialMode: ThemeMode = (typeof localStorage !== 'undefined' && (localStorage.getItem('theme_mode') as ThemeMode)) || 'system';
  const effective = initialMode === 'system' ? getSystemTheme() : initialMode;
  applyThemeToDocument(effective);

  if (typeof window !== 'undefined' && window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (get().mode === 'system') {
        const newTheme = e.matches ? 'dark' : 'light';
        applyThemeToDocument(newTheme);
        set({ effectiveTheme: newTheme });
      }
    });
  }

  return {
    mode: initialMode,
    effectiveTheme: effective,
    setMode: (mode) => {
      const eff = mode === 'system' ? getSystemTheme() : mode;
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('theme_mode', mode);
      }
      applyThemeToDocument(eff);
      set({ mode, effectiveTheme: eff });
    },
  };
});
