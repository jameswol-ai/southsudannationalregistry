'use client';

import React, { useState } from 'react';
import { CensusRecord, Gender, MaritalStatus, EducationLevel, EmploymentStatus } from '@/lib/types';
import { COMMON_TRIBES, COMMON_COMMUNITIES, COMMON_REGIONS } from '@/lib/initialData';
import { generateCensusId, generateHouseholdId } from '@/lib/storage';
import { 
  Zap, 
  UserPlus, 
  CheckCircle2, 
  MapPin, 
  Sparkles, 
  Building2, 
  ShieldCheck, 
  Lock 
} from 'lucide-react';

interface Props {
  existingRecords: CensusRecord[];
  onSaveRecord: (record: CensusRecord) => void;
}

export const FieldQuickMode: React.FC<Props> = ({ existingRecords, onSaveRecord }) => {
  // Sticky Field Settings (Persists between entries)
  const [lockedLocation, setLockedLocation] = useState(true);
  const [community, setCommunity] = useState(COMMON_COMMUNITIES[0]);
  const [stateOrRegion, setStateOrRegion] = useState(COMMON_REGIONS[0]);
  const [subCountyOrBoma, setSubCountyOrBoma] = useState('Central Boma');
  const [countyOrPayam, setCountyOrPayam] = useState('Urban Payam');
  const [enumeratorName, setEnumeratorName] = useState('Grace Kiden Taban');
  const [enumeratorBadgeId, setEnumeratorBadgeId] = useState('ENUM-042');

  // Active Individual Entry Form
  const [householdId, setHouseholdId] = useState('HH-001');
  const [isNewHousehold, setIsNewHousehold] = useState(false);
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState<number | ''>(30);
  const [gender, setGender] = useState<Gender>('Male');
  const [maritalStatus, setMaritalStatus] = useState<MaritalStatus>('Married');
  const [tribe, setTribe] = useState(COMMON_TRIBES[0]);
  const [nativeLanguage, setNativeLanguage] = useState('Dinka (Thuɔŋjäŋ)');
  const [isHouseholdHead, setIsHouseholdHead] = useState(false);
  const [educationLevel, setEducationLevel] = useState<EducationLevel>('Secondary Education');
  const [employmentStatus, setEmploymentStatus] = useState<EmploymentStatus>('Agriculture & Farming');
  const [primaryOccupation, setPrimaryOccupation] = useState('');
  const [recentSaved, setRecentSaved] = useState<CensusRecord[]>([]);

  const handleNextHousehold = () => {
    const nextHh = generateHouseholdId([...existingRecords, ...recentSaved]);
    setHouseholdId(nextHh);
    setIsHouseholdHead(true);
  };

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) return;

    const now = new Date().toISOString();
    const newRecord: CensusRecord = {
      id: generateCensusId(),
      fullName: fullName.trim(),
      age: typeof age === 'number' ? age : 0,
      gender,
      maritalStatus,
      tribe,
      nativeLanguage,
      nationality: 'South Sudan',
      community,
      subCountyOrBoma,
      countyOrPayam,
      stateOrRegion,
      durationOfStayYears: 10,
      householdId: householdId.trim() || 'HH-001',
      householdRole: isHouseholdHead ? 'Head of Household' : 'Son / Daughter',
      isHouseholdHead,
      educationLevel,
      isLiterate: educationLevel !== 'None / Informal',
      employmentStatus,
      primaryOccupation: primaryOccupation.trim() || undefined,
      hasSpecialNeedsOrDisability: false,
      enumeratorName,
      enumeratorBadgeId,
      enumerationDate: now.split('T')[0],
      verificationStatus: 'Verified',
      createdAt: now,
      updatedAt: now
    };

    onSaveRecord(newRecord);
    setRecentSaved(prev => [newRecord, ...prev]);

    // Reset input fields for next person
    setFullName('');
    setAge(25);
    setPrimaryOccupation('');
    if (isHouseholdHead) {
      setIsHouseholdHead(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Sticky Location Banner */}
      <div className="bg-slate-900 text-white rounded-2xl p-5 border border-slate-800 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-amber-400 uppercase tracking-widest">
                Rapid Field Enumerator Mode
              </div>
              <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
                Sticky Location & Badge Presets
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              Locked for Batch Entry
            </span>
          </div>
        </div>

        {/* Sticky Fields Grid */}
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-slate-400 mb-1 font-semibold uppercase text-[10px]">
              Community / Settlement
            </label>
            <select
              value={community}
              onChange={(e) => setCommunity(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:ring-1 focus:ring-amber-400"
            >
              {COMMON_COMMUNITIES.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold uppercase text-[10px]">
              State / Region
            </label>
            <select
              value={stateOrRegion}
              onChange={(e) => setStateOrRegion(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:ring-1 focus:ring-amber-400"
            >
              {COMMON_REGIONS.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold uppercase text-[10px]">
              Enumerator Name
            </label>
            <input
              type="text"
              value={enumeratorName}
              onChange={(e) => setEnumeratorName(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:ring-1 focus:ring-amber-400"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold uppercase text-[10px]">
              Badge ID
            </label>
            <input
              type="text"
              value={enumeratorBadgeId}
              onChange={(e) => setEnumeratorBadgeId(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:ring-1 focus:ring-amber-400 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Main Entry & Session Roster */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Fast Form (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
              <UserPlus className="w-4 h-4 text-emerald-600" />
              Quick Person Entry
            </h3>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleNextHousehold}
                className="px-2.5 py-1 text-xs font-semibold bg-purple-50 text-purple-800 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
              >
                + New Household ID
              </button>
            </div>
          </div>

          <form onSubmit={handleQuickSubmit} className="space-y-4 text-xs sm:text-sm">
            {/* Household & Head */}
            <div className="grid grid-cols-2 gap-3 bg-purple-50/50 p-3 rounded-xl border border-purple-100">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Active Household Code
                </label>
                <input
                  type="text"
                  required
                  value={householdId}
                  onChange={(e) => setHouseholdId(e.target.value.toUpperCase())}
                  className="w-full px-3 py-1.5 rounded-lg border border-purple-300 bg-white font-mono font-bold text-purple-950"
                />
              </div>

              <div className="flex items-center pt-5">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isHouseholdHead}
                    onChange={(e) => setIsHouseholdHead(e.target.checked)}
                    className="w-4 h-4 text-purple-600 rounded"
                  />
                  <span className="font-semibold text-slate-800 text-xs">
                    Is Household Head
                  </span>
                </label>
              </div>
            </div>

            {/* Name and Age */}
            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <label className="block font-semibold text-slate-700 mb-1">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Dut Deng Akech"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Age (Years) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="120"
                  required
                  value={age}
                  onChange={(e) => setAge(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-slate-900"
                />
              </div>
            </div>

            {/* Gender & Marital */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Gender</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value as Gender)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Marital Status</label>
                <select
                  value={maritalStatus}
                  onChange={(e) => setMaritalStatus(e.target.value as MaritalStatus)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
                >
                  <option value="Single">Single</option>
                  <option value="Married">Married</option>
                  <option value="Widowed">Widowed</option>
                  <option value="Divorced">Divorced</option>
                </select>
              </div>
            </div>

            {/* Tribe & Language */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Tribe</label>
                <select
                  value={tribe}
                  onChange={(e) => setTribe(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white font-medium"
                >
                  {COMMON_TRIBES.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Education Level</label>
                <select
                  value={educationLevel}
                  onChange={(e) => setEducationLevel(e.target.value as EducationLevel)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
                >
                  <option value="None / Informal">None / Informal</option>
                  <option value="Primary Education">Primary Education</option>
                  <option value="Secondary Education">Secondary Education</option>
                  <option value="Vocational / Diploma">Vocational / Diploma</option>
                  <option value="Tertiary / Bachelor Degree">Tertiary Degree</option>
                </select>
              </div>
            </div>

            {/* Occupation */}
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Occupation / Trade</label>
              <input
                type="text"
                value={primaryOccupation}
                onChange={(e) => setPrimaryOccupation(e.target.value)}
                placeholder="e.g. Cattle Herder, Market Vendor, Teacher"
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-md transition-colors flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              Save Record & Log Next Person
            </button>
          </form>
        </div>

        {/* Live Session Log (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 flex flex-col h-[520px]">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Session Enumeration Log ({recentSaved.length})
            </h3>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {recentSaved.length === 0 ? (
              <div className="py-16 text-center text-slate-400 text-xs">
                No entries recorded in this session yet. Submit the form on the left to start rapid field logging.
              </div>
            ) : (
              recentSaved.map((r, i) => (
                <div
                  key={r.id}
                  className="p-3 rounded-xl border border-emerald-100 bg-emerald-50/40 text-xs flex items-center justify-between"
                >
                  <div>
                    <div className="font-bold text-slate-900">{r.fullName}</div>
                    <div className="text-slate-500 text-[11px] mt-0.5">
                      {r.age} yrs • {r.gender} • <span className="font-mono text-purple-900 font-semibold">{r.householdId}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-mono text-[10px] font-bold text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {r.id}
                    </span>
                    <div className="text-[10px] text-emerald-700 font-semibold mt-1">
                      {r.tribe}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
