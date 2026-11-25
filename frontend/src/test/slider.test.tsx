/// <reference types="@testing-library/jest-dom" />
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ComparisonSlider } from '../components/viewer/ComparisonSlider';

describe('ComparisonSlider Component', () => {
  const beforeUrl = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
  const afterUrl = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

  it('renders slider with original and enhanced labels', () => {
    render(<ComparisonSlider beforeUrl={beforeUrl} afterUrl={afterUrl} />);

    expect(screen.getByText('ORIGINAL')).toBeInTheDocument();
    expect(screen.getByText('ENHANCED')).toBeInTheDocument();
  });

  it('renders accessible slider handle with ARIA attributes', () => {
    render(<ComparisonSlider beforeUrl={beforeUrl} afterUrl={afterUrl} />);

    const sliderHandle = screen.getByRole('slider');
    expect(sliderHandle).toBeInTheDocument();
    expect(sliderHandle).toHaveAttribute('aria-valuenow', '50');
    expect(sliderHandle).toHaveAttribute('aria-valuemin', '0');
    expect(sliderHandle).toHaveAttribute('aria-valuemax', '100');
  });

  it('responds to keyboard arrow navigation', () => {
    render(<ComparisonSlider beforeUrl={beforeUrl} afterUrl={afterUrl} />);

    const sliderHandle = screen.getByRole('slider');
    sliderHandle.focus();

    // Arrow Left decreases slider position by 2
    fireEvent.keyDown(sliderHandle, { key: 'ArrowLeft' });
    expect(sliderHandle).toHaveAttribute('aria-valuenow', '48');

    // Arrow Right increases slider position by 2
    fireEvent.keyDown(sliderHandle, { key: 'ArrowRight' });
    expect(sliderHandle).toHaveAttribute('aria-valuenow', '50');

    // Shift + Arrow Right increases by 10
    fireEvent.keyDown(sliderHandle, { key: 'ArrowRight', shiftKey: true });
    expect(sliderHandle).toHaveAttribute('aria-valuenow', '60');
  });

  it('renders zoom controls and toggles 1:1 view', () => {
    render(<ComparisonSlider beforeUrl={beforeUrl} afterUrl={afterUrl} />);

    expect(screen.getByText('100%')).toBeInTheDocument();
    const oneToOneBtn = screen.getByText('1:1');
    expect(oneToOneBtn).toBeInTheDocument();

    fireEvent.click(oneToOneBtn);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});
