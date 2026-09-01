'use client';

import React, { useState, useEffect } from 'react';
import { 
  CensusRecord, 
  Gender, 
  MaritalStatus, 
  EducationLevel, 
  EmploymentStatus, 
  HouseholdRole,
  VerificationStatus,
  IdentificationType
} from '@/lib/types';
import { 
  COMMON_TRIBES, 
  COMMON_COMMUNITIES, 
  COMMON_REGIONS, 
  COMMON_LANGUAGES 
} from '@/lib/initialData';
import { generateCensusId, generateHouseholdId } from '@/lib/storage';
import { OFFICIAL_POLLING_STATIONS, generateVoterId, checkVoterEligibility, getAssignedPollingStation } from '@/lib/electionData';
import { getStoredAdministrativeUnits } from '@/lib/administrativeData';
import { 
  UserPlus, 
  Save, 
  CheckCircle2, 
  AlertCircle, 
  Users, 
  MapPin, 
  Building2, 
  GraduationCap, 
  Briefcase, 
  ShieldCheck, 
  Sparkles,
  ArrowRight,
  RotateCcw,
  Vote,
  IdCard,
  Phone,
  Mail,
  FileText
} from 'lucide-react';

interface Props {
  existingRecord?: CensusRecord | null;
  existingRecords: CensusRecord[];
  onSave: (record: CensusRecord) => void;
  onCancel?: () => void;
  defaultHouseholdId?: string;
  defaultCommunity?: string;
  defaultStateOrRegion?: string;
}

export const EnumerationForm: React.FC<Props> = ({
  existingRecord,
  existingRecords,
  onSave,
  onCancel,
  defaultHouseholdId,
  defaultCommunity,
  defaultStateOrRegion
}) => {
  // Existing HH lookup if adding to existing HH
  const existingInHH = defaultHouseholdId 
    ? existingRecords.find(r => r.householdId === defaultHouseholdId)
    : undefined;

  // Form State initialized directly
  const [fullName, setFullName] = useState(existingRecord?.fullName || '');
  const [idDocumentType, setIdDocumentType] = useState<IdentificationType>(existingRecord?.idDocumentType || 'National ID');
  const [nationalId, setNationalId] = useState(existingRecord?.nationalId || '');
  const [passportNumber, setPassportNumber] = useState(existingRecord?.passportNumber || '');
  const [age, setAge] = useState<number | ''>(existingRecord ? existingRecord.age : 25);
  const [dateOfBirth, setDateOfBirth] = useState(existingRecord?.dateOfBirth || '');
  const [gender, setGender] = useState<Gender>(existingRecord?.gender || 'Male');
  const [maritalStatus, setMaritalStatus] = useState<MaritalStatus>(existingRecord?.maritalStatus || 'Single');

  // Contact Details
  const [phoneNumber, setPhoneNumber] = useState(existingRecord?.phoneNumber || '');
  const [emailAddress, setEmailAddress] = useState(existingRecord?.emailAddress || '');
  const [emergencyContactName, setEmergencyContactName] = useState(existingRecord?.emergencyContactName || '');
  const [emergencyContactPhone, setEmergencyContactPhone] = useState(existingRecord?.emergencyContactPhone || '');

  // Heritage
  const [tribe, setTribe] = useState(() => {
    if (existingRecord) {
      return COMMON_TRIBES.includes(existingRecord.tribe) ? existingRecord.tribe : 'Other / Not Listed';
    }
    if (existingInHH) {
      return COMMON_TRIBES.includes(existingInHH.tribe) ? existingInHH.tribe : 'Other / Not Listed';
    }
    return COMMON_TRIBES[0];
  });
  const [customTribe, setCustomTribe] = useState(() => {
    if (existingRecord && !COMMON_TRIBES.includes(existingRecord.tribe)) {
      return existingRecord.tribe;
    }
    if (existingInHH && !COMMON_TRIBES.includes(existingInHH.tribe)) {
      return existingInHH.tribe;
    }
    return '';
  });
  const [subTribeOrClan, setSubTribeOrClan] = useState(existingRecord?.subTribeOrClan || existingInHH?.subTribeOrClan || '');
  const [nativeLanguage, setNativeLanguage] = useState(() => {
    if (existingRecord) {
      return COMMON_LANGUAGES.includes(existingRecord.nativeLanguage) ? existingRecord.nativeLanguage : 'Other';
    }
    if (existingInHH) {
      return COMMON_LANGUAGES.includes(existingInHH.nativeLanguage) ? existingInHH.nativeLanguage : 'Other';
    }
    return COMMON_LANGUAGES[0];
  });
  const [customLanguage, setCustomLanguage] = useState(() => {
    if (existingRecord && !COMMON_LANGUAGES.includes(existingRecord.nativeLanguage)) {
      return existingRecord.nativeLanguage;
    }
    if (existingInHH && !COMMON_LANGUAGES.includes(existingInHH.nativeLanguage)) {
      return existingInHH.nativeLanguage;
    }
    return '';
  });
  const [nationality, setNationality] = useState(existingRecord?.nationality || 'South Sudan');

  // Location & Admin Hierarchy
  const [community, setCommunity] = useState(() => {
    if (existingRecord) {
      return COMMON_COMMUNITIES.includes(existingRecord.community) ? existingRecord.community : 'Other';
    }
    if (existingInHH) {
      return COMMON_COMMUNITIES.includes(existingInHH.community) ? existingInHH.community : 'Other';
    }
    if (defaultCommunity) {
      return COMMON_COMMUNITIES.includes(defaultCommunity) ? defaultCommunity : 'Other';
    }
    return COMMON_COMMUNITIES[0];
  });
  const [customCommunity, setCustomCommunity] = useState(() => {
    if (existingRecord && !COMMON_COMMUNITIES.includes(existingRecord.community)) {
      return existingRecord.community;
    }
    if (existingInHH && !COMMON_COMMUNITIES.includes(existingInHH.community)) {
      return existingInHH.community;
    }
    return '';
  });
  const [boma, setBoma] = useState(existingRecord?.boma || existingRecord?.subCountyOrBoma || existingInHH?.boma || existingInHH?.subCountyOrBoma || '');
  const [subCountyOrBoma, setSubCountyOrBoma] = useState(existingRecord?.subCountyOrBoma || existingInHH?.subCountyOrBoma || '');
  const [countyOrPayam, setCountyOrPayam] = useState(existingRecord?.countyOrPayam || existingInHH?.countyOrPayam || '');
  const [stateOrRegion, setStateOrRegion] = useState(
    existingRecord?.stateOrRegion || existingInHH?.stateOrRegion || defaultStateOrRegion || COMMON_REGIONS[0]
  );
  const [residentialAddress, setResidentialAddress] = useState(existingRecord?.residentialAddress || existingInHH?.residentialAddress || '');
  const [durationOfStayYears, setDurationOfStayYears] = useState<number | ''>(existingRecord ? existingRecord.durationOfStayYears : 5);

  // Administrative units for dynamic lookup options
  const adminUnits = getStoredAdministrativeUnits();
  const availableStates = Array.from(new Set([...COMMON_REGIONS, ...adminUnits.filter(u => u.type === 'State').map(u => u.name)]));
  
  const suggestedCounties = adminUnits
    .filter(u => u.type === 'County' && (!stateOrRegion || u.stateOrRegion === stateOrRegion || u.parentName === stateOrRegion))
    .map(u => u.name);

  const suggestedPayams = adminUnits
    .filter(u => u.type === 'Payam' && (!countyOrPayam || u.countyOrPayam === countyOrPayam || u.parentName === countyOrPayam))
    .map(u => u.name);

  const suggestedBomas = adminUnits
    .filter(u => u.type === 'Boma' && (!subCountyOrBoma || u.subCountyOrBoma === subCountyOrBoma || u.parentName === subCountyOrBoma))
    .map(u => u.name);

  // Household
  const [householdId, setHouseholdId] = useState(
    existingRecord?.householdId || defaultHouseholdId || 'HH-001'
  );
  const [householdRole, setHouseholdRole] = useState<HouseholdRole>(
    existingRecord?.householdRole || (defaultHouseholdId ? 'Son / Daughter' : 'Head of Household')
  );
  const [isHouseholdHead, setIsHouseholdHead] = useState(
    existingRecord ? !!existingRecord.isHouseholdHead : !defaultHouseholdId
  );

  // Socioeconomic & Occupation
  const [educationLevel, setEducationLevel] = useState<EducationLevel>(
    existingRecord?.educationLevel || 'Secondary Education'
  );
  const [isLiterate, setIsLiterate] = useState(existingRecord ? existingRecord.isLiterate : true);
  const [employmentStatus, setEmploymentStatus] = useState<EmploymentStatus>(
    existingRecord?.employmentStatus || 'Agriculture & Farming'
  );
  const [primaryOccupation, setPrimaryOccupation] = useState(existingRecord?.primaryOccupation || '');
  const [employerOrBusinessName, setEmployerOrBusinessName] = useState(existingRecord?.employerOrBusinessName || '');
  const [industrySector, setIndustrySector] = useState(existingRecord?.industrySector || '');
  const [monthlyIncomeRange, setMonthlyIncomeRange] = useState(existingRecord?.monthlyIncomeRange || 'SSP 50,000 - 150,000');
  const [hasSpecialNeedsOrDisability, setHasSpecialNeedsOrDisability] = useState(
    existingRecord?.hasSpecialNeedsOrDisability || false
  );
  const [disabilityType, setDisabilityType] = useState(existingRecord?.disabilityType || '');

  // Electoral & Voter Enrollment State
  const [voterIdNumber, setVoterIdNumber] = useState(existingRecord?.voterIdNumber || '');
  const [pollingStationId, setPollingStationId] = useState(
    existingRecord?.pollingStationId || OFFICIAL_POLLING_STATIONS[0].id
  );
  const [voterStatus, setVoterStatus] = useState(existingRecord?.voterStatus || 'Registered');

  // Enumerator & Metadata
  const [enumeratorName, setEnumeratorName] = useState(existingRecord?.enumeratorName || 'Grace Kiden Taban');
  const [enumeratorBadgeId, setEnumeratorBadgeId] = useState(existingRecord?.enumeratorBadgeId || 'ENUM-042');
  const [enumerationDate, setEnumerationDate] = useState(
    existingRecord?.enumerationDate || new Date().toISOString().split('T')[0]
  );
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus>(
    existingRecord?.verificationStatus || 'Verified'
  );
  const [notes, setNotes] = useState(existingRecord?.notes || '');

  // Status & Feedback
  const [errorMsg, setErrorMsg] = useState('');
  const [successSaved, setSuccessSaved] = useState(false);

  // Unique list of existing households for easy dropdown selection
  const existingHouseholdIds = Array.from(
    new Set(existingRecords.map(r => r.householdId).filter(Boolean))
  ).sort();

  const handleGenerateNewHouseholdId = () => {
    const newId = generateHouseholdId(existingRecords);
    setHouseholdId(newId);
    setIsHouseholdHead(true);
    setHouseholdRole('Head of Household');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!fullName.trim()) {
      setErrorMsg('Please enter the full legal name of the individual.');
      return;
    }

    const finalTribe = tribe === 'Other / Not Listed' ? customTribe.trim() || 'Unspecified Tribe' : tribe;
    const finalLanguage = nativeLanguage === 'Other' ? customLanguage.trim() || 'Other' : nativeLanguage;
    const finalCommunity = community === 'Other' ? customCommunity.trim() || 'General Community' : community;

    if (!finalTribe) {
      setErrorMsg('Please specify the tribe or ethnic group.');
      return;
    }

    if (!finalCommunity) {
      setErrorMsg('Please specify the community or settlement name.');
      return;
    }

    const currentAge = typeof age === 'number' ? age : 0;
    const isCitizen = nationality.toLowerCase().includes('south sudan') || nationality.toLowerCase().includes('national');
    const isEligibleToVote = currentAge >= 18 && isCitizen && verificationStatus !== 'Flagged';

    const selectedPs = OFFICIAL_POLLING_STATIONS.find(ps => ps.id === pollingStationId) || OFFICIAL_POLLING_STATIONS[0];
    const generatedVrn = voterIdNumber.trim() || (isEligibleToVote ? `VRN-2026-${Math.floor(100000 + Math.random() * 900000)}` : undefined);

    const nowIso = new Date().toISOString();
    const recordToSave: CensusRecord = {
      id: existingRecord ? existingRecord.id : generateCensusId(),
      idDocumentType,
      nationalId: nationalId.trim() || undefined,
      passportNumber: passportNumber.trim() || undefined,
      fullName: fullName.trim(),
      age: currentAge,
      dateOfBirth: dateOfBirth || undefined,
      gender,
      maritalStatus,
      phoneNumber: phoneNumber.trim() || undefined,
      emailAddress: emailAddress.trim() || undefined,
      emergencyContactName: emergencyContactName.trim() || undefined,
      emergencyContactPhone: emergencyContactPhone.trim() || undefined,
      tribe: finalTribe,
      subTribeOrClan: subTribeOrClan.trim() || undefined,
      nativeLanguage: finalLanguage,
      nationality: nationality.trim() || 'South Sudan',
      community: finalCommunity,
      boma: boma.trim() || undefined,
      subCountyOrBoma: subCountyOrBoma.trim() || boma.trim() || 'Central Payam',
      countyOrPayam: countyOrPayam.trim() || 'Juba County',
      stateOrRegion: stateOrRegion.trim() || 'Central Equatoria',
      residentialAddress: residentialAddress.trim() || undefined,
      durationOfStayYears: typeof durationOfStayYears === 'number' ? durationOfStayYears : 0,
      householdId: householdId.trim() || 'HH-001',
      householdRole,
      isHouseholdHead,
      educationLevel,
      isLiterate,
      employmentStatus,
      primaryOccupation: primaryOccupation.trim() || undefined,
      employerOrBusinessName: employerOrBusinessName.trim() || undefined,
      industrySector: industrySector.trim() || undefined,
      monthlyIncomeRange: monthlyIncomeRange || undefined,
      hasSpecialNeedsOrDisability,
      disabilityType: hasSpecialNeedsOrDisability ? disabilityType.trim() : undefined,
      // Electoral Metadata
      voterIdNumber: isEligibleToVote ? generatedVrn : undefined,
      voterStatus: isEligibleToVote ? voterStatus : 'Ineligible',
      constituency: selectedPs.constituency,
      pollingStationId: selectedPs.id,
      pollingStationName: selectedPs.name,
      hasVoted: existingRecord?.hasVoted || false,
      votedAt: existingRecord?.votedAt,
      votedBallotSelection: existingRecord?.votedBallotSelection,
      // Enumerator
      enumeratorName: enumeratorName.trim() || 'Field Enumerator',
      enumeratorBadgeId: enumeratorBadgeId.trim() || 'ENUM-001',
      enumerationDate: enumerationDate || nowIso.split('T')[0],
      verificationStatus,
      notes: notes.trim() || undefined,
      createdAt: existingRecord ? existingRecord.createdAt : nowIso,
      updatedAt: nowIso
    };

    onSave(recordToSave);
    setSuccessSaved(true);

    if (!existingRecord) {
      // Clear personal fields for next entry in same household or new
      setTimeout(() => {
        setSuccessSaved(false);
        setFullName('');
        setNationalId('');
        setPassportNumber('');
        setPhoneNumber('');
        setEmailAddress('');
        setEmergencyContactName('');
        setEmergencyContactPhone('');
        setAge(25);
        setDateOfBirth('');
        setPrimaryOccupation('');
        setEmployerOrBusinessName('');
        setSubTribeOrClan('');
        // Keep household ID if needed, but flip head status
        if (isHouseholdHead) {
          setIsHouseholdHead(false);
          setHouseholdRole('Spouse');
        }
      }, 1200);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-200 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 mb-2">
            <UserPlus className="w-3.5 h-3.5" />
            {existingRecord ? 'Editing Census Record' : 'Official Enumeration Entry'}
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            {existingRecord ? `Update Record: ${existingRecord.fullName}` : 'Register Individual for Census'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Capture demographic particulars, ethnic heritage, community settlement, and household membership.
          </p>
        </div>

        {existingRecord && onCancel && (
          <button
            id="cancel-edit-btn"
            type="button"
            onClick={onCancel}
            className="self-start sm:self-auto px-3.5 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Cancel Edit
          </button>
        )}
      </div>

      {errorMsg && (
        <div className="my-4 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs sm:text-sm flex items-center gap-2 font-medium animate-shake">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successSaved && (
        <div className="my-4 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs sm:text-sm flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>Record successfully saved and committed to census database!</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-8">
        {/* Section 1: Personal & Legal Identification */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs flex items-center justify-center font-bold">1</span>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
              Personal & Legal Identification
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs sm:text-sm">
            {/* Full Name */}
            <div className="lg:col-span-2">
              <label htmlFor="census-fullname-input" className="block font-semibold text-slate-700 mb-1">
                Full Legal Name <span className="text-red-500">*</span>
              </label>
              <input
                id="census-fullname-input"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Deng Majok Akech"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400 font-medium"
              />
            </div>

            {/* Document Type */}
            <div>
              <label htmlFor="census-idtype-select" className="block font-semibold text-slate-700 mb-1">
                Primary Identity Document
              </label>
              <select
                id="census-idtype-select"
                value={idDocumentType}
                onChange={(e) => setIdDocumentType(e.target.value as IdentificationType)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                <option value="National ID">National ID Card</option>
                <option value="Passport">Passport</option>
                <option value="Birth Certificate">Birth Certificate</option>
                <option value="Refugee / Alien Registration">Refugee / Alien Card</option>
                <option value="Voter Card">Voter Registration Card</option>
                <option value="Other">Other / Local Chief Letter</option>
              </select>
            </div>

            {/* National ID Number */}
            <div>
              <label htmlFor="census-nationalid-input" className="block font-semibold text-slate-700 mb-1">
                National ID Number
              </label>
              <input
                id="census-nationalid-input"
                type="text"
                value={nationalId}
                onChange={(e) => setNationalId(e.target.value)}
                placeholder="e.g. SSD-1098452-A"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400 font-mono"
              />
            </div>

            {/* Passport Number */}
            <div>
              <label htmlFor="census-passport-input" className="block font-semibold text-slate-700 mb-1">
                Passport Number (if applicable)
              </label>
              <input
                id="census-passport-input"
                type="text"
                value={passportNumber}
                onChange={(e) => setPassportNumber(e.target.value)}
                placeholder="e.g. P01984251"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400 font-mono"
              />
            </div>

            {/* Age */}
            <div>
              <label htmlFor="census-age-input" className="block font-semibold text-slate-700 mb-1">
                Age (Completed Years) <span className="text-red-500">*</span>
              </label>
              <input
                id="census-age-input"
                type="number"
                min="0"
                max="130"
                required
                value={age}
                onChange={(e) => setAge(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              />
            </div>

            {/* Date of Birth */}
            <div>
              <label htmlFor="census-dob-input" className="block font-semibold text-slate-700 mb-1">
                Date of Birth (if known)
              </label>
              <input
                id="census-dob-input"
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              />
            </div>

            {/* Gender */}
            <div>
              <label htmlFor="census-gender-select" className="block font-semibold text-slate-700 mb-1">
                Gender <span className="text-red-500">*</span>
              </label>
              <select
                id="census-gender-select"
                value={gender}
                onChange={(e) => setGender(e.target.value as Gender)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Marital Status */}
            <div>
              <label htmlFor="census-marital-select" className="block font-semibold text-slate-700 mb-1">
                Marital Status <span className="text-red-500">*</span>
              </label>
              <select
                id="census-marital-select"
                value={maritalStatus}
                onChange={(e) => setMaritalStatus(e.target.value as MaritalStatus)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                <option value="Single">Single (Never Married)</option>
                <option value="Married">Married (Monogamous/Polygamous)</option>
                <option value="Widowed">Widowed</option>
                <option value="Divorced">Divorced</option>
                <option value="Separated">Separated</option>
              </select>
            </div>

            {/* Nationality */}
            <div>
              <label htmlFor="census-nationality-input" className="block font-semibold text-slate-700 mb-1">
                Country of Citizenship
              </label>
              <input
                id="census-nationality-input"
                type="text"
                value={nationality}
                onChange={(e) => setNationality(e.target.value)}
                placeholder="South Sudan"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              />
            </div>
          </div>
        </div>

        {/* Section: Contact & Emergency Details */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-cyan-800 text-white text-xs flex items-center justify-center font-bold">
              <Phone className="w-3 h-3" />
            </span>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
              Contact & Emergency Particulars
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs sm:text-sm">
            <div>
              <label htmlFor="census-phone-input" className="block font-semibold text-slate-700 mb-1">
                Primary Phone Number
              </label>
              <input
                id="census-phone-input"
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+211 92 000 0000"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-700 text-slate-900 bg-white font-mono"
              />
            </div>

            <div>
              <label htmlFor="census-email-input" className="block font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <input
                id="census-email-input"
                type="email"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                placeholder="citizen@example.gov.ss"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-700 text-slate-900 bg-white"
              />
            </div>

            <div>
              <label htmlFor="census-emergency-name" className="block font-semibold text-slate-700 mb-1">
                Emergency Contact Name
              </label>
              <input
                id="census-emergency-name"
                type="text"
                value={emergencyContactName}
                onChange={(e) => setEmergencyContactName(e.target.value)}
                placeholder="e.g. Mary Yar Deng"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-700 text-slate-900 bg-white"
              />
            </div>

            <div>
              <label htmlFor="census-emergency-phone" className="block font-semibold text-slate-700 mb-1">
                Emergency Contact Phone
              </label>
              <input
                id="census-emergency-phone"
                type="tel"
                value={emergencyContactPhone}
                onChange={(e) => setEmergencyContactPhone(e.target.value)}
                placeholder="+211 91 111 2222"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-700 text-slate-900 bg-white font-mono"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Heritage & Origin (Tribe, Clan, Native Language) */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-emerald-800 text-white text-xs flex items-center justify-center font-bold">2</span>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
              Tribe, Ethnic Group & Mother Tongue
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs sm:text-sm">
            {/* Tribe Selection */}
            <div>
              <label htmlFor="census-tribe-select" className="block font-semibold text-slate-700 mb-1">
                Tribe / Ethnic Community <span className="text-red-500">*</span>
              </label>
              <select
                id="census-tribe-select"
                value={tribe}
                onChange={(e) => setTribe(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white font-medium"
              >
                {COMMON_TRIBES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            {/* Custom Tribe if Other */}
            {tribe === 'Other / Not Listed' && (
              <div>
                <label htmlFor="census-custom-tribe-input" className="block font-semibold text-emerald-800 mb-1">
                  Specify Tribe / Ethnicity Name <span className="text-red-500">*</span>
                </label>
                <input
                  id="census-custom-tribe-input"
                  type="text"
                  required
                  value={customTribe}
                  onChange={(e) => setCustomTribe(e.target.value)}
                  placeholder="e.g. Pojulu, Moru, Shilluk, Kuku..."
                  className="w-full px-3.5 py-2 rounded-lg border border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-emerald-50/50"
                />
              </div>
            )}

            {/* Sub-Tribe or Clan */}
            <div>
              <label htmlFor="census-subclan-input" className="block font-semibold text-slate-700 mb-1">
                Sub-Tribe / Clan / Section
              </label>
              <input
                id="census-subclan-input"
                type="text"
                value={subTribeOrClan}
                onChange={(e) => setSubTribeOrClan(e.target.value)}
                placeholder="e.g. Rek / Lou / Pöri / Payira"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
            </div>

            {/* Native Language */}
            <div>
              <label htmlFor="census-language-select" className="block font-semibold text-slate-700 mb-1">
                Native Language / Dialect <span className="text-red-500">*</span>
              </label>
              <select
                id="census-language-select"
                value={nativeLanguage}
                onChange={(e) => setNativeLanguage(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                {COMMON_LANGUAGES.map((lang) => (
                  <option key={lang} value={lang}>{lang}</option>
                ))}
              </select>
            </div>

            {/* Custom Language */}
            {nativeLanguage === 'Other' && (
              <div>
                <label htmlFor="census-custom-lang-input" className="block font-semibold text-slate-700 mb-1">
                  Specify Language Name
                </label>
                <input
                  id="census-custom-lang-input"
                  type="text"
                  value={customLanguage}
                  onChange={(e) => setCustomLanguage(e.target.value)}
                  placeholder="Enter language"
                  className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
                />
              </div>
            )}
          </div>
        </div>

        {/* Section 3: Geographic & Community Settlement */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-blue-800 text-white text-xs flex items-center justify-center font-bold">3</span>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
                Administrative Hierarchy & Community Settlement
              </h3>
              <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                State &gt; County &gt; Payam &gt; Boma
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs sm:text-sm">
            {/* State / Region */}
            <div>
              <label htmlFor="census-region-select" className="block font-semibold text-slate-700 mb-1">
                State / Administrative Area <span className="text-red-500">*</span>
              </label>
              <select
                id="census-region-select"
                value={stateOrRegion}
                onChange={(e) => setStateOrRegion(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white font-medium"
              >
                {availableStates.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            {/* County / Municipality */}
            <div>
              <label htmlFor="census-payam-input" className="block font-semibold text-slate-700 mb-1">
                County / Municipality <span className="text-red-500">*</span>
              </label>
              <input
                id="census-payam-input"
                list="county-suggestions"
                type="text"
                value={countyOrPayam}
                onChange={(e) => setCountyOrPayam(e.target.value)}
                placeholder="e.g. Juba County, Bor South..."
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400 font-medium"
              />
              <datalist id="county-suggestions">
                {suggestedCounties.map(c => (
                  <option key={c} value={c} />
                ))}
              </datalist>
            </div>

            {/* Payam (Sub-County) */}
            <div>
              <label htmlFor="census-subcounty-input" className="block font-semibold text-slate-700 mb-1">
                Payam (Sub-County)
              </label>
              <input
                id="census-subcounty-input"
                list="payam-suggestions"
                type="text"
                value={subCountyOrBoma}
                onChange={(e) => setSubCountyOrBoma(e.target.value)}
                placeholder="e.g. Munuki Payam, Kator..."
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
              <datalist id="payam-suggestions">
                {suggestedPayams.map(p => (
                  <option key={p} value={p} />
                ))}
              </datalist>
            </div>

            {/* Boma (Ward/Quarter) */}
            <div>
              <label htmlFor="census-boma-input" className="block font-semibold text-slate-700 mb-1">
                Boma / Village Ward / Quarter
              </label>
              <input
                id="census-boma-input"
                list="boma-suggestions"
                type="text"
                value={boma}
                onChange={(e) => setBoma(e.target.value)}
                placeholder="e.g. Block 4 Boma, Malakia..."
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
              <datalist id="boma-suggestions">
                {suggestedBomas.map(b => (
                  <option key={b} value={b} />
                ))}
              </datalist>
            </div>

            {/* Community / Village Selection */}
            <div>
              <label htmlFor="census-community-select" className="block font-semibold text-slate-700 mb-1">
                Community / Settlement <span className="text-red-500">*</span>
              </label>
              <select
                id="census-community-select"
                value={community}
                onChange={(e) => setCommunity(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white font-medium"
              >
                {COMMON_COMMUNITIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
                <option value="Other">+ Custom / Unlisted Community</option>
              </select>
            </div>

            {/* Custom Community */}
            {community === 'Other' && (
              <div>
                <label htmlFor="census-custom-comm-input" className="block font-semibold text-blue-800 mb-1">
                  Enter Settlement Name <span className="text-red-500">*</span>
                </label>
                <input
                  id="census-custom-comm-input"
                  type="text"
                  required
                  value={customCommunity}
                  onChange={(e) => setCustomCommunity(e.target.value)}
                  placeholder="e.g. Bilpam Village, Tongpiny..."
                  className="w-full px-3.5 py-2 rounded-lg border border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-600 text-slate-900 bg-blue-50/40"
                />
              </div>
            )}

            {/* Residential Address / Landmark */}
            <div>
              <label htmlFor="census-address-input" className="block font-semibold text-slate-700 mb-1">
                Physical Address / Plot / Landmark
              </label>
              <input
                id="census-address-input"
                type="text"
                value={residentialAddress}
                onChange={(e) => setResidentialAddress(e.target.value)}
                placeholder="e.g. Plot 42 Near St. Paul Church"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
            </div>

            {/* Duration of stay */}
            <div>
              <label htmlFor="census-stay-years-input" className="block font-semibold text-slate-700 mb-1">
                Years Lived in this Community
              </label>
              <input
                id="census-stay-years-input"
                type="number"
                min="0"
                max="100"
                value={durationOfStayYears}
                onChange={(e) => setDurationOfStayYears(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              />
            </div>
          </div>
        </div>

        {/* Section 4: Household Unit Association */}
        <div>
          <div className="flex items-center justify-between mb-4 pb-1 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-purple-800 text-white text-xs flex items-center justify-center font-bold">4</span>
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
                Household & Family Unit Mapping
              </h3>
            </div>
            <button
              id="generate-household-id-btn"
              type="button"
              onClick={handleGenerateNewHouseholdId}
              className="text-xs text-purple-700 hover:text-purple-900 font-semibold flex items-center gap-1 bg-purple-50 px-2.5 py-1 rounded-md border border-purple-200"
            >
              + Start New Household Unit
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs sm:text-sm bg-purple-50/40 p-4 rounded-xl border border-purple-100">
            {/* Household ID */}
            <div>
              <label htmlFor="census-household-id-input" className="block font-semibold text-slate-700 mb-1">
                Household Identification Code <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2">
                <input
                  id="census-household-id-input"
                  type="text"
                  required
                  value={householdId}
                  onChange={(e) => setHouseholdId(e.target.value.toUpperCase())}
                  placeholder="e.g. HH-001"
                  className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-purple-700 text-slate-900 bg-white font-mono font-bold"
                />
              </div>
              {existingHouseholdIds.length > 0 && (
                <div className="mt-1.5 flex items-center gap-1.5 flex-wrap">
                  <span className="text-[11px] text-slate-500">Pick Existing:</span>
                  {existingHouseholdIds.slice(0, 5).map((hh) => (
                    <button
                      key={hh}
                      type="button"
                      onClick={() => {
                        setHouseholdId(hh);
                        setIsHouseholdHead(false);
                        setHouseholdRole('Son / Daughter');
                      }}
                      className="px-1.5 py-0.5 text-[11px] font-mono bg-white hover:bg-purple-100 text-purple-800 rounded border border-purple-200"
                    >
                      {hh}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Household Role */}
            <div>
              <label htmlFor="census-household-role-select" className="block font-semibold text-slate-700 mb-1">
                Relationship to Household Head
              </label>
              <select
                id="census-household-role-select"
                value={householdRole}
                onChange={(e) => {
                  const val = e.target.value as HouseholdRole;
                  setHouseholdRole(val);
                  setIsHouseholdHead(val === 'Head of Household');
                }}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-purple-700 text-slate-900 bg-white font-medium"
              >
                <option value="Head of Household">Head of Household</option>
                <option value="Spouse">Spouse</option>
                <option value="Son / Daughter">Son / Daughter</option>
                <option value="Parent / Parent-in-law">Parent / Parent-in-law</option>
                <option value="Grandchild">Grandchild</option>
                <option value="Other Relative">Other Relative</option>
                <option value="Non-Relative / Resident">Non-Relative / Domestic Assistant</option>
              </select>
            </div>

            {/* Is Head Checkbox */}
            <div className="flex items-center">
              <label className="flex items-center gap-2.5 p-3 rounded-lg bg-white border border-purple-200 cursor-pointer w-full">
                <input
                  id="census-is-head-checkbox"
                  type="checkbox"
                  checked={isHouseholdHead}
                  onChange={(e) => {
                    setIsHouseholdHead(e.target.checked);
                    if (e.target.checked) {
                      setHouseholdRole('Head of Household');
                    }
                  }}
                  className="w-4 h-4 text-purple-600 rounded border-slate-300 focus:ring-purple-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 block text-xs">Primary Household Head</span>
                  <span className="text-[11px] text-slate-500 block">Responsible for family enumeration unit</span>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Section 5: Socioeconomic & Vital Data */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-amber-700 text-white text-xs flex items-center justify-center font-bold">5</span>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
              Education, Livelihood & Special Needs
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs sm:text-sm">
            {/* Education */}
            <div>
              <label htmlFor="census-education-select" className="block font-semibold text-slate-700 mb-1">
                Highest Educational Attainment
              </label>
              <select
                id="census-education-select"
                value={educationLevel}
                onChange={(e) => {
                  const val = e.target.value as EducationLevel;
                  setEducationLevel(val);
                  setIsLiterate(val !== 'None / Informal');
                }}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                <option value="None / Informal">None / Informal (No formal schooling)</option>
                <option value="Primary Education">Primary Education (Grades 1-8)</option>
                <option value="Secondary Education">Secondary Education (Grades 9-12)</option>
                <option value="Vocational / Diploma">Vocational / Diploma / Certificate</option>
                <option value="Tertiary / Bachelor Degree">Tertiary / University Bachelor</option>
                <option value="Post-Graduate (Master/PhD)">Post-Graduate (Master / Doctorate)</option>
              </select>
            </div>

            {/* Literacy Toggle */}
            <div className="flex items-center">
              <label className="flex items-center gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200 cursor-pointer w-full">
                <input
                  id="census-literacy-checkbox"
                  type="checkbox"
                  checked={isLiterate}
                  onChange={(e) => setIsLiterate(e.target.checked)}
                  className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 block text-xs">Literacy Status</span>
                  <span className="text-[11px] text-slate-500 block">Can read & write with understanding</span>
                </div>
              </label>
            </div>

            {/* Employment Status */}
            <div>
              <label htmlFor="census-employment-select" className="block font-semibold text-slate-700 mb-1">
                Economic Activity / Sector
              </label>
              <select
                id="census-employment-select"
                value={employmentStatus}
                onChange={(e) => setEmploymentStatus(e.target.value as EmploymentStatus)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                <option value="Agriculture & Farming">Agriculture & Farming</option>
                <option value="Pastoralism & Livestock">Pastoralism & Livestock</option>
                <option value="Employed (Public/Civil Service)">Employed (Public / Civil Service)</option>
                <option value="Employed (Private Sector)">Employed (Private Sector / NGO)</option>
                <option value="Self-Employed / Business">Self-Employed / Business & Retail</option>
                <option value="Artisan / Trade">Artisan / Trade (Mechanic, Carpentry, Mason)</option>
                <option value="Student">Student (Full-time)</option>
                <option value="Homemaker / Caregiver">Homemaker / Caregiver</option>
                <option value="Unemployed / Seeking Work">Unemployed / Seeking Work</option>
                <option value="Retired / Pensioner">Retired / Pensioner</option>
              </select>
            </div>

            {/* Primary Occupation */}
            <div>
              <label htmlFor="census-occupation-input" className="block font-semibold text-slate-700 mb-1">
                Specific Occupation / Trade Title
              </label>
              <input
                id="census-occupation-input"
                type="text"
                value={primaryOccupation}
                onChange={(e) => setPrimaryOccupation(e.target.value)}
                placeholder="e.g. Sorghum Farmer, Midwife, Teacher"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
            </div>

            {/* Employer / Business Name */}
            <div>
              <label htmlFor="census-employer-input" className="block font-semibold text-slate-700 mb-1">
                Employer / Enterprise Name
              </label>
              <input
                id="census-employer-input"
                type="text"
                value={employerOrBusinessName}
                onChange={(e) => setEmployerOrBusinessName(e.target.value)}
                placeholder="e.g. Ministry of Health, Self-Employed"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
            </div>

            {/* Industry Sector */}
            <div>
              <label htmlFor="census-industry-input" className="block font-semibold text-slate-700 mb-1">
                Industry / Economic Sector
              </label>
              <input
                id="census-industry-input"
                type="text"
                value={industrySector}
                onChange={(e) => setIndustrySector(e.target.value)}
                placeholder="e.g. Healthcare, Agriculture, Logistics"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
            </div>

            {/* Monthly Income Bracket */}
            <div>
              <label htmlFor="census-income-select" className="block font-semibold text-slate-700 mb-1">
                Estimated Monthly Income (SSP)
              </label>
              <select
                id="census-income-select"
                value={monthlyIncomeRange}
                onChange={(e) => setMonthlyIncomeRange(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              >
                <option value="No Direct Cash Income">No Direct Cash Income / Subsistence</option>
                <option value="Under SSP 50,000">Under SSP 50,000</option>
                <option value="SSP 50,000 - 150,000">SSP 50,000 - 150,000</option>
                <option value="SSP 150,000 - 400,000">SSP 150,000 - 400,000</option>
                <option value="SSP 400,000 - 1,000,000">SSP 400,000 - 1,000,000</option>
                <option value="Over SSP 1,000,000">Over SSP 1,000,000</option>
              </select>
            </div>

            {/* Special Needs */}
            <div>
              <label className="flex items-center gap-2.5 p-3 rounded-lg bg-amber-50/50 border border-amber-200 cursor-pointer w-full mt-1">
                <input
                  id="census-special-needs-checkbox"
                  type="checkbox"
                  checked={hasSpecialNeedsOrDisability}
                  onChange={(e) => setHasSpecialNeedsOrDisability(e.target.checked)}
                  className="w-4 h-4 text-amber-600 rounded border-slate-300 focus:ring-amber-500"
                />
                <div>
                  <span className="font-semibold text-slate-900 block text-xs">Special Needs / Disability</span>
                  <span className="text-[11px] text-slate-500 block">Requires specialized social support</span>
                </div>
              </label>
            </div>

            {hasSpecialNeedsOrDisability && (
              <div className="lg:col-span-3">
                <label htmlFor="census-disability-input" className="block font-semibold text-amber-800 mb-1">
                  Describe Disability / Special Assistance Type
                </label>
                <input
                  id="census-disability-input"
                  type="text"
                  value={disabilityType}
                  onChange={(e) => setDisabilityType(e.target.value)}
                  placeholder="e.g. Visual impairment, mobility assistance required, hearing difficulty"
                  className="w-full px-3.5 py-2 rounded-lg border border-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-600 text-slate-900 bg-white placeholder:text-slate-400"
                />
              </div>
            )}
          </div>
        </div>

        {/* Section 6: Electoral Roll & Voter Registration */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-purple-900 text-white text-xs flex items-center justify-center font-bold">6</span>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
                Electoral Roll & Voter Registration Credentials
              </h3>
              <span className="text-[10px] font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200">
                General Elections Integration
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-purple-50/40 border border-purple-200/80 space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-700">
                Statutory Voting Qualification (18+ Citizen):
              </span>
              {(typeof age === 'number' && age >= 18) ? (
                <span className="px-2.5 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Eligible for Electoral Roll
                </span>
              ) : (
                <span className="px-2.5 py-0.5 rounded-full font-bold bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Under Legal Voting Age ({typeof age === 'number' ? age : 0} &lt; 18)
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs sm:text-sm">
              {/* Voter Registration Number */}
              <div>
                <label htmlFor="census-vrn-input" className="block font-semibold text-slate-700 mb-1">
                  Voter Registration No. (VRN)
                </label>
                <input
                  id="census-vrn-input"
                  type="text"
                  value={voterIdNumber}
                  onChange={(e) => setVoterIdNumber(e.target.value)}
                  placeholder="Auto-generated (e.g. VRN-2026-881204)"
                  className="w-full px-3.5 py-2 rounded-lg border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-700 text-slate-900 bg-white font-mono"
                />
              </div>

              {/* Polling Station Assignment */}
              <div className="lg:col-span-2">
                <label htmlFor="census-ps-select" className="block font-semibold text-slate-700 mb-1">
                  Assigned Polling Station Center
                </label>
                <select
                  id="census-ps-select"
                  value={pollingStationId}
                  onChange={(e) => setPollingStationId(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-lg border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-700 text-slate-900 bg-white"
                >
                  {OFFICIAL_POLLING_STATIONS.map((ps) => (
                    <option key={ps.id} value={ps.id}>
                      {ps.code} - {ps.name} ({ps.constituency})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Section 7: Enumerator & Field Log */}
        <div>
          <div className="flex items-center gap-2 mb-4 pb-1 border-b border-slate-100">
            <span className="w-6 h-6 rounded-full bg-slate-700 text-white text-xs flex items-center justify-center font-bold">7</span>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase">
              Enumerator Sign-off & Verification Status
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs sm:text-sm">
            <div>
              <label htmlFor="census-enum-name-input" className="block font-semibold text-slate-700 mb-1">
                Enumerator Name
              </label>
              <input
                id="census-enum-name-input"
                type="text"
                value={enumeratorName}
                onChange={(e) => setEnumeratorName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white font-medium"
              />
            </div>

            <div>
              <label htmlFor="census-enum-badge-input" className="block font-semibold text-slate-700 mb-1">
                Badge / Agent ID
              </label>
              <input
                id="census-enum-badge-input"
                type="text"
                value={enumeratorBadgeId}
                onChange={(e) => setEnumeratorBadgeId(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white font-mono"
              />
            </div>

            <div>
              <label htmlFor="census-enum-date-input" className="block font-semibold text-slate-700 mb-1">
                Enumeration Date
              </label>
              <input
                id="census-enum-date-input"
                type="date"
                value={enumerationDate}
                onChange={(e) => setEnumerationDate(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white"
              />
            </div>

            <div>
              <label htmlFor="census-verification-select" className="block font-semibold text-slate-700 mb-1">
                Quality Verification
              </label>
              <select
                id="census-verification-select"
                value={verificationStatus}
                onChange={(e) => setVerificationStatus(e.target.value as VerificationStatus)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white font-medium"
              >
                <option value="Verified">Verified (Complete)</option>
                <option value="Pending Review">Pending Supervisor Review</option>
                <option value="Flagged">Flagged for Re-visit</option>
              </select>
            </div>

            <div className="sm:col-span-2 lg:col-span-4">
              <label htmlFor="census-notes-input" className="block font-semibold text-slate-700 mb-1">
                Field Enumerator Observation Notes
              </label>
              <textarea
                id="census-notes-input"
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Optional comments regarding household structure, language dialect, or landmark..."
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-slate-900 bg-white placeholder:text-slate-400"
              />
            </div>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-500">
            * All recorded particulars are strictly protected under the National Statistics & Population Act.
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            {onCancel && (
              <button
                id="census-form-cancel-bottom-btn"
                type="button"
                onClick={onCancel}
                className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 font-semibold text-xs sm:text-sm transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              id="census-form-submit-btn"
              type="submit"
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs sm:text-sm shadow-md transition-all active:scale-[0.99]"
            >
              <Save className="w-4 h-4 text-emerald-400" />
              {existingRecord ? 'Update Record' : 'Save & Register Individual'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
