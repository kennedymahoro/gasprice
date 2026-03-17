export interface GasPrices {
  regular: number;
  premium: number;
  diesel: number;
}

// Pseudo-random generator based on FIPS string to ensure stable mock data
function pseudoRandom(seed: string) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = Math.imul(31, h) + seed.charCodeAt(i) | 0;
  return function() {
    h = Math.imul(1597334677, h);
    return ((h >>> 0) / 4294967296);
  };
}

export function getGasPricesForCounty(fips: string): GasPrices {
  const rand = pseudoRandom(fips);
  
  // Base prices around national average with regional variation roughly based on FIPS
  // First digit of FIPS is state roughly.
  const stateCode = parseInt(fips.substring(0, 2)) || 10;
  
  // Some arbitrary math to create regional clusters
  const stateMultiplier = 1 + (stateCode % 10) * 0.05; 
  
  const baseRegular = 3.00 * stateMultiplier + (rand() * 1.5 - 0.5); // Add some noise
  
  return {
    regular: Number(Math.max(1.99, baseRegular).toFixed(2)),
    premium: Number(Math.max(2.50, (baseRegular + 0.60 + (rand() * 0.3))).toFixed(2)),
    diesel: Number(Math.max(2.99, (baseRegular + 0.80 + (rand() * 0.4))).toFixed(2))
  };
}
