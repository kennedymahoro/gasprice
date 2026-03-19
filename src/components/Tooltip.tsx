import React from 'react';
import { GasPrices } from './CountyMap';
import { MapPin } from 'lucide-react';

interface TooltipProps {
  content: {
    countyName: string;
    stateName: string;
    prices: GasPrices;
  } | null;
  position: { x: number; y: number };
}

export const Tooltip: React.FC<TooltipProps> = ({ content, position }) => {
  if (!content) return null;

  // Add a small offset so cursor doesn't cover tooltip
  const left = position.x + 15;
  const top = position.y + 15;

  return (
    <div 
      className="tooltip-container"
      style={{ left, top }}
    >
      <div className="tooltip-header">
        <MapPin size={16} className="tooltip-icon" />
        <span className="tooltip-title">{content.countyName} County</span>
      </div>
      <div className="tooltip-body">
        <div className="price-row">
          <span className="price-label regular">Regular</span>
          <span className="price-value">${content.prices.regular.toFixed(2)}</span>
        </div>
        <div className="price-row">
          <span className="price-label premium">Premium</span>
          <span className="price-value">${content.prices.premium.toFixed(2)}</span>
        </div>
        <div className="price-row">
          <span className="price-label diesel">Diesel</span>
          <span className="price-value">${content.prices.diesel.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};
