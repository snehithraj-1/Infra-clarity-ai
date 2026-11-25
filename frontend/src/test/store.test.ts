import { describe, it, expect, beforeEach } from 'vitest';
import { useEnhanceStore } from '../store/useEnhanceStore';
import { DegradationReport, Severity } from '../types';

describe('useEnhanceStore - Planner Option State', () => {
  beforeEach(() => {
    useEnhanceStore.getState().reset();
  });

  it('initializes with default options and stages', () => {
    const state = useEnhanceStore.getState();
    expect(state.preset).toBe('Auto');
    expect(state.stages).toHaveLength(4);
    expect(state.outputFormat).toBe('png');
    expect(state.stripGps).toBe(true);
  });

  it('updates stages correctly when switching presets', () => {
    const store = useEnhanceStore.getState();

    // 1. Hazy / Rainy Weather preset
    store.setPreset('Hazy / Rainy Weather');
    let stages = useEnhanceStore.getState().stages;
    const dehaze = stages.find((s) => s.name === 'dehaze');
    expect(dehaze?.enabled).toBe(true);
    expect(dehaze?.strength).toBe(75);

    // 2. Pipeline Close-up preset (dehaze should be disabled, deblur 75%)
    store.setPreset('Pipeline Close-up');
    stages = useEnhanceStore.getState().stages;
    const closeUpDehaze = stages.find((s) => s.name === 'dehaze');
    const closeUpDeblur = stages.find((s) => s.name === 'deblur');
    expect(closeUpDehaze?.enabled).toBe(false);
    expect(closeUpDeblur?.enabled).toBe(true);
    expect(closeUpDeblur?.strength).toBe(75);

    // 3. Distant Tower preset (super-resolution enabled)
    store.setPreset('Distant Tower');
    stages = useEnhanceStore.getState().stages;
    const towerSuperres = stages.find((s) => s.name === 'super_resolution');
    expect(towerSuperres?.enabled).toBe(true);
    expect(towerSuperres?.strength).toBe(65);
  });

  it('allows manual toggling of individual stages and strength sliders', () => {
    const store = useEnhanceStore.getState();

    store.toggleStage('denoise', true);
    store.setStageStrength('denoise', 85);

    const stages = useEnhanceStore.getState().stages;
    const denoise = stages.find((s) => s.name === 'denoise');
    expect(denoise?.enabled).toBe(true);
    expect(denoise?.strength).toBe(85);
  });

  it('automatically configures stages on report in Auto preset', () => {
    const mockReport: DegradationReport = {
      blur: { score: 30.0, severity: 'high', label: 'Severe Blur', hint: 'Blurry' },
      haze: { score: 0.40, severity: 'high', label: 'Dense Fog', hint: 'Hazy' },
      noise: { score: 1.0, severity: 'low', label: 'Clean', hint: 'Clean' },
      contrast: { score: 0.35, severity: 'low', label: 'Good', hint: 'Good' },
      resolution_flag: true,
      dimensions: [1200, 800],
      hints: ['Severe blur', 'Dense fog'],
    };

    const store = useEnhanceStore.getState();
    store.setPreset('Auto');
    store.setReport(mockReport);

    const stages = useEnhanceStore.getState().stages;
    const dehaze = stages.find((s) => s.name === 'dehaze');
    const deblur = stages.find((s) => s.name === 'deblur');
    const denoise = stages.find((s) => s.name === 'denoise');
    const superres = stages.find((s) => s.name === 'super_resolution');

    expect(dehaze?.enabled).toBe(true);
    expect(dehaze?.strength).toBe(75);
    expect(deblur?.enabled).toBe(true);
    expect(deblur?.strength).toBe(75);
    expect(denoise?.enabled).toBe(true); // Enforce full-spectrum noise removal for crystal clarity
    expect(superres?.enabled).toBe(true); // resolution flag was true
  });
});
