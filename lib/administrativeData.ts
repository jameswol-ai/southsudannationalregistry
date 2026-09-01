import { AdministrativeUnit, AdministrativePopulationSummary, CensusRecord } from './types';

export const INITIAL_ADMINISTRATIVE_UNITS: AdministrativeUnit[] = [
  // --- STATES ---
  {
    id: 'STATE-CE',
    type: 'State',
    name: 'Central Equatoria',
    code: 'CE-01',
    stateOrRegion: 'Central Equatoria',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Emmanuel Adil Anthony',
    headquarters: 'Juba City',
    estimatedTargetPopulation: 1450000,
    notes: 'National capital territory and primary administrative hub.'
  },
  {
    id: 'STATE-JON',
    type: 'State',
    name: 'Jonglei',
    code: 'JON-02',
    stateOrRegion: 'Jonglei',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Mahjoub Biel',
    headquarters: 'Bor Town',
    estimatedTargetPopulation: 1380000,
    notes: 'Largest territorial state across the Nile floodplains.'
  },
  {
    id: 'STATE-UN',
    type: 'State',
    name: 'Upper Nile',
    code: 'UN-03',
    stateOrRegion: 'Upper Nile',
    administratorTitle: 'Governor',
    administratorName: 'Hon. James Odhok Oyay',
    headquarters: 'Malakal Town',
    estimatedTargetPopulation: 980000,
    notes: 'Strategic river transport and oilfields corridor.'
  },
  {
    id: 'STATE-WBG',
    type: 'State',
    name: 'Western Bahr el Ghazal',
    code: 'WBG-04',
    stateOrRegion: 'Western Bahr el Ghazal',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Sarah Cleto Rial',
    headquarters: 'Wau City',
    estimatedTargetPopulation: 650000,
    notes: 'Commercial trade hub and historic railway terminus.'
  },
  {
    id: 'STATE-EE',
    type: 'State',
    name: 'Eastern Equatoria',
    code: 'EE-05',
    stateOrRegion: 'Eastern Equatoria',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Louis Lobong Lojore',
    headquarters: 'Torit Town',
    estimatedTargetPopulation: 910000,
    notes: 'Key international border trading and agricultural region.'
  },
  {
    id: 'STATE-WE',
    type: 'State',
    name: 'Western Equatoria',
    code: 'WE-06',
    stateOrRegion: 'Western Equatoria',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Alfred Futuyo Karaba',
    headquarters: 'Yambio Town',
    estimatedTargetPopulation: 720000,
    notes: 'High-yield agricultural breadbasket and forestry belt.'
  },
  {
    id: 'STATE-LAK',
    type: 'State',
    name: 'Lakes State',
    code: 'LAK-07',
    stateOrRegion: 'Lakes State',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Rin Tueny Mabor',
    headquarters: 'Rumbek City',
    estimatedTargetPopulation: 780000,
    notes: 'Central cattle corridor and academic heritage center.'
  },
  {
    id: 'STATE-NBEG',
    type: 'State',
    name: 'Northern Bahr el Ghazal',
    code: 'NBEG-08',
    stateOrRegion: 'Northern Bahr el Ghazal',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Tong Akeen Ngor',
    headquarters: 'Aweil City',
    estimatedTargetPopulation: 830000,
    notes: 'Dense agricultural and border trade zone.'
  },
  {
    id: 'STATE-UNT',
    type: 'State',
    name: 'Unity State',
    code: 'UNT-09',
    stateOrRegion: 'Unity State',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Joseph Monytuil',
    headquarters: 'Bentiu Town',
    estimatedTargetPopulation: 640000,
    notes: 'Key petroleum reserve and rich marshland ecosystem.'
  },
  {
    id: 'STATE-WRP',
    type: 'State',
    name: 'Warrap',
    code: 'WRP-10',
    stateOrRegion: 'Warrap',
    administratorTitle: 'Governor',
    administratorName: 'Hon. Kuol Muor Muor',
    headquarters: 'Kuajok City',
    estimatedTargetPopulation: 990000,
    notes: 'Major livestock and agricultural state.'
  },

  // --- COUNTIES ---
  {
    id: 'COU-JUBA',
    type: 'County',
    name: 'Juba County',
    code: 'COU-101',
    parentId: 'STATE-CE',
    parentName: 'Central Equatoria',
    stateOrRegion: 'Central Equatoria',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Charles Joseph Wani',
    headquarters: 'Juba Town',
    estimatedTargetPopulation: 680000,
    notes: 'Primary metropolitan county hosting government institutions.'
  },
  {
    id: 'COU-YEI',
    type: 'County',
    name: 'Yei River County',
    code: 'COU-102',
    parentId: 'STATE-CE',
    parentName: 'Central Equatoria',
    stateOrRegion: 'Central Equatoria',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Aggrey Cyrus Kanyikwa',
    headquarters: 'Yei Town',
    estimatedTargetPopulation: 250000,
    notes: 'Vibrant cross-border commercial and coffee producing center.'
  },
  {
    id: 'COU-BOR',
    type: 'County',
    name: 'Bor County',
    code: 'COU-201',
    parentId: 'STATE-JON',
    parentName: 'Jonglei',
    stateOrRegion: 'Jonglei',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. James Tuor',
    headquarters: 'Bor Town',
    estimatedTargetPopulation: 310000,
    notes: 'Historic trading town along the White Nile.'
  },
  {
    id: 'COU-MAL',
    type: 'County',
    name: 'Malakal County',
    code: 'COU-301',
    parentId: 'STATE-UN',
    parentName: 'Upper Nile',
    stateOrRegion: 'Upper Nile',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Paulino Onyaw',
    headquarters: 'Malakal Central',
    estimatedTargetPopulation: 220000,
    notes: 'River port connecting northern agricultural basins.'
  },
  {
    id: 'COU-WAU',
    type: 'County',
    name: 'Wau County',
    code: 'COU-401',
    parentId: 'STATE-WBG',
    parentName: 'Western Bahr el Ghazal',
    stateOrRegion: 'Western Bahr el Ghazal',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. George Andrea',
    headquarters: 'Wau City',
    estimatedTargetPopulation: 290000,
    notes: 'Cathedral city and manufacturing hub.'
  },
  {
    id: 'COU-TORIT',
    type: 'County',
    name: 'Torit County',
    code: 'COU-501',
    parentId: 'STATE-EE',
    parentName: 'Eastern Equatoria',
    stateOrRegion: 'Eastern Equatoria',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Jacob Atari Albano',
    headquarters: 'Torit Town',
    estimatedTargetPopulation: 210000,
    notes: 'Cradle of modern South Sudanese liberation movement.'
  },
  {
    id: 'COU-YAMBIO',
    type: 'County',
    name: 'Yambio County',
    code: 'COU-601',
    parentId: 'STATE-WE',
    parentName: 'Western Equatoria',
    stateOrRegion: 'Western Equatoria',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Mbiko Barakat',
    headquarters: 'Yambio Central',
    estimatedTargetPopulation: 195000,
    notes: 'Timber, fruit orchards, and dense tropical agriculture.'
  },
  {
    id: 'COU-RUMBEK',
    type: 'County',
    name: 'Rumbek Central County',
    code: 'COU-701',
    parentId: 'STATE-LAK',
    parentName: 'Lakes State',
    stateOrRegion: 'Lakes State',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Dut Manak',
    headquarters: 'Rumbek Town',
    estimatedTargetPopulation: 240000,
    notes: 'Cultural and academic crossroads in central South Sudan.'
  },
  {
    id: 'COU-AWEIL',
    type: 'County',
    name: 'Aweil Center County',
    code: 'COU-801',
    parentId: 'STATE-NBEG',
    parentName: 'Northern Bahr el Ghazal',
    stateOrRegion: 'Northern Bahr el Ghazal',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Peter Natale',
    headquarters: 'Aweil Town',
    estimatedTargetPopulation: 275000,
    notes: 'Rice irrigation scheme and bustling northern market.'
  },
  {
    id: 'COU-BENTIU',
    type: 'County',
    name: 'Rubkona / Bentiu County',
    code: 'COU-901',
    parentId: 'STATE-UNT',
    parentName: 'Unity State',
    stateOrRegion: 'Unity State',
    administratorTitle: 'County Commissioner',
    administratorName: 'Hon. Gatluak Wichar',
    headquarters: 'Rubkona Town',
    estimatedTargetPopulation: 230000,
    notes: 'Commercial trade hub and logistics port.'
  },

  // --- PAYAMS ---
  {
    id: 'PAY-JUBA',
    type: 'Payam',
    name: 'Juba Payam',
    code: 'PAY-101-01',
    parentId: 'COU-JUBA',
    parentName: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Ustaz Francis Lado',
    headquarters: 'Juba Na Bari',
    estimatedTargetPopulation: 180000
  },
  {
    id: 'PAY-MUNUKI',
    type: 'Payam',
    name: 'Munuki Payam',
    code: 'PAY-101-02',
    parentId: 'COU-JUBA',
    parentName: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. John Taban Wani',
    headquarters: 'Munuki Block A',
    estimatedTargetPopulation: 240000
  },
  {
    id: 'PAY-KATOR',
    type: 'Payam',
    name: 'Kator Payam',
    code: 'PAY-101-03',
    parentId: 'COU-JUBA',
    parentName: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Ms. Hellen Keji',
    headquarters: 'Kator Center',
    estimatedTargetPopulation: 140000
  },
  {
    id: 'PAY-RAJAF',
    type: 'Payam',
    name: 'Rajaf Payam',
    code: 'PAY-101-04',
    parentId: 'COU-JUBA',
    parentName: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Clement Jada',
    headquarters: 'Rajaf Hill',
    estimatedTargetPopulation: 85000
  },
  {
    id: 'PAY-BOR-TOWN',
    type: 'Payam',
    name: 'Bor Town Payam',
    code: 'PAY-201-01',
    parentId: 'COU-BOR',
    parentName: 'Bor County',
    stateOrRegion: 'Jonglei',
    countyOrPayam: 'Bor County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Deng Alier Mach',
    headquarters: 'Bor Town Center',
    estimatedTargetPopulation: 120000
  },
  {
    id: 'PAY-MAL-CENTRAL',
    type: 'Payam',
    name: 'Malakal Central Payam',
    code: 'PAY-301-01',
    parentId: 'COU-MAL',
    parentName: 'Malakal County',
    stateOrRegion: 'Upper Nile',
    countyOrPayam: 'Malakal County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Edward Yor',
    headquarters: 'Malakal Square',
    estimatedTargetPopulation: 95000
  },
  {
    id: 'PAY-WAU-NORTH',
    type: 'Payam',
    name: 'Wau North Payam',
    code: 'PAY-401-01',
    parentId: 'COU-WAU',
    parentName: 'Wau County',
    stateOrRegion: 'Western Bahr el Ghazal',
    countyOrPayam: 'Wau County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Santino Uyu',
    headquarters: 'Hai Jebel Wau',
    estimatedTargetPopulation: 110000
  },
  {
    id: 'PAY-TORIT-URBAN',
    type: 'Payam',
    name: 'Torit Urban Payam',
    code: 'PAY-501-01',
    parentId: 'COU-TORIT',
    parentName: 'Torit County',
    stateOrRegion: 'Eastern Equatoria',
    countyOrPayam: 'Torit County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Charles Ohure',
    headquarters: 'Torit Municipality',
    estimatedTargetPopulation: 88000
  },
  {
    id: 'PAY-YAMBIO-CENTRAL',
    type: 'Payam',
    name: 'Yambio Central Payam',
    code: 'PAY-601-01',
    parentId: 'COU-YAMBIO',
    parentName: 'Yambio County',
    stateOrRegion: 'Western Equatoria',
    countyOrPayam: 'Yambio County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Justin Gbaki',
    headquarters: 'Yambio Town Center',
    estimatedTargetPopulation: 75000
  },
  {
    id: 'PAY-RUMBEK-TOWN',
    type: 'Payam',
    name: 'Rumbek Town Payam',
    code: 'PAY-701-01',
    parentId: 'COU-RUMBEK',
    parentName: 'Rumbek Central County',
    stateOrRegion: 'Lakes State',
    countyOrPayam: 'Rumbek Central County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Isaiah Mayen',
    headquarters: 'Rumbek Civic Complex',
    estimatedTargetPopulation: 105000
  },
  {
    id: 'PAY-AWEIL-URBAN',
    type: 'Payam',
    name: 'Aweil Urban Payam',
    code: 'PAY-801-01',
    parentId: 'COU-AWEIL',
    parentName: 'Aweil Center County',
    stateOrRegion: 'Northern Bahr el Ghazal',
    countyOrPayam: 'Aweil Center County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Garang Deng Tong',
    headquarters: 'Aweil Market District',
    estimatedTargetPopulation: 115000
  },
  {
    id: 'PAY-BENTIU-TOWN',
    type: 'Payam',
    name: 'Bentiu Town Payam',
    code: 'PAY-901-01',
    parentId: 'COU-BENTIU',
    parentName: 'Rubkona / Bentiu County',
    stateOrRegion: 'Unity State',
    countyOrPayam: 'Rubkona / Bentiu County',
    administratorTitle: 'Payam Executive Director',
    administratorName: 'Mr. Peter Puok',
    headquarters: 'Bentiu Center',
    estimatedTargetPopulation: 90000
  },

  // --- BOMAS ---
  {
    id: 'BOM-MUN-BLKA',
    type: 'Boma',
    name: 'Munuki Block A',
    code: 'BOM-101-02-01',
    parentId: 'PAY-MUNUKI',
    parentName: 'Munuki Payam',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    subCountyOrBoma: 'Munuki Block A',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief David Kenyi',
    headquarters: 'Munuki Primary School',
    estimatedTargetPopulation: 45000
  },
  {
    id: 'BOM-MUN-BLKB',
    type: 'Boma',
    name: 'Munuki Block B',
    code: 'BOM-101-02-02',
    parentId: 'PAY-MUNUKI',
    parentName: 'Munuki Payam',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    subCountyOrBoma: 'Munuki Block B',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Simon Lado',
    headquarters: 'Munuki Community Center',
    estimatedTargetPopulation: 52000
  },
  {
    id: 'BOM-GUD-SEC1',
    type: 'Boma',
    name: 'Gudele Sector 1',
    code: 'BOM-101-02-03',
    parentId: 'PAY-MUNUKI',
    parentName: 'Munuki Payam',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    subCountyOrBoma: 'Gudele Sector 1',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Daniel Marial',
    headquarters: 'Gudele Market',
    estimatedTargetPopulation: 60000
  },
  {
    id: 'BOM-JUB-NABARI',
    type: 'Boma',
    name: 'Juba Na Bari Sector',
    code: 'BOM-101-01-01',
    parentId: 'PAY-JUBA',
    parentName: 'Juba Payam',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    subCountyOrBoma: 'Juba Na Bari Sector',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Wani Pitia',
    headquarters: 'Juba Na Bari Hall',
    estimatedTargetPopulation: 42000
  },
  {
    id: 'BOM-KAT-PARISH',
    type: 'Boma',
    name: 'Kator Parish Ward',
    code: 'BOM-101-03-01',
    parentId: 'PAY-KATOR',
    parentName: 'Kator Payam',
    stateOrRegion: 'Central Equatoria',
    countyOrPayam: 'Juba County',
    subCountyOrBoma: 'Kator Parish Ward',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Joseph Gore',
    headquarters: 'St. Theresa Parish Square',
    estimatedTargetPopulation: 38000
  },
  {
    id: 'BOM-BOR-ZONE3',
    type: 'Boma',
    name: 'Bor Town Zone 3',
    code: 'BOM-201-01-01',
    parentId: 'PAY-BOR-TOWN',
    parentName: 'Bor Town Payam',
    stateOrRegion: 'Jonglei',
    countyOrPayam: 'Bor County',
    subCountyOrBoma: 'Bor Town Zone 3',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Machar Kuol',
    headquarters: 'Bor Peace Park',
    estimatedTargetPopulation: 34000
  },
  {
    id: 'BOM-MAL-SETTLEMENT',
    type: 'Boma',
    name: 'Malakal Central Settlement',
    code: 'BOM-301-01-01',
    parentId: 'PAY-MAL-CENTRAL',
    parentName: 'Malakal Central Payam',
    stateOrRegion: 'Upper Nile',
    countyOrPayam: 'Malakal County',
    subCountyOrBoma: 'Malakal Central Settlement',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Chol Nyikang',
    headquarters: 'Malakal Port Office',
    estimatedTargetPopulation: 29000
  },
  {
    id: 'BOM-WAU-OLDTOWN',
    type: 'Boma',
    name: 'Wau Old Town',
    code: 'BOM-401-01-01',
    parentId: 'PAY-WAU-NORTH',
    parentName: 'Wau North Payam',
    stateOrRegion: 'Western Bahr el Ghazal',
    countyOrPayam: 'Wau County',
    subCountyOrBoma: 'Wau Old Town',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Hassan Fartak',
    headquarters: 'Wau Heritage Center',
    estimatedTargetPopulation: 31000
  },
  {
    id: 'BOM-TOR-HILLSIDE',
    type: 'Boma',
    name: 'Torit Hillside Community',
    code: 'BOM-501-01-01',
    parentId: 'PAY-TORIT-URBAN',
    parentName: 'Torit Urban Payam',
    stateOrRegion: 'Eastern Equatoria',
    countyOrPayam: 'Torit County',
    subCountyOrBoma: 'Torit Hillside Community',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Mario Oduho',
    headquarters: 'Torit Cultural Grounds',
    estimatedTargetPopulation: 26000
  },
  {
    id: 'BOM-YAM-GREENVALLEY',
    type: 'Boma',
    name: 'Yambio Green Valley',
    code: 'BOM-601-01-01',
    parentId: 'PAY-YAMBIO-CENTRAL',
    parentName: 'Yambio Central Payam',
    stateOrRegion: 'Western Equatoria',
    countyOrPayam: 'Yambio County',
    subCountyOrBoma: 'Yambio Green Valley',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Daniel Gbudwe',
    headquarters: 'Yambio Botanical Garden',
    estimatedTargetPopulation: 22000
  },
  {
    id: 'BOM-RUM-PALMGROVE',
    type: 'Boma',
    name: 'Rumbek Palm Grove',
    code: 'BOM-701-01-01',
    parentId: 'PAY-RUMBEK-TOWN',
    parentName: 'Rumbek Town Payam',
    stateOrRegion: 'Lakes State',
    countyOrPayam: 'Rumbek Central County',
    subCountyOrBoma: 'Rumbek Palm Grove',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Maker Deng',
    headquarters: 'Rumbek Freedom Square',
    estimatedTargetPopulation: 33000
  },
  {
    id: 'BOM-AWE-RAILWAY',
    type: 'Boma',
    name: 'Aweil Railway District',
    code: 'BOM-801-01-01',
    parentId: 'PAY-AWEIL-URBAN',
    parentName: 'Aweil Urban Payam',
    stateOrRegion: 'Northern Bahr el Ghazal',
    countyOrPayam: 'Aweil Center County',
    subCountyOrBoma: 'Aweil Railway District',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Akol Dut',
    headquarters: 'Aweil Old Depot',
    estimatedTargetPopulation: 28000
  },
  {
    id: 'BOM-BEN-RIVERSIDE',
    type: 'Boma',
    name: 'Bentiu Riverside Block',
    code: 'BOM-901-01-01',
    parentId: 'PAY-BENTIU-TOWN',
    parentName: 'Bentiu Town Payam',
    stateOrRegion: 'Unity State',
    countyOrPayam: 'Rubkona / Bentiu County',
    subCountyOrBoma: 'Bentiu Riverside Block',
    administratorTitle: 'Boma Chief / Headman',
    administratorName: 'Chief Taban Gatwich',
    headquarters: 'Bentiu Port Jetty',
    estimatedTargetPopulation: 25000
  }
];

const ADMIN_STORAGE_KEY = 'census_admin_units_v1';

export function getStoredAdministrativeUnits(): AdministrativeUnit[] {
  if (typeof window === 'undefined') {
    return INITIAL_ADMINISTRATIVE_UNITS;
  }
  try {
    const raw = localStorage.getItem(ADMIN_STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(INITIAL_ADMINISTRATIVE_UNITS));
      return INITIAL_ADMINISTRATIVE_UNITS;
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed) && parsed.length > 0) {
      return parsed;
    }
    return INITIAL_ADMINISTRATIVE_UNITS;
  } catch (err) {
    console.error('Error loading admin units:', err);
    return INITIAL_ADMINISTRATIVE_UNITS;
  }
}

export function saveAdministrativeUnits(units: AdministrativeUnit[]): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(units));
    window.dispatchEvent(new Event('admin_units_changed'));
  } catch (err) {
    console.error('Error saving admin units:', err);
  }
}

export function resetAdministrativeUnits(): AdministrativeUnit[] {
  if (typeof window === 'undefined') return INITIAL_ADMINISTRATIVE_UNITS;
  try {
    localStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(INITIAL_ADMINISTRATIVE_UNITS));
    window.dispatchEvent(new Event('admin_units_changed'));
    return INITIAL_ADMINISTRATIVE_UNITS;
  } catch (err) {
    console.error('Error resetting admin units:', err);
    return INITIAL_ADMINISTRATIVE_UNITS;
  }
}

// Calculate summary statistics for Counties, Payams, or Bomas based on census records
export function calculateAdministrativeSummaries(
  records: CensusRecord[],
  adminUnits: AdministrativeUnit[],
  type: 'State' | 'County' | 'Payam' | 'Boma',
  filterParent?: string
): AdministrativePopulationSummary[] {
  const units = adminUnits.filter(u => {
    if (u.type !== type) return false;
    if (filterParent) {
      return (
        u.parentId === filterParent ||
        u.parentName === filterParent ||
        u.stateOrRegion === filterParent ||
        u.countyOrPayam === filterParent
      );
    }
    return true;
  });

  return units.map(unit => {
    // Match records to this administrative unit
    const matchedRecords = records.filter(r => {
      if (type === 'State') {
        return r.stateOrRegion.toLowerCase() === unit.name.toLowerCase() ||
          r.stateOrRegion.toLowerCase().includes(unit.name.toLowerCase());
      }
      if (type === 'County') {
        return (
          (r.countyOrPayam && r.countyOrPayam.toLowerCase() === unit.name.toLowerCase()) ||
          (r.countyOrPayam && r.countyOrPayam.toLowerCase().includes(unit.name.toLowerCase()))
        );
      }
      if (type === 'Payam') {
        return (
          (r.countyOrPayam && r.countyOrPayam.toLowerCase() === unit.name.toLowerCase()) ||
          (r.subCountyOrBoma && r.subCountyOrBoma.toLowerCase().includes(unit.name.toLowerCase()))
        );
      }
      if (type === 'Boma') {
        return (
          (r.subCountyOrBoma && r.subCountyOrBoma.toLowerCase() === unit.name.toLowerCase()) ||
          (r.subCountyOrBoma && r.subCountyOrBoma.toLowerCase().includes(unit.name.toLowerCase())) ||
          (r.community && r.community.toLowerCase().includes(unit.name.toLowerCase()))
        );
      }
      return false;
    });

    const population = matchedRecords.length;
    const householdIds = new Set(matchedRecords.map(r => r.householdId).filter(Boolean));
    const maleCount = matchedRecords.filter(r => r.gender === 'Male').length;
    const femaleCount = matchedRecords.filter(r => r.gender === 'Female').length;
    const youthCount = matchedRecords.filter(r => r.age < 18).length;
    const adultCount = matchedRecords.filter(r => r.age >= 18 && r.age < 60).length;
    const seniorCount = matchedRecords.filter(r => r.age >= 60).length;
    const votersEligibleCount = matchedRecords.filter(
      r => r.age >= 18 && r.nationality.toLowerCase().includes('south sudan')
    ).length;
    const literateCount = matchedRecords.filter(r => r.isLiterate).length;
    const literacyRate = population > 0 ? Math.round((literateCount / population) * 100) : 0;
    const specialNeedsCount = matchedRecords.filter(r => r.hasSpecialNeedsOrDisability).length;

    const target = unit.estimatedTargetPopulation || 0;
    const coveragePercentage = target > 0 ? Math.min(100, Math.round((population / target) * 100 * 100) / 100) : undefined;

    return {
      name: unit.name,
      type: unit.type,
      stateOrRegion: unit.stateOrRegion,
      countyOrPayam: unit.countyOrPayam,
      subCountyOrBoma: unit.subCountyOrBoma,
      population,
      householdsCount: householdIds.size,
      maleCount,
      femaleCount,
      youthCount,
      adultCount,
      seniorCount,
      votersEligibleCount,
      literacyRate,
      specialNeedsCount,
      administratorName: unit.administratorName ? `${unit.administratorTitle || 'Admin'}: ${unit.administratorName}` : undefined,
      targetPopulation: unit.estimatedTargetPopulation,
      coveragePercentage
    };
  });
}
