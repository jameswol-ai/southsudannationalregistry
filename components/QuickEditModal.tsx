'use client';

import React, { useState, useEffect } from 'react';
import { CensusRecord, Gender, MaritalStatus, EducationLevel, EmploymentStatus, HouseholdRole, VerificationStatus } from '@/lib/types';
import { COMMON_TRIBES, COMMON_REGIONS, COMMON_LANGUAGES } from '@/lib/initialData';
import { OFFICIAL_POLLING_STATIONS } from '@/lib/electionData';
import { getStoredAdministrativeUnits } from '@/lib/administrativeData';
import { 
  X, 
  Save, 
  User, 
  MapPin, 
  Home, 
  Briefcase, 
  ShieldCheck, 
  Vote, 
  CheckCircle2, 
  AlertCircle
} from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  record: CensusRecord | null;
  onSave: (updatedRecord: CensusRecord) => void;
}

export const QuickEditModal: React.FC<Props> = ({
  isOpen,
  onClose,
  record,
  onSave
}) => {
  if (!isOpen || !record) return null;

  return (
    <QuickEditModalContent
      key={record.id}
      isOpen={isOpen}
      onClose={onClose}
      record={record}
      onSave={onSave}
    />
  );
};

const QuickEditModalContent: React.FC<Props & { record: CensusRecord }> = ({
  onClose,
  record,
  onSave
}) => {
  const [formData, setFormData] = useState<Partial<CensusRecord>>(() => ({ ...record }));
  const [activeSection, setActiveSection] = useState<'demographics' | 'contact' | 'location' | 'household' | 'socioeconomic' | 'electoral'>('demographics');
  const [successNotice, setSuccessNotice] = useState(false);
  const [errorNotice, setErrorNotice] = useState<string | null>(null);

  // Administrative units for dynamic dropdown options
  const adminUnits = getStoredAdministrativeUnits();
  const states = Array.from(new Set([...COMMON_REGIONS, ...adminUnits.filter(u => u.type === 'State').map(u => u.name)]));
  
  const currentCounties = adminUnits
    .filter(u => u.type === 'County' && (!formData.stateOrRegion || u.stateOrRegion === formData.stateOrRegion || u.parentName === formData.stateOrRegion))
    .map(u => u.name);

  const currentPayams = adminUnits
    .filter(u => u.type === 'Payam' && (!formData.countyOrPayam || u.countyOrPayam === formData.countyOrPayam || u.parentName === formData.countyOrPayam))
    .map(u => u.name);

  const currentBomas = adminUnits
    .filter(u => u.type === 'Boma' && (!formData.subCountyOrBoma || u.subCountyOrBoma === formData.subCountyOrBoma || u.parentName === formData.subCountyOrBoma))
    .map(u => u.name);

  const handleChange = (field: keyof CensusRecord, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.fullName?.trim()) {
      setErrorNotice('Full Name is required.');
      return;
    }

    const currentAge = typeof formData.age === 'number' ? formData.age : 0;
    const isCitizen = (formData.nationality || '').toLowerCase().includes('south sudan');
    const isEligible = currentAge >= 18 && isCitizen;

    const updated: CensusRecord = {
      ...record,
      ...(formData as CensusRecord),
      fullName: formData.fullName.trim(),
      age: currentAge,
      voterStatus: isEligible ? (formData.voterStatus || 'Registered') : 'Ineligible',
      voterIdNumber: isEligible 
        ? (formData.voterIdNumber || `VRN-2026-${Math.floor(100000 + Math.random() * 900000)}`) 
        : undefined,
      updatedAt: new Date().toISOString()
    };

    onSave(updated);
    setSuccessNotice(true);
    setTimeout(() => {
      onClose();
    }, 400);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs overflow-y-auto">
      <div 
        id="quick-edit-modal"
        className="w-full max-w-3xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh] my-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-xs">
              EDIT
            </div>
            <div>
              <h3 className="font-bold text-sm tracking-wide">
                Edit Record: {record.fullName}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                ID: {record.id} &bull; Household: {record.householdId}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Section Tabs */}
        <div className="flex border-b border-slate-200 bg-slate-50 px-6 gap-1 overflow-x-auto shrink-0">
          <button
            type="button"
            onClick={() => setActiveSection('demographics')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'demographics'
                ? 'border-emerald-600 text-emerald-800 bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <User className="w-3.5 h-3.5" />
            Demographics & ID
          </button>

          <button
            type="button"
            onClick={() => setActiveSection('contact')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'contact'
                ? 'border-emerald-600 text-emerald-800 bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            Contact & Emergency
          </button>

          <button
            type="button"
            onClick={() => setActiveSection('location')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'location'
                ? 'border-emerald-600 text-emerald-800 bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <MapPin className="w-3.5 h-3.5" />
            County, Payam & Boma
          </button>

          <button
            type="button"
            onClick={() => setActiveSection('household')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'household'
                ? 'border-emerald-600 text-emerald-800 bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Home className="w-3.5 h-3.5" />
            Household Unit
          </button>

          <button
            type="button"
            onClick={() => setActiveSection('socioeconomic')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'socioeconomic'
                ? 'border-emerald-600 text-emerald-800 bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            Education & Occupation
          </button>

          <button
            type="button"
            onClick={() => setActiveSection('electoral')}
            className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'electoral'
                ? 'border-emerald-600 text-emerald-800 bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Vote className="w-3.5 h-3.5" />
            Electoral Roll
          </button>
        </div>

        {/* Scrollable Form Body */}
        <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-4">
          {errorNotice && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{errorNotice}</span>
            </div>
          )}

          {successNotice && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Record updated successfully!</span>
            </div>
          )}

          {/* Demographics & ID Tab */}
          {activeSection === 'demographics' && (
            <div className="space-y-4 text-xs sm:text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="quick-edit-name" className="block font-semibold text-slate-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    id="quick-edit-name"
                    type="text"
                    required
                    value={formData.fullName || ''}
                    onChange={(e) => handleChange('fullName', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-idtype" className="block font-semibold text-slate-700 mb-1">
                    Identification Document Type
                  </label>
                  <select
                    id="quick-edit-idtype"
                    value={formData.idDocumentType || 'National ID'}
                    onChange={(e) => handleChange('idDocumentType', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="National ID">National ID Card</option>
                    <option value="Passport">Passport</option>
                    <option value="Birth Certificate">Birth Certificate</option>
                    <option value="Refugee / Alien Registration">Refugee / Alien Registration</option>
                    <option value="Voter Card">Voter Card</option>
                    <option value="Other">Other / None</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-nationalid" className="block font-semibold text-slate-700 mb-1">
                    National ID Number
                  </label>
                  <input
                    id="quick-edit-nationalid"
                    type="text"
                    value={formData.nationalId || ''}
                    onChange={(e) => handleChange('nationalId', e.target.value)}
                    placeholder="e.g. SS-98214301-A"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-passport" className="block font-semibold text-slate-700 mb-1">
                    Passport Number
                  </label>
                  <input
                    id="quick-edit-passport"
                    type="text"
                    value={formData.passportNumber || ''}
                    onChange={(e) => handleChange('passportNumber', e.target.value)}
                    placeholder="e.g. P-SS882001"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-age" className="block font-semibold text-slate-700 mb-1">
                    Age (Years)
                  </label>
                  <input
                    id="quick-edit-age"
                    type="number"
                    min="0"
                    max="120"
                    value={formData.age ?? ''}
                    onChange={(e) => handleChange('age', parseInt(e.target.value, 10) || 0)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-dob" className="block font-semibold text-slate-700 mb-1">
                    Date of Birth
                  </label>
                  <input
                    id="quick-edit-dob"
                    type="date"
                    value={formData.dateOfBirth || ''}
                    onChange={(e) => handleChange('dateOfBirth', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-gender" className="block font-semibold text-slate-700 mb-1">
                    Gender
                  </label>
                  <select
                    id="quick-edit-gender"
                    value={formData.gender || 'Male'}
                    onChange={(e) => handleChange('gender', e.target.value as Gender)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-marital" className="block font-semibold text-slate-700 mb-1">
                    Marital Status
                  </label>
                  <select
                    id="quick-edit-marital"
                    value={formData.maritalStatus || 'Single'}
                    onChange={(e) => handleChange('maritalStatus', e.target.value as MaritalStatus)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="Single">Single</option>
                    <option value="Married">Married</option>
                    <option value="Widowed">Widowed</option>
                    <option value="Divorced">Divorced</option>
                    <option value="Separated">Separated</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-tribe" className="block font-semibold text-slate-700 mb-1">
                    Tribe / Ethnic Origin
                  </label>
                  <select
                    id="quick-edit-tribe"
                    value={formData.tribe || COMMON_TRIBES[0]}
                    onChange={(e) => handleChange('tribe', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    {COMMON_TRIBES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-language" className="block font-semibold text-slate-700 mb-1">
                    Native Language
                  </label>
                  <select
                    id="quick-edit-language"
                    value={formData.nativeLanguage || COMMON_LANGUAGES[0]}
                    onChange={(e) => handleChange('nativeLanguage', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    {COMMON_LANGUAGES.map(l => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-nationality" className="block font-semibold text-slate-700 mb-1">
                    Nationality / Citizenship
                  </label>
                  <input
                    id="quick-edit-nationality"
                    type="text"
                    value={formData.nationality || 'South Sudan'}
                    onChange={(e) => handleChange('nationality', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Contact Details Tab */}
          {activeSection === 'contact' && (
            <div className="space-y-4 text-xs sm:text-sm">
              <div className="p-3 bg-emerald-50/50 border border-emerald-200 rounded-xl">
                <span className="font-semibold text-emerald-900 block text-xs">
                  Direct Citizen Contact & Emergency Notification
                </span>
                <span className="text-[11px] text-emerald-700">
                  Used for official census verification notices and electoral polling notifications.
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="quick-edit-phone" className="block font-semibold text-slate-700 mb-1">
                    Primary Phone Number
                  </label>
                  <input
                    id="quick-edit-phone"
                    type="tel"
                    value={formData.phoneNumber || ''}
                    onChange={(e) => handleChange('phoneNumber', e.target.value)}
                    placeholder="e.g. +211 912 345 678"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-email" className="block font-semibold text-slate-700 mb-1">
                    Email Address
                  </label>
                  <input
                    id="quick-edit-email"
                    type="email"
                    value={formData.emailAddress || ''}
                    onChange={(e) => handleChange('emailAddress', e.target.value)}
                    placeholder="e.g. citizen@example.com"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-emg-name" className="block font-semibold text-slate-700 mb-1">
                    Emergency Contact / Next of Kin Name
                  </label>
                  <input
                    id="quick-edit-emg-name"
                    type="text"
                    value={formData.emergencyContactName || ''}
                    onChange={(e) => handleChange('emergencyContactName', e.target.value)}
                    placeholder="e.g. Mary Chol Deng"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-emg-phone" className="block font-semibold text-slate-700 mb-1">
                    Emergency Contact Phone Number
                  </label>
                  <input
                    id="quick-edit-emg-phone"
                    type="tel"
                    value={formData.emergencyContactPhone || ''}
                    onChange={(e) => handleChange('emergencyContactPhone', e.target.value)}
                    placeholder="e.g. +211 922 991 405"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Location Tab: State, County, Payam, Boma, Community */}
          {activeSection === 'location' && (
            <div className="space-y-4 text-xs sm:text-sm">
              <div className="p-3 bg-blue-50/50 border border-blue-200 rounded-xl">
                <span className="font-semibold text-blue-900 block text-xs">
                  Administrative Hierarchy Structure
                </span>
                <span className="text-[11px] text-blue-700">
                  State &rarr; County &rarr; Payam &rarr; Boma &rarr; Community / Settlement
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="quick-edit-state" className="block font-semibold text-slate-700 mb-1">
                    State / Region *
                  </label>
                  <select
                    id="quick-edit-state"
                    value={formData.stateOrRegion || states[0]}
                    onChange={(e) => handleChange('stateOrRegion', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    {states.map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-county" className="block font-semibold text-slate-700 mb-1">
                    County / Municipality *
                  </label>
                  <input
                    id="quick-edit-county"
                    type="text"
                    list="quick-counties-list"
                    value={formData.countyOrPayam || ''}
                    onChange={(e) => handleChange('countyOrPayam', e.target.value)}
                    placeholder="e.g. Juba County"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                  <datalist id="quick-counties-list">
                    {currentCounties.map(c => (
                      <option key={c} value={c} />
                    ))}
                  </datalist>
                </div>

                <div>
                  <label htmlFor="quick-edit-payam" className="block font-semibold text-slate-700 mb-1">
                    Payam (Sub-County)
                  </label>
                  <input
                    id="quick-edit-payam"
                    type="text"
                    list="quick-payams-list"
                    value={formData.subCountyOrBoma || ''}
                    onChange={(e) => handleChange('subCountyOrBoma', e.target.value)}
                    placeholder="e.g. Munuki Payam"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                  <datalist id="quick-payams-list">
                    {currentPayams.map(p => (
                      <option key={p} value={p} />
                    ))}
                  </datalist>
                </div>

                <div>
                  <label htmlFor="quick-edit-boma" className="block font-semibold text-slate-700 mb-1">
                    Boma / Ward
                  </label>
                  <input
                    id="quick-edit-boma"
                    type="text"
                    list="quick-bomas-list"
                    value={formData.boma || ''}
                    onChange={(e) => handleChange('boma', e.target.value)}
                    placeholder="e.g. Munuki Block A"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                  <datalist id="quick-bomas-list">
                    {currentBomas.map(b => (
                      <option key={b} value={b} />
                    ))}
                  </datalist>
                </div>

                <div>
                  <label htmlFor="quick-edit-community" className="block font-semibold text-slate-700 mb-1">
                    Community / Settlement / Quarter
                  </label>
                  <input
                    id="quick-edit-community"
                    type="text"
                    value={formData.community || ''}
                    onChange={(e) => handleChange('community', e.target.value)}
                    placeholder="e.g. Munuki Residential Area"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-stayyears" className="block font-semibold text-slate-700 mb-1">
                    Years Lived in Community
                  </label>
                  <input
                    id="quick-edit-stayyears"
                    type="number"
                    min="0"
                    max="100"
                    value={formData.durationOfStayYears ?? ''}
                    onChange={(e) => handleChange('durationOfStayYears', parseInt(e.target.value, 10) || 0)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label htmlFor="quick-edit-address" className="block font-semibold text-slate-700 mb-1">
                    Specific Residential Address / House / Plot
                  </label>
                  <input
                    id="quick-edit-address"
                    type="text"
                    value={formData.residentialAddress || ''}
                    onChange={(e) => handleChange('residentialAddress', e.target.value)}
                    placeholder="e.g. Plot 142, Street 8, Munuki Block B"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Household Tab */}
          {activeSection === 'household' && (
            <div className="space-y-4 text-xs sm:text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="quick-edit-hhid" className="block font-semibold text-slate-700 mb-1">
                    Household ID (HH-XXX)
                  </label>
                  <input
                    id="quick-edit-hhid"
                    type="text"
                    value={formData.householdId || ''}
                    onChange={(e) => handleChange('householdId', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono font-bold"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-hhrole" className="block font-semibold text-slate-700 mb-1">
                    Role in Household
                  </label>
                  <select
                    id="quick-edit-hhrole"
                    value={formData.householdRole || 'Head of Household'}
                    onChange={(e) => {
                      const role = e.target.value as HouseholdRole;
                      handleChange('householdRole', role);
                      handleChange('isHouseholdHead', role === 'Head of Household');
                    }}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="Head of Household">Head of Household</option>
                    <option value="Spouse">Spouse</option>
                    <option value="Son / Daughter">Son / Daughter</option>
                    <option value="Parent / Parent-in-law">Parent / Parent-in-law</option>
                    <option value="Grandchild">Grandchild</option>
                    <option value="Other Relative">Other Relative</option>
                    <option value="Non-Relative / Resident">Non-Relative / Resident</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.isHouseholdHead || false}
                      onChange={(e) => handleChange('isHouseholdHead', e.target.checked)}
                      className="w-4 h-4 text-emerald-600 rounded"
                    />
                    <span className="font-semibold text-slate-800">
                      Citizen is the Primary Head of this Household
                    </span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Socioeconomic & Occupation Tab */}
          {activeSection === 'socioeconomic' && (
            <div className="space-y-4 text-xs sm:text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="quick-edit-education" className="block font-semibold text-slate-700 mb-1">
                    Highest Educational Attainment
                  </label>
                  <select
                    id="quick-edit-education"
                    value={formData.educationLevel || 'Secondary Education'}
                    onChange={(e) => handleChange('educationLevel', e.target.value as EducationLevel)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="None / Informal">None / Informal</option>
                    <option value="Primary Education">Primary Education</option>
                    <option value="Secondary Education">Secondary Education</option>
                    <option value="Vocational / Diploma">Vocational / Diploma</option>
                    <option value="Tertiary / Bachelor Degree">Tertiary / Bachelor Degree</option>
                    <option value="Post-Graduate (Master/PhD)">Post-Graduate (Master/PhD)</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-employment" className="block font-semibold text-slate-700 mb-1">
                    Employment / Livelihood Status
                  </label>
                  <select
                    id="quick-edit-employment"
                    value={formData.employmentStatus || 'Self-Employed / Business'}
                    onChange={(e) => handleChange('employmentStatus', e.target.value as EmploymentStatus)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="Employed (Public/Civil Service)">Employed (Public/Civil Service)</option>
                    <option value="Employed (Private Sector)">Employed (Private Sector)</option>
                    <option value="Self-Employed / Business">Self-Employed / Business</option>
                    <option value="Agriculture & Farming">Agriculture & Farming</option>
                    <option value="Pastoralism & Livestock">Pastoralism & Livestock</option>
                    <option value="Artisan / Trade">Artisan / Trade</option>
                    <option value="Student">Student</option>
                    <option value="Unemployed / Seeking Work">Unemployed / Seeking Work</option>
                    <option value="Homemaker / Caregiver">Homemaker / Caregiver</option>
                    <option value="Retired / Pensioner">Retired / Pensioner</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-occupation" className="block font-semibold text-slate-700 mb-1">
                    Primary Profession / Occupation
                  </label>
                  <input
                    id="quick-edit-occupation"
                    type="text"
                    value={formData.primaryOccupation || ''}
                    onChange={(e) => handleChange('primaryOccupation', e.target.value)}
                    placeholder="e.g. Senior Teacher, Agronomist, Trader"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-employer" className="block font-semibold text-slate-700 mb-1">
                    Employer or Business Name
                  </label>
                  <input
                    id="quick-edit-employer"
                    type="text"
                    value={formData.employerOrBusinessName || ''}
                    onChange={(e) => handleChange('employerOrBusinessName', e.target.value)}
                    placeholder="e.g. Ministry of Agriculture / Nile Supplies Ltd"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-industry" className="block font-semibold text-slate-700 mb-1">
                    Industry Sector
                  </label>
                  <input
                    id="quick-edit-industry"
                    type="text"
                    value={formData.industrySector || ''}
                    onChange={(e) => handleChange('industrySector', e.target.value)}
                    placeholder="e.g. Education, Health, Commerce, Logistics"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-income" className="block font-semibold text-slate-700 mb-1">
                    Monthly Income Bracket
                  </label>
                  <select
                    id="quick-edit-income"
                    value={formData.monthlyIncomeRange || 'SSP 50,000 - 150,000'}
                    onChange={(e) => handleChange('monthlyIncomeRange', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="Under SSP 20,000">Under SSP 20,000</option>
                    <option value="SSP 20,000 - 50,000">SSP 20,000 - 50,000</option>
                    <option value="SSP 50,000 - 150,000">SSP 50,000 - 150,000</option>
                    <option value="SSP 150,000 - 350,000">SSP 150,000 - 350,000</option>
                    <option value="Over SSP 350,000">Over SSP 350,000</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.hasSpecialNeedsOrDisability || false}
                      onChange={(e) => handleChange('hasSpecialNeedsOrDisability', e.target.checked)}
                      className="w-4 h-4 text-emerald-600 rounded"
                    />
                    <span className="font-semibold text-slate-800">
                      Has Special Needs, Physical Disability, or Impairment
                    </span>
                  </label>
                </div>

                {formData.hasSpecialNeedsOrDisability && (
                  <div className="sm:col-span-2">
                    <label htmlFor="quick-edit-disability" className="block font-semibold text-slate-700 mb-1">
                      Disability Specifics / Assistive Devices
                    </label>
                    <input
                      id="quick-edit-disability"
                      type="text"
                      value={formData.disabilityType || ''}
                      onChange={(e) => handleChange('disabilityType', e.target.value)}
                      placeholder="e.g. Visual Impairment, Mobility / Wheelchair"
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Electoral Tab */}
          {activeSection === 'electoral' && (
            <div className="space-y-4 text-xs sm:text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="quick-edit-vrn" className="block font-semibold text-slate-700 mb-1">
                    Voter Registration Number (VRN)
                  </label>
                  <input
                    id="quick-edit-vrn"
                    type="text"
                    value={formData.voterIdNumber || ''}
                    onChange={(e) => handleChange('voterIdNumber', e.target.value)}
                    placeholder="e.g. VRN-2026-881204"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono"
                  />
                </div>

                <div>
                  <label htmlFor="quick-edit-voterstatus" className="block font-semibold text-slate-700 mb-1">
                    Voter Status
                  </label>
                  <select
                    id="quick-edit-voterstatus"
                    value={formData.voterStatus || 'Registered'}
                    onChange={(e) => handleChange('voterStatus', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    <option value="Registered">Registered & Active</option>
                    <option value="Eligible">Eligible (Unregistered)</option>
                    <option value="Ineligible">Ineligible (Underage / Non-citizen)</option>
                    <option value="Suspended">Suspended</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label htmlFor="quick-edit-polling" className="block font-semibold text-slate-700 mb-1">
                    Assigned Polling Station
                  </label>
                  <select
                    id="quick-edit-polling"
                    value={formData.pollingStationId || OFFICIAL_POLLING_STATIONS[0].id}
                    onChange={(e) => {
                      const selected = OFFICIAL_POLLING_STATIONS.find(p => p.id === e.target.value);
                      if (selected) {
                        handleChange('pollingStationId', selected.id);
                        handleChange('pollingStationName', selected.name);
                        handleChange('constituency', selected.constituency);
                      }
                    }}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                  >
                    {OFFICIAL_POLLING_STATIONS.map(ps => (
                      <option key={ps.id} value={ps.id}>
                        {ps.code} - {ps.name} ({ps.constituency})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="quick-edit-verification" className="block font-semibold text-slate-700 mb-1">
                    Census Verification Status
                  </label>
                  <select
                    id="quick-edit-verification"
                    value={formData.verificationStatus || 'Verified'}
                    onChange={(e) => handleChange('verificationStatus', e.target.value as VerificationStatus)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white font-semibold"
                  >
                    <option value="Verified">Verified Official</option>
                    <option value="Pending Review">Pending Field Review</option>
                    <option value="Flagged">Flagged / Needs Audit</option>
                  </select>
                </div>

                <div>
                  <label className="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer mt-5">
                    <input
                      type="checkbox"
                      checked={formData.hasVoted || false}
                      onChange={(e) => handleChange('hasVoted', e.target.checked)}
                      className="w-4 h-4 text-emerald-600 rounded"
                    />
                    <span className="font-semibold text-slate-800">
                      Has Cast Official Ballot on Election Day
                    </span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-5 py-2 text-xs font-bold text-white bg-emerald-700 hover:bg-emerald-800 rounded-xl shadow-sm transition-all"
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

