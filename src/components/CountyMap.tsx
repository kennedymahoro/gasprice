import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { scaleQuantile } from 'd3-scale';
import { getGasPricesForCounty, GasPrices } from '../utils/mockData';
import { Tooltip } from './Tooltip';

const geoUrl = "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json";

export const CountyMap: React.FC = () => {
  const [tooltipContent, setTooltipContent] = useState<{
    countyName: string;
    stateName: string;
    prices: GasPrices;
  } | null>(null);
  
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // Premium color scale for gas prices
  const colorScale = scaleQuantile<string>()
    .domain([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
    .range([
      "#2A9D8F", // Teal (cheaper)
      "#8AB17D", 
      "#E9C46A", // Yellow (average)
      "#F4A261", 
      "#E76F51", // Red/Orange
      "#D62828", // Deep Red
      "#9D0208", // Dark Red (most expensive)
    ]);

  return (
    <div 
      className="map-wrapper" 
      onMouseMove={(e) => {
        if (tooltipContent) {
           setTooltipPos({ x: e.clientX, y: e.clientY });
        }
      }}
    >
      <ComposableMap projection="geoAlbersUsa" projectionConfig={{ scale: 1000 }} width={960} height={600} style={{ width: "100%", height: "100%" }}>
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map(geo => {
              const fips = geo.id;
              const prices = getGasPricesForCounty(fips);
              const curColor = colorScale(prices.regular);

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={curColor}
                  className="geography-path"
                  onMouseEnter={(e) => {
                    setTooltipContent({
                      countyName: geo.properties.name,
                      stateName: "", // Optional: Can map state ID to name if needed
                      prices: prices
                    });
                    setTooltipPos({ x: e.clientX, y: e.clientY });
                  }}
                  onMouseLeave={() => {
                    setTooltipContent(null);
                  }}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>
      <Tooltip content={tooltipContent} position={tooltipPos} />
    </div>
  );
};
