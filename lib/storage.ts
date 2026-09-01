import { CensusRecord } from './types';
import { INITIAL_CENSUS_RECORDS } from './initialData';

const STORAGE_KEY = 'census_records_data_v1';

export function getStoredCensusRecords(): CensusRecord[] {
  if (typeof window === 'undefined') {
    return INITIAL_CENSUS_RECORDS;
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_CENSUS_RECORDS));
      return INITIAL_CENSUS_RECORDS;
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed) && parsed.length > 0) {
      return parsed;
    }
    return INITIAL_CENSUS_RECORDS;
  } catch (err) {
    console.error('Error loading census records from storage:', err);
    return INITIAL_CENSUS_RECORDS;
  }
}

export function saveCensusRecords(records: CensusRecord[]): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
    // Dispatch custom event so any active listeners can refresh
    window.dispatchEvent(new Event('census_data_changed'));
  } catch (err) {
    console.error('Error saving census records:', err);
  }
}

export function clearAllCensusRecords(): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
    window.dispatchEvent(new Event('census_data_changed'));
  } catch (err) {
    console.error('Error clearing census records:', err);
  }
}

export function resetToInitialRecords(): CensusRecord[] {
  if (typeof window === 'undefined') return INITIAL_CENSUS_RECORDS;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_CENSUS_RECORDS));
    window.dispatchEvent(new Event('census_data_changed'));
    return INITIAL_CENSUS_RECORDS;
  } catch (err) {
    console.error('Error resetting census records:', err);
    return INITIAL_CENSUS_RECORDS;
  }
}

export function generateCensusId(): string {
  const year = new Date().getFullYear();
  const randomNum = Math.floor(1000 + Math.random() * 9000);
  return `CEN-${year}-${randomNum}`;
}

export function generateHouseholdId(existingRecords: CensusRecord[]): string {
  const maxNum = existingRecords.reduce((max, r) => {
    const match = r.householdId?.match(/HH-(\d+)/i);
    if (match) {
      const val = parseInt(match[1], 10);
      return val > max ? val : max;
    }
    return max;
  }, 0);
  const nextNum = maxNum + 1;
  return `HH-${String(nextNum).padStart(3, '0')}`;
}

export function exportToCSV(records: CensusRecord[]): void {
  if (!records.length) return;
  
  const headers = [
    'Census ID',
    'ID Document Type',
    'National ID',
    'Passport Number',
    'Full Name',
    'Age',
    'Date of Birth',
    'Gender',
    'Marital Status',
    'Phone Number',
    'Email Address',
    'Emergency Contact Name',
    'Emergency Contact Phone',
    'Tribe / Ethnicity',
    'Sub-Tribe / Clan',
    'Native Language',
    'Nationality',
    'State / Region',
    'County / Payam',
    'Sub-County / Payam',
    'Boma',
    'Community / Settlement',
    'Residential Address',
    'Years in Community',
    'Household ID',
    'Household Role',
    'Is Head of Household',
    'Education Level',
    'Literate',
    'Employment Status',
    'Primary Occupation',
    'Employer / Business Name',
    'Industry Sector',
    'Monthly Income Range',
    'Disability / Special Needs',
    'Disability Details',
    'Voter ID Number',
    'Voter Status',
    'Polling Station ID',
    'Polling Station Name',
    'Has Voted',
    'Enumerator Name',
    'Enumerator Badge',
    'Enumeration Date',
    'Verification Status',
    'Notes'
  ];

  const rows = records.map(r => [
    r.id,
    `"${(r.idDocumentType || 'National ID').replace(/"/g, '""')}"`,
    r.nationalId || '',
    r.passportNumber || '',
    `"${r.fullName.replace(/"/g, '""')}"`,
    r.age,
    r.dateOfBirth || '',
    r.gender,
    r.maritalStatus,
    `"${(r.phoneNumber || '').replace(/"/g, '""')}"`,
    `"${(r.emailAddress || '').replace(/"/g, '""')}"`,
    `"${(r.emergencyContactName || '').replace(/"/g, '""')}"`,
    `"${(r.emergencyContactPhone || '').replace(/"/g, '""')}"`,
    `"${(r.tribe || '').replace(/"/g, '""')}"`,
    `"${(r.subTribeOrClan || '').replace(/"/g, '""')}"`,
    `"${(r.nativeLanguage || '').replace(/"/g, '""')}"`,
    `"${(r.nationality || '').replace(/"/g, '""')}"`,
    `"${(r.stateOrRegion || '').replace(/"/g, '""')}"`,
    `"${(r.countyOrPayam || '').replace(/"/g, '""')}"`,
    `"${(r.subCountyOrBoma || '').replace(/"/g, '""')}"`,
    `"${(r.boma || '').replace(/"/g, '""')}"`,
    `"${(r.community || '').replace(/"/g, '""')}"`,
    `"${(r.residentialAddress || '').replace(/"/g, '""')}"`,
    r.durationOfStayYears,
    r.householdId,
    r.householdRole,
    r.isHouseholdHead ? 'Yes' : 'No',
    `"${(r.educationLevel || '').replace(/"/g, '""')}"`,
    r.isLiterate ? 'Yes' : 'No',
    `"${(r.employmentStatus || '').replace(/"/g, '""')}"`,
    `"${(r.primaryOccupation || '').replace(/"/g, '""')}"`,
    `"${(r.employerOrBusinessName || '').replace(/"/g, '""')}"`,
    `"${(r.industrySector || '').replace(/"/g, '""')}"`,
    `"${(r.monthlyIncomeRange || '').replace(/"/g, '""')}"`,
    r.hasSpecialNeedsOrDisability ? 'Yes' : 'No',
    `"${(r.disabilityType || '').replace(/"/g, '""')}"`,
    `"${(r.voterIdNumber || '').replace(/"/g, '""')}"`,
    r.voterStatus || '',
    `"${(r.pollingStationId || '').replace(/"/g, '""')}"`,
    `"${(r.pollingStationName || '').replace(/"/g, '""')}"`,
    r.hasVoted ? 'Yes' : 'No',
    `"${(r.enumeratorName || '').replace(/"/g, '""')}"`,
    r.enumeratorBadgeId,
    r.enumerationDate,
    r.verificationStatus,
    `"${(r.notes || '').replace(/"/g, '""')}"`
  ]);

  const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `population_census_full_export_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function exportElectoralRollToCSV(records: CensusRecord[]): void {
  const voters = records.filter(r => r.age >= 18);
  if (!voters.length) return;

  const headers = [
    'Voter ID (VRN)',
    'National ID',
    'Passport Number',
    'Full Name',
    'Age',
    'Gender',
    'Phone Number',
    'State / Region',
    'County / Payam',
    'Payam',
    'Boma',
    'Community / Village',
    'Household ID',
    'Polling Station ID',
    'Polling Station Name',
    'Voter Status',
    'Has Voted',
    'Voted Timestamp'
  ];

  const rows = voters.map(r => [
    `"${(r.voterIdNumber || 'VRN-PENDING').replace(/"/g, '""')}"`,
    r.nationalId || '',
    r.passportNumber || '',
    `"${r.fullName.replace(/"/g, '""')}"`,
    r.age,
    r.gender,
    `"${(r.phoneNumber || '').replace(/"/g, '""')}"`,
    `"${(r.stateOrRegion || '').replace(/"/g, '""')}"`,
    `"${(r.countyOrPayam || '').replace(/"/g, '""')}"`,
    `"${(r.subCountyOrBoma || '').replace(/"/g, '""')}"`,
    `"${(r.boma || '').replace(/"/g, '""')}"`,
    `"${(r.community || '').replace(/"/g, '""')}"`,
    r.householdId,
    `"${(r.pollingStationId || '').replace(/"/g, '""')}"`,
    `"${(r.pollingStationName || '').replace(/"/g, '""')}"`,
    r.voterStatus || 'Registered',
    r.hasVoted ? 'YES' : 'NO',
    r.votedAt || ''
  ]);

  const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `official_voter_roll_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function downloadCensusCSVTemplate(): void {
  const headers = [
    'Full Name',
    'Age',
    'Gender',
    'Marital Status',
    'Phone Number',
    'Email Address',
    'ID Document Type',
    'National ID',
    'Passport Number',
    'Tribe',
    'State / Region',
    'County / Payam',
    'Sub-County / Payam',
    'Boma',
    'Community',
    'Household ID',
    'Household Role',
    'Education Level',
    'Employment Status',
    'Occupation',
    'Employer or Business',
    'Has Special Needs',
    'Voter ID',
    'Polling Station'
  ];

  const sampleRows = [
    [
      'Achol Deng Dut',
      '29',
      'Female',
      'Married',
      '+211 912 345 678',
      'achol.deng@example.com',
      'National ID',
      'SS-8921001-A',
      'P-SS882001',
      'Dinka (Jieng)',
      'Central Equatoria',
      'Juba County',
      'Munuki Payam',
      'Munuki Block A',
      'Munuki Residential Area',
      'HH-101',
      'Head of Household',
      'Tertiary / Bachelor Degree',
      'Employed (Public/Civil Service)',
      'Public Health Nurse',
      'Ministry of Health Clinic',
      'No',
      'VRN-2026-991204',
      'Munuki Primary Community Hall'
    ],
    [
      'Lado Taban Kenyi',
      '34',
      'Male',
      'Married',
      '+211 922 884 102',
      'lado.taban@business.org',
      'National ID',
      'SS-8921002-B',
      'P-SS882002',
      'Bari',
      'Central Equatoria',
      'Juba County',
      'Kator Payam',
      'Kator West Boma',
      'Kator Parish Ward',
      'HH-102',
      'Head of Household',
      'Vocational / Diploma',
      'Self-Employed / Business',
      'Hardware Wholesale Merchant',
      'Equatoria Supplies Co.',
      'No',
      'VRN-2026-991205',
      'Kator Community Center'
    ],
    [
      'Nyandeng Gatwich Biel',
      '21',
      'Female',
      'Single',
      '+211 977 112 334',
      'nyandeng.biel@edu.ss',
      'Passport',
      'SS-8921003-C',
      'P-SS882003',
      'Nuer (Naath)',
      'Jonglei',
      'Bor County',
      'Bor South Payam',
      'Hai Machuor Boma',
      'Bor Town Zone 3',
      'HH-103',
      'Son / Daughter',
      'Secondary Education',
      'Student',
      'University Student',
      'Dr. John Garang Memorial University',
      'No',
      'VRN-2026-991206',
      'Bor Civic Hall & Polling Stream'
    ]
  ];

  const csvContent = [headers.join(','), ...sampleRows.map(r => r.map(c => `"${c.replace(/"/g, '""')}"`).join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `census_data_import_template.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Robust CSV Line Parser that handles quoted commas and spaces
function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let insideQuote = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      if (insideQuote && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        insideQuote = !insideQuote;
      }
    } else if (char === ',' && !insideQuote) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim());
  return result;
}

export function parseCSVToCensusRecords(csvText: string): { 
  records: CensusRecord[]; 
  errors: string[]; 
  warnings: string[];
  totalRows: number 
} {
  const lines = csvText.split(/\r?\n/).filter(line => line.trim().length > 0);
  if (lines.length < 2) {
    return { records: [], errors: ['CSV file is empty or missing data rows.'], warnings: [], totalRows: 0 };
  }

  const rawHeaders = parseCSVLine(lines[0]).map(h => h.toLowerCase().replace(/[^a-z0-9]/g, ''));
  const headerMap: Record<string, number> = {};

  rawHeaders.forEach((h, idx) => {
    if (h.includes('fullname') || h === 'name' || h.includes('personname')) headerMap['fullName'] = idx;
    else if (h === 'age' || h.includes('yearsold')) headerMap['age'] = idx;
    else if (h === 'gender' || h === 'sex') headerMap['gender'] = idx;
    else if (h.includes('marital')) headerMap['maritalStatus'] = idx;
    else if (h.includes('phone') || h.includes('mobile') || h.includes('tel')) headerMap['phoneNumber'] = idx;
    else if (h.includes('email') || h.includes('mail')) headerMap['emailAddress'] = idx;
    else if (h.includes('emergencyphone') || h.includes('emergencymobile')) headerMap['emergencyContactPhone'] = idx;
    else if (h.includes('emergency') || h.includes('nextofkin')) headerMap['emergencyContactName'] = idx;
    else if (h.includes('passport')) headerMap['passportNumber'] = idx;
    else if (h.includes('doctype') || h.includes('documenttype') || h.includes('idtype')) headerMap['idDocumentType'] = idx;
    else if (h.includes('nationalid') || h.includes('nin') || h.includes('idnumber')) headerMap['nationalId'] = idx;
    else if (h.includes('tribe') || h.includes('ethnicity')) headerMap['tribe'] = idx;
    else if (h.includes('subtribe') || h.includes('clan')) headerMap['subTribeOrClan'] = idx;
    else if (h.includes('language')) headerMap['nativeLanguage'] = idx;
    else if (h.includes('nationality') || h.includes('citizenship')) headerMap['nationality'] = idx;
    else if (h.includes('state') || h.includes('region')) headerMap['stateOrRegion'] = idx;
    else if (h.includes('county')) headerMap['countyOrPayam'] = idx;
    else if (h.includes('payam') || h.includes('subcounty')) headerMap['subCountyOrBoma'] = idx;
    else if (h.includes('boma') || h.includes('ward') || h.includes('block')) headerMap['boma'] = idx;
    else if (h.includes('community') || h.includes('settlement') || h.includes('village')) headerMap['community'] = idx;
    else if (h.includes('address') || h.includes('street')) headerMap['residentialAddress'] = idx;
    else if (h.includes('householdid') || h.includes('hhid')) headerMap['householdId'] = idx;
    else if (h.includes('role') || h.includes('householdrole')) headerMap['householdRole'] = idx;
    else if (h.includes('head') || h.includes('ishead')) headerMap['isHouseholdHead'] = idx;
    else if (h.includes('education') || h.includes('school')) headerMap['educationLevel'] = idx;
    else if (h.includes('literate') || h.includes('literacy')) headerMap['isLiterate'] = idx;
    else if (h.includes('employment') || h.includes('status')) headerMap['employmentStatus'] = idx;
    else if (h.includes('employer') || h.includes('business') || h.includes('company')) headerMap['employerOrBusinessName'] = idx;
    else if (h.includes('industry') || h.includes('sector')) headerMap['industrySector'] = idx;
    else if (h.includes('income') || h.includes('salary')) headerMap['monthlyIncomeRange'] = idx;
    else if (h.includes('occupation') || h.includes('job') || h.includes('profession')) headerMap['primaryOccupation'] = idx;
    else if (h.includes('disability') || h.includes('specialneeds')) headerMap['hasSpecialNeedsOrDisability'] = idx;
    else if (h.includes('voterid') || h.includes('vrn')) headerMap['voterIdNumber'] = idx;
    else if (h.includes('polling') || h.includes('station')) headerMap['pollingStationName'] = idx;
    else if (h.includes('id') || h.includes('censusid')) headerMap['id'] = idx;
  });

  if (headerMap['fullName'] === undefined) {
    return { 
      records: [], 
      errors: ['Could not identify "Full Name" or "Name" column in CSV headers.'], 
      warnings: [],
      totalRows: lines.length - 1 
    };
  }

  const records: CensusRecord[] = [];
  const errors: string[] = [];
  const warnings: string[] = [];
  const nowIso = new Date().toISOString();

  for (let i = 1; i < lines.length; i++) {
    const rowValues = parseCSVLine(lines[i]);
    if (rowValues.length < 2 || rowValues.every(val => !val)) continue;

    const getValue = (key: string): string => {
      const idx = headerMap[key];
      return idx !== undefined && rowValues[idx] ? rowValues[idx] : '';
    };

    const fullName = getValue('fullName');
    if (!fullName) {
      warnings.push(`Row ${i + 1}: Skipped record due to blank name.`);
      continue;
    }

    const rawAge = parseInt(getValue('age'), 10);
    const age = isNaN(rawAge) ? 25 : Math.max(0, Math.min(120, rawAge));

    let gender = (getValue('gender') || 'Male') as any;
    if (!['Male', 'Female', 'Other'].includes(gender)) {
      gender = gender.toLowerCase().startsWith('f') ? 'Female' : 'Male';
    }

    let maritalStatus = (getValue('maritalStatus') || 'Single') as any;
    if (!['Single', 'Married', 'Widowed', 'Divorced', 'Separated'].includes(maritalStatus)) {
      maritalStatus = 'Single';
    }

    const tribe = getValue('tribe') || 'Dinka (Jieng)';
    const stateOrRegion = getValue('stateOrRegion') || 'Central Equatoria';
    const countyOrPayam = getValue('countyOrPayam') || 'Juba County';
    const subCountyOrBoma = getValue('subCountyOrBoma') || 'Munuki Payam';
    const boma = getValue('boma') || 'Munuki Block A';
    const community = getValue('community') || `${subCountyOrBoma} Area`;

    const householdId = getValue('householdId') || `HH-${String(100 + i).padStart(3, '0')}`;
    let householdRole = (getValue('householdRole') || 'Head of Household') as any;
    const isHeadRaw = getValue('isHouseholdHead').toLowerCase();
    const isHouseholdHead = isHeadRaw === 'yes' || isHeadRaw === 'true' || householdRole === 'Head of Household';

    let educationLevel = (getValue('educationLevel') || 'Secondary Education') as any;
    const isLiterate = getValue('isLiterate').toLowerCase() === 'no' ? false : (age >= 6);

    let employmentStatus = (getValue('employmentStatus') || 'Self-Employed / Business') as any;
    const primaryOccupation = getValue('primaryOccupation') || 'Resident / Worker';

    const specialNeedsRaw = getValue('hasSpecialNeedsOrDisability').toLowerCase();
    const hasSpecialNeedsOrDisability = specialNeedsRaw === 'yes' || specialNeedsRaw === 'true';

    const voterIdNumber = getValue('voterIdNumber') || (age >= 18 ? `VRN-2026-${Math.floor(100000 + Math.random() * 900000)}` : undefined);
    const voterStatus = age >= 18 ? 'Registered' : 'Ineligible';

    const recordId = getValue('id') || `CEN-2026-${String(Math.floor(1000 + Math.random() * 9000))}`;

    records.push({
      id: recordId,
      idDocumentType: (getValue('idDocumentType') || (getValue('passportNumber') ? 'Passport' : 'National ID')) as any,
      nationalId: getValue('nationalId') || undefined,
      passportNumber: getValue('passportNumber') || undefined,
      fullName,
      age,
      gender,
      maritalStatus,
      phoneNumber: getValue('phoneNumber') || undefined,
      emailAddress: getValue('emailAddress') || undefined,
      emergencyContactName: getValue('emergencyContactName') || undefined,
      emergencyContactPhone: getValue('emergencyContactPhone') || undefined,
      tribe,
      subTribeOrClan: getValue('subTribeOrClan') || undefined,
      nativeLanguage: getValue('nativeLanguage') || 'Dinka (Thuɔŋjäŋ)',
      nationality: getValue('nationality') || 'South Sudan',
      stateOrRegion,
      countyOrPayam,
      subCountyOrBoma,
      boma,
      community,
      residentialAddress: getValue('residentialAddress') || `${community}, ${countyOrPayam}`,
      durationOfStayYears: 5,
      householdId,
      householdRole,
      isHouseholdHead,
      educationLevel,
      isLiterate,
      employmentStatus,
      primaryOccupation,
      employerOrBusinessName: getValue('employerOrBusinessName') || undefined,
      industrySector: getValue('industrySector') || undefined,
      monthlyIncomeRange: getValue('monthlyIncomeRange') || undefined,
      hasSpecialNeedsOrDisability,
      voterIdNumber,
      voterStatus,
      pollingStationName: getValue('pollingStationName') || `${countyOrPayam} Polling Station`,
      enumeratorName: 'Import Engine Batch Ingest',
      enumeratorBadgeId: 'BATCH-CSV-01',
      enumerationDate: nowIso.split('T')[0],
      verificationStatus: 'Verified',
      notes: `Imported via CSV file on ${new Date().toLocaleDateString()}`,
      createdAt: nowIso,
      updatedAt: nowIso
    });
  }

  return {
    records,
    errors,
    warnings,
    totalRows: lines.length - 1
  };
}

export function exportAdministrativeSummaryToCSV(
  summaries: any[],
  levelName: string
): void {
  if (!summaries.length) return;

  const headers = [
    'Administrative Level',
    'Name',
    'Parent Region / County',
    'Counted Population',
    'Target Projection',
    'Coverage %',
    'Households',
    'Male Count',
    'Female Count',
    'Youth (0-17)',
    'Adults (18-59)',
    'Seniors (60+)',
    'Eligible Voters',
    'Literacy Rate %',
    'Special Needs Cases',
    'Designated Administrator'
  ];

  const rows = summaries.map(s => [
    levelName,
    `"${(s.name || '').replace(/"/g, '""')}"`,
    `"${(s.stateOrRegion || s.countyOrPayam || '').replace(/"/g, '""')}"`,
    s.population,
    s.targetPopulation || 'N/A',
    s.coveragePercentage ? `${s.coveragePercentage}%` : 'N/A',
    s.householdsCount,
    s.maleCount,
    s.femaleCount,
    s.youthCount,
    s.adultCount,
    s.seniorCount,
    s.votersEligibleCount,
    `${s.literacyRate}%`,
    s.specialNeedsCount,
    `"${(s.administratorName || '').replace(/"/g, '""')}"`
  ]);

  const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${levelName.toLowerCase()}_population_census_summary_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function exportToJSON(records: CensusRecord[]): void {
  const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(records, null, 2))}`;
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute('href', jsonString);
  downloadAnchor.setAttribute('download', `census_data_backup_${new Date().toISOString().split('T')[0]}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

