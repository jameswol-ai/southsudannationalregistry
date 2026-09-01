import { CensusRecord, Candidate, PollingStation, ElectionSummaryStats } from './types';

export const OFFICIAL_POLLING_STATIONS: PollingStation[] = [
  {
    id: 'PS-JUB-01',
    code: 'PS-101-A',
    name: 'Munuki Primary School Polling Center (Stream A)',
    constituency: 'Juba Central Constituency',
    wardOrBoma: 'Munuki Block A',
    countyOrPayam: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    capacity: 750,
    isAccessible: true,
  },
  {
    id: 'PS-JUB-02',
    code: 'PS-101-B',
    name: 'Gudele Community Hall Station',
    constituency: 'Juba West Constituency',
    wardOrBoma: 'Gudele Sector 2',
    countyOrPayam: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    capacity: 650,
    isAccessible: true,
  },
  {
    id: 'PS-KAT-01',
    code: 'PS-102-A',
    name: 'Kator Cathedral Civic Center',
    constituency: 'Juba South Constituency',
    wardOrBoma: 'Kator Parish',
    countyOrPayam: 'Juba County',
    stateOrRegion: 'Central Equatoria',
    capacity: 800,
    isAccessible: true,
  },
  {
    id: 'PS-MAL-01',
    code: 'PS-201-A',
    name: 'Malakal Central Nile Riverside Pavilion',
    constituency: 'Malakal Central Constituency',
    wardOrBoma: 'Zone 1 Riverside',
    countyOrPayam: 'Malakal County',
    stateOrRegion: 'Upper Nile',
    capacity: 600,
    isAccessible: false,
  },
  {
    id: 'PS-BOR-01',
    code: 'PS-301-A',
    name: 'Bor Town Memorial High School Stream 1',
    constituency: 'Bor County Constituency',
    wardOrBoma: 'Bor Zone 3',
    countyOrPayam: 'Bor County',
    stateOrRegion: 'Jonglei',
    capacity: 700,
    isAccessible: true,
  },
  {
    id: 'PS-RUM-01',
    code: 'PS-401-A',
    name: 'Rumbek Freedom Square Station',
    constituency: 'Rumbek Central Constituency',
    wardOrBoma: 'Palm Grove Boma',
    countyOrPayam: 'Rumbek Central',
    stateOrRegion: 'Lakes State',
    capacity: 550,
    isAccessible: true,
  },
  {
    id: 'PS-TOR-01',
    code: 'PS-501-A',
    name: 'Torit Hillside Municipal Pavilion',
    constituency: 'Torit Urban Constituency',
    wardOrBoma: 'Hillside Ward',
    countyOrPayam: 'Torit County',
    stateOrRegion: 'Eastern Equatoria',
    capacity: 500,
    isAccessible: true,
  },
  {
    id: 'PS-YAM-01',
    code: 'PS-601-A',
    name: 'Yambio Green Valley Agricultural Center',
    constituency: 'Yambio Central Constituency',
    wardOrBoma: 'Green Valley Boma',
    countyOrPayam: 'Yambio County',
    stateOrRegion: 'Western Equatoria',
    capacity: 600,
    isAccessible: true,
  },
  {
    id: 'PS-AWE-01',
    code: 'PS-701-A',
    name: 'Aweil Railway Junction Voting Center',
    constituency: 'Aweil Town Constituency',
    wardOrBoma: 'Railway District',
    countyOrPayam: 'Aweil Center',
    stateOrRegion: 'Northern Bahr el Ghazal',
    capacity: 650,
    isAccessible: false,
  },
  {
    id: 'PS-WAU-01',
    code: 'PS-801-A',
    name: 'Wau Heritage Vocational Hall',
    constituency: 'Wau Urban Constituency',
    wardOrBoma: 'Old Town Boma',
    countyOrPayam: 'Wau County',
    stateOrRegion: 'Western Bahr el Ghazal',
    capacity: 700,
    isAccessible: true,
  }
];

export const INITIAL_CANDIDATES: Candidate[] = [
  {
    id: 'CAND-01',
    name: 'Dr. Rebecca Nyandeng Lado',
    party: 'National Democratic Alliance (NDA)',
    partyCode: 'NDA',
    position: 'Presidential',
    slogan: 'Unity, Economic Renewal & Inclusive Infrastructure',
    color: '#059669', // Emerald
    votesCount: 0,
  },
  {
    id: 'CAND-02',
    name: 'Hon. Emmanuel Taban Garang',
    party: 'People’s Progress & Reconstruction Movement (PPRM)',
    partyCode: 'PPRM',
    position: 'Presidential',
    slogan: 'Modern Agriculture, Universal Education & Public Integrity',
    color: '#2563eb', // Blue
    votesCount: 0,
  },
  {
    id: 'CAND-03',
    name: 'General Bol Majok Deng',
    party: 'Federal Coalition for Peace & Stability (FCPS)',
    partyCode: 'FCPS',
    position: 'Presidential',
    slogan: 'Security First, Border Logistics & Youth Employment',
    color: '#7c3aed', // Purple
    votesCount: 0,
  },
  {
    id: 'CAND-04',
    name: 'Grace Achiro Okello',
    party: 'Independent Civic Front (ICF)',
    partyCode: 'ICF',
    position: 'Presidential',
    slogan: 'Healthcare for All, Clean Energy & Community Empowerment',
    color: '#d97706', // Amber
    votesCount: 0,
  }
];

/**
 * Determines whether a census record meets national voter registration criteria:
 * 1. Age >= 18
 * 2. Nationality is South Sudan (or national citizen)
 * 3. Verification status is not 'Flagged'
 */
export function checkVoterEligibility(record: CensusRecord): {
  isEligible: boolean;
  reasons: string[];
} {
  const reasons: string[] = [];
  
  if (record.age < 18) {
    reasons.push(`Under legal voting age (${record.age} yrs < 18 yrs required)`);
  }
  
  const validNationalities = ['South Sudan', 'South Sudanese', 'National Citizen'];
  const hasValidNationality = validNationalities.some(n => 
    (record.nationality || '').toLowerCase().includes(n.toLowerCase())
  );
  if (!hasValidNationality) {
    reasons.push(`Non-citizen or foreign resident (${record.nationality || 'Unspecified'})`);
  }

  if (record.verificationStatus === 'Flagged') {
    reasons.push('Record flagged during demographic audit (requires electoral verification)');
  }

  return {
    isEligible: reasons.length === 0,
    reasons
  };
}

/**
 * Assigns or resolves the best matching polling station for a census record
 */
export function getAssignedPollingStation(record: CensusRecord): PollingStation {
  // If explicitly assigned:
  if (record.pollingStationId) {
    const found = OFFICIAL_POLLING_STATIONS.find(ps => ps.id === record.pollingStationId);
    if (found) return found;
  }

  // Otherwise match by state or community name
  const recState = (record.stateOrRegion || '').toLowerCase();
  const recComm = (record.community || '').toLowerCase();

  const match = OFFICIAL_POLLING_STATIONS.find(ps => {
    return ps.stateOrRegion.toLowerCase() === recState ||
           recComm.includes(ps.wardOrBoma.toLowerCase()) ||
           recComm.includes(ps.constituency.toLowerCase().split(' ')[0]);
  });

  return match || OFFICIAL_POLLING_STATIONS[0];
}

/**
 * Generates an official Voter Registration Number (VRN)
 */
export function generateVoterId(record: CensusRecord): string {
  if (record.voterIdNumber) return record.voterIdNumber;
  const cleanId = record.id.replace(/\D/g, '').slice(-4) || '1001';
  const ageHash = Math.abs((record.age * 37) % 900) + 100;
  return `VRN-2026-${cleanId}${ageHash}`;
}

/**
 * Enhances records with electoral metadata if missing
 */
export function syncElectoralData(records: CensusRecord[]): CensusRecord[] {
  return records.map(record => {
    const eligibility = checkVoterEligibility(record);
    const assignedStation = getAssignedPollingStation(record);
    const vrn = eligibility.isEligible ? generateVoterId(record) : undefined;
    
    return {
      ...record,
      voterIdNumber: record.voterIdNumber || vrn,
      voterStatus: record.voterStatus || (eligibility.isEligible ? 'Registered' : 'Ineligible'),
      constituency: record.constituency || assignedStation.constituency,
      pollingStationId: record.pollingStationId || assignedStation.id,
      pollingStationName: record.pollingStationName || assignedStation.name,
      hasVoted: typeof record.hasVoted === 'boolean' ? record.hasVoted : false
    };
  });
}

/**
 * Computes comprehensive election stats
 */
export function calculateElectionStats(records: CensusRecord[]): ElectionSummaryStats {
  const eligibleRecords = records.filter(r => checkVoterEligibility(r).isEligible);
  const registered = records.filter(r => r.voterStatus === 'Registered' || (checkVoterEligibility(r).isEligible && r.voterIdNumber));
  const voted = records.filter(r => r.hasVoted);

  const firstTime = eligibleRecords.filter(r => r.age >= 18 && r.age <= 24).length;
  const female = eligibleRecords.filter(r => r.gender === 'Female').length;
  const male = eligibleRecords.filter(r => r.gender === 'Male').length;
  const specialNeeds = eligibleRecords.filter(r => r.hasSpecialNeedsOrDisability).length;

  const totalRegistered = registered.length || eligibleRecords.length;
  const turnoutPercentage = totalRegistered > 0 ? (voted.length / totalRegistered) * 100 : 0;

  return {
    totalEligible: eligibleRecords.length,
    totalRegisteredVoters: totalRegistered,
    totalVotesCast: voted.length,
    turnoutPercentage: Math.round(turnoutPercentage * 10) / 10,
    firstTimeVotersCount: firstTime,
    femaleVotersCount: female,
    maleVotersCount: male,
    specialNeedsVotersCount: specialNeeds
  };
}

/**
 * Exports the official Electoral Commission Voter Register as CSV
 */
export function exportElectoralRollCSV(records: CensusRecord[]): void {
  const eligibleRecords = records.filter(r => checkVoterEligibility(r).isEligible);
  if (!eligibleRecords.length) return;

  const headers = [
    'Voter Registration No (VRN)',
    'National Census ID',
    'Full Voter Name',
    'Age',
    'Gender',
    'Tribe / Heritage',
    'Community / Settlement',
    'Assigned Constituency',
    'Polling Station Code',
    'Polling Station Name',
    'Special Needs / Accessible Booth Needed',
    'Voter Status',
    'Ballot Cast Status',
    'Voted Timestamp'
  ];

  const rows = eligibleRecords.map(r => {
    const ps = getAssignedPollingStation(r);
    return [
      r.voterIdNumber || generateVoterId(r),
      r.id,
      `"${r.fullName.replace(/"/g, '""')}"`,
      r.age,
      r.gender,
      `"${(r.tribe || '').replace(/"/g, '""')}"`,
      `"${(r.community || '').replace(/"/g, '""')}"`,
      `"${(r.constituency || ps.constituency).replace(/"/g, '""')}"`,
      ps.code,
      `"${(r.pollingStationName || ps.name).replace(/"/g, '""')}"`,
      r.hasSpecialNeedsOrDisability ? 'Yes (Priority Queue)' : 'No',
      r.voterStatus || 'Registered',
      r.hasVoted ? 'VOTED' : 'NOT VOTED',
      r.votedAt || ''
    ];
  });

  const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `official_electoral_roll_register_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
