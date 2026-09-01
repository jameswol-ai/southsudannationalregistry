export type Gender = 'Male' | 'Female' | 'Other';

export type MaritalStatus = 'Single' | 'Married' | 'Widowed' | 'Divorced' | 'Separated';

export type EducationLevel = 
  | 'None / Informal'
  | 'Primary Education'
  | 'Secondary Education'
  | 'Vocational / Diploma'
  | 'Tertiary / Bachelor Degree'
  | 'Post-Graduate (Master/PhD)';

export type EmploymentStatus = 
  | 'Employed (Private Sector)'
  | 'Employed (Public/Civil Service)'
  | 'Self-Employed / Business'
  | 'Agriculture & Farming'
  | 'Pastoralism & Livestock'
  | 'Artisan / Trade'
  | 'Student'
  | 'Unemployed / Seeking Work'
  | 'Homemaker / Caregiver'
  | 'Retired / Pensioner';

export type HouseholdRole = 
  | 'Head of Household'
  | 'Spouse'
  | 'Son / Daughter'
  | 'Parent / Parent-in-law'
  | 'Grandchild'
  | 'Other Relative'
  | 'Non-Relative / Resident';

export type VerificationStatus = 'Verified' | 'Pending Review' | 'Flagged';

export type IdentificationType = 
  | 'National ID'
  | 'Passport'
  | 'Birth Certificate'
  | 'Refugee / Alien Registration'
  | 'Voter Card'
  | 'Other';

export interface CensusRecord {
  id: string; // Unique Census ID, e.g. CEN-2026-0841
  
  // Identification & Travel Documents
  idDocumentType?: IdentificationType;
  nationalId?: string; // e.g. SS-98214301-A
  passportNumber?: string; // e.g. P-SS8839201
  
  fullName: string;
  age: number;
  dateOfBirth?: string;
  gender: Gender;
  maritalStatus: MaritalStatus;
  
  // Contact & Communication Details
  phoneNumber?: string;
  emailAddress?: string;
  emergencyContactName?: string;
  emergencyContactPhone?: string;

  // Ethnic and Cultural Heritage
  tribe: string;
  subTribeOrClan?: string;
  nativeLanguage: string;
  nationality: string;
  
  // Location & Administrative Geography
  community: string; // Village / Neighborhood / Settlement
  boma?: string; // Grassroots Boma / Block
  subCountyOrBoma: string; // Payam / Sub-County
  countyOrPayam: string; // County
  stateOrRegion: string; // State / Region
  residentialAddress?: string;
  durationOfStayYears: number; // Years lived in this community
  
  // Household Unit
  householdId: string; // e.g. HH-0104
  householdRole: HouseholdRole;
  isHouseholdHead: boolean;
  
  // Socioeconomic & Demographics
  educationLevel: EducationLevel;
  isLiterate: boolean;
  employmentStatus: EmploymentStatus;
  primaryOccupation?: string;
  employerOrBusinessName?: string;
  industrySector?: string;
  monthlyIncomeRange?: string;
  hasSpecialNeedsOrDisability: boolean;
  disabilityType?: string;
  
  // Health & Vital info
  isBiologicalParentAlive?: {
    motherAlive: boolean;
    fatherAlive: boolean;
  };
  
  // Electoral & Voter Metadata
  voterIdNumber?: string; // Official Voter Registration Number e.g. VRN-884-209
  voterStatus?: 'Eligible' | 'Ineligible' | 'Registered' | 'Suspended';
  constituency?: string;
  pollingStationId?: string;
  pollingStationName?: string;
  hasVoted?: boolean;
  votedAt?: string;
  votedBallotSelection?: string;

  // Enumeration Metadata
  enumeratorName: string;
  enumeratorBadgeId: string;
  enumerationDate: string;
  verificationStatus: VerificationStatus;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Candidate {
  id: string;
  name: string;
  party: string;
  partyCode: string;
  position: 'Presidential' | 'Parliamentary' | 'Gubernatorial';
  slogan: string;
  color: string;
  votesCount: number;
}

export interface PollingStation {
  id: string;
  code: string;
  name: string;
  constituency: string;
  countyOrPayam: string;
  stateOrRegion: string;
  wardOrBoma: string;
  capacity: number;
  isAccessible: boolean;
}

export interface ElectionSummaryStats {
  totalEligible: number;
  totalRegisteredVoters: number;
  totalVotesCast: number;
  turnoutPercentage: number;
  firstTimeVotersCount: number; // 18-24
  femaleVotersCount: number;
  maleVotersCount: number;
  specialNeedsVotersCount: number;
}

export interface HouseholdSummary {
  householdId: string;
  headName: string;
  community: string;
  stateOrRegion: string;
  membersCount: number;
  members: CensusRecord[];
  primaryTribe: string;
}

export interface CensusStats {
  totalCount: number;
  totalHouseholds: number;
  maleCount: number;
  femaleCount: number;
  otherCount: number;
  avgAge: number;
  literacyRate: number;
  tribesCount: number;
  communitiesCount: number;
}

export interface AdministrativeUnit {
  id: string; // e.g. "COU-JUBA", "PAY-MUNUKI", "BOM-BLKA"
  type: 'State' | 'County' | 'Payam' | 'Boma';
  name: string;
  code: string;
  parentId?: string; // Links Boma -> Payam -> County -> State
  parentName?: string;
  stateOrRegion: string;
  countyOrPayam?: string;
  subCountyOrBoma?: string;
  administratorTitle?: string; // e.g. "County Commissioner", "Executive Director", "Boma Chief"
  administratorName?: string;
  headquarters?: string;
  estimatedTargetPopulation?: number;
  notes?: string;
}

export interface AdministrativePopulationSummary {
  name: string;
  type: 'State' | 'County' | 'Payam' | 'Boma';
  stateOrRegion: string;
  countyOrPayam?: string;
  subCountyOrBoma?: string;
  population: number;
  householdsCount: number;
  maleCount: number;
  femaleCount: number;
  youthCount: number; // 0-17
  adultCount: number; // 18-59
  seniorCount: number; // 60+
  votersEligibleCount: number;
  literacyRate: number;
  specialNeedsCount: number;
  administratorName?: string;
  targetPopulation?: number;
  coveragePercentage?: number;
}
