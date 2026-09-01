'use client';

import React from 'react';
import { CensusRecord } from '@/lib/types';
import { 
  X, 
  Printer, 
  ShieldCheck, 
  Building2, 
  User, 
  MapPin, 
  Calendar, 
  Award, 
  FileText, 
  Sparkles 
} from 'lucide-react';

interface Props {
  record: CensusRecord | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (record: CensusRecord) => void;
}

export const CensusCertificateModal: React.FC<Props> = ({
  record,
  isOpen,
  onClose,
  onEdit
}) => {
  if (!isOpen || !record) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs overflow-y-auto">
      <div 
        id="census-certificate-modal"
        className="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden my-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Controls (Hidden in Print) */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white print:hidden">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span className="font-semibold text-sm tracking-wide uppercase">
              Official Census Verification Record
            </span>
          </div>
          <div className="flex items-center gap-3">
            {onEdit && (
              <button
                id="edit-from-certificate-btn"
                type="button"
                onClick={() => {
                  onClose();
                  onEdit(record);
                }}
                className="px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700"
              >
                Edit Details
              </button>
            )}
            <button
              id="print-certificate-btn"
              type="button"
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors shadow-xs"
            >
              <Printer className="w-3.5 h-3.5" />
              Print / Save PDF
            </button>
            <button
              id="close-certificate-btn"
              type="button"
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Certificate / Slip Body (Printable) */}
        <div className="p-8 sm:p-10 bg-white text-slate-900 relative">
          {/* Subtle Watermark Stamp */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.03] select-none">
            <Award className="w-96 h-96 text-slate-900" />
          </div>

          {/* Certificate Header */}
          <div className="border-b-2 border-slate-900 pb-6 mb-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-2xl tracking-tighter shadow-md shrink-0">
                  <span className="text-emerald-400 font-serif">CS</span>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                    National Bureau of Statistics & Demographics
                  </div>
                  <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                    Population Census Enumeration Slip
                  </h2>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Official Individual Demographic Record & Vital Registration
                  </p>
                </div>
              </div>
              <div className="text-left sm:text-right border-l-2 sm:border-l-0 sm:border-r-0 pl-3 sm:pl-0 border-emerald-500">
                <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Census Registration ID
                </div>
                <div className="text-lg font-mono font-bold text-slate-900 tracking-wider">
                  {record.id}
                </div>
                <div className="inline-flex items-center gap-1 mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <ShieldCheck className="w-3 h-3" />
                  {record.verificationStatus}
                </div>
              </div>
            </div>
          </div>

          {/* Main Grid Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 text-sm">
            {/* 1. Personal & Individual Information */}
            <div className="bg-slate-50/80 rounded-xl p-4 border border-slate-200/80 space-y-3">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <User className="w-4 h-4 text-emerald-600" />
                Personal Particulars
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-xs text-slate-500 block">Full Legal Name</span>
                  <span className="font-semibold text-slate-900">{record.fullName}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Primary ID Doc ({record.idDocumentType || 'National ID'})</span>
                  <span className="font-mono font-medium text-slate-800">{record.nationalId || 'N/A (Pending issue)'}</span>
                </div>
                {record.passportNumber && (
                  <div>
                    <span className="text-xs text-slate-500 block">Passport Number</span>
                    <span className="font-mono font-medium text-slate-800">{record.passportNumber}</span>
                  </div>
                )}
                <div>
                  <span className="text-xs text-slate-500 block">Age & Gender</span>
                  <span className="font-medium text-slate-900">{record.age} years • {record.gender}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Marital Status</span>
                  <span className="font-medium text-slate-900">{record.maritalStatus}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Date of Birth</span>
                  <span className="font-medium text-slate-900">{record.dateOfBirth || 'Estimated from Age'}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Nationality</span>
                  <span className="font-medium text-slate-900">{record.nationality}</span>
                </div>
                {record.phoneNumber && (
                  <div>
                    <span className="text-xs text-slate-500 block">Contact Phone</span>
                    <span className="font-mono font-medium text-slate-800">{record.phoneNumber}</span>
                  </div>
                )}
                {record.emailAddress && (
                  <div>
                    <span className="text-xs text-slate-500 block">Email Address</span>
                    <span className="font-medium text-slate-800">{record.emailAddress}</span>
                  </div>
                )}
              </div>
            </div>

            {/* 2. Cultural & Ethnic Heritage */}
            <div className="bg-slate-50/80 rounded-xl p-4 border border-slate-200/80 space-y-3">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-amber-600" />
                Tribe & Ethnic Heritage
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-xs text-slate-500 block">Tribe / Ethnicity</span>
                  <span className="font-bold text-slate-900 text-base text-emerald-950">{record.tribe}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Sub-Tribe / Clan</span>
                  <span className="font-medium text-slate-900">{record.subTribeOrClan || 'Not Specified'}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Native Language / Mother Tongue</span>
                  <span className="font-medium text-slate-900">{record.nativeLanguage}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Years in Locality</span>
                  <span className="font-medium text-slate-900">{record.durationOfStayYears} years</span>
                </div>
              </div>
            </div>

            {/* 3. Community & Geographic Location */}
            <div className="bg-slate-50/80 rounded-xl p-4 border border-slate-200/80 space-y-3">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <MapPin className="w-4 h-4 text-blue-600" />
                Administrative Hierarchy & Settlement
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-xs text-slate-500 block">State / Region</span>
                  <span className="font-bold text-slate-900">{record.stateOrRegion}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">County / Municipality</span>
                  <span className="font-semibold text-slate-900">{record.countyOrPayam}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Payam (Sub-County)</span>
                  <span className="font-medium text-slate-900">{record.subCountyOrBoma || 'Not Specified'}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Boma / Village Ward</span>
                  <span className="font-medium text-slate-900">{record.boma || 'Central Boma'}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Community / Settlement</span>
                  <span className="font-semibold text-slate-900">{record.community}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Years in Locality</span>
                  <span className="font-medium text-slate-900">{record.durationOfStayYears} years</span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-slate-500 block">Physical Address / Landmark</span>
                  <span className="font-medium text-slate-800">{record.residentialAddress || 'Standard Village Residence'}</span>
                </div>
              </div>
            </div>

            {/* 4. Household & Socioeconomic Details */}
            <div className="bg-slate-50/80 rounded-xl p-4 border border-slate-200/80 space-y-3">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-200 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <Building2 className="w-4 h-4 text-purple-600" />
                Household & Livelihood
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-xs text-slate-500 block">Household Number</span>
                  <span className="font-mono font-bold text-purple-900">{record.householdId}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Family Role</span>
                  <span className="font-semibold text-slate-900">
                    {record.householdRole} {record.isHouseholdHead && '(Head)'}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Education Attainment</span>
                  <span className="font-medium text-slate-900">{record.educationLevel}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Literacy</span>
                  <span className="font-medium text-slate-900">
                    {record.isLiterate ? 'Literate (Can read/write)' : 'Non-Literate'}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-slate-500 block">Employment & Sector</span>
                  <span className="font-medium text-slate-900">
                    {record.employmentStatus}
                    {record.primaryOccupation ? ` — ${record.primaryOccupation}` : ''}
                  </span>
                </div>
                {record.employerOrBusinessName && (
                  <div>
                    <span className="text-xs text-slate-500 block">Employer / Enterprise</span>
                    <span className="font-medium text-slate-800">{record.employerOrBusinessName}</span>
                  </div>
                )}
                {record.monthlyIncomeRange && (
                  <div>
                    <span className="text-xs text-slate-500 block">Monthly Income Range</span>
                    <span className="font-medium text-slate-800">{record.monthlyIncomeRange}</span>
                  </div>
                )}
                {record.hasSpecialNeedsOrDisability && (
                  <div className="col-span-2 bg-amber-50 p-2 rounded text-amber-900 text-xs border border-amber-200">
                    <span className="font-semibold block">Special Needs / Disability Status:</span>
                    {record.disabilityType || 'Assistance requested during field survey.'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Enumeration Sign-off Section */}
          <div className="border-t-2 border-slate-200 pt-6 mt-4 grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs text-slate-600">
            <div>
              <span className="font-semibold text-slate-800 block">Field Enumerator</span>
              <span className="text-slate-900 font-medium">{record.enumeratorName}</span>
              <span className="text-slate-500 block font-mono text-[11px]">Badge: {record.enumeratorBadgeId}</span>
            </div>
            <div>
              <span className="font-semibold text-slate-800 block">Enumeration Date</span>
              <span className="text-slate-900 font-medium">{record.enumerationDate}</span>
              <span className="text-slate-500 block text-[11px]">Record Timestamp: {new Date(record.createdAt).toLocaleDateString()}</span>
            </div>
            <div className="sm:text-right flex flex-col justify-end">
              <div className="h-8 border-b border-dashed border-slate-400 mb-1"></div>
              <span className="font-semibold text-slate-700 text-[11px] uppercase tracking-wider">
                Official Signature & Stamp
              </span>
            </div>
          </div>

          {/* Barcode & Security Marker */}
          <div className="mt-8 pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 font-mono">
            <div>SECURITY HASH: {record.id.replace(/-/g, '')}X98A-{record.householdId}</div>
            <div className="tracking-[0.3em] font-bold text-slate-600 text-xs">
              ||| | |||| | || |||| ||| |||| |
            </div>
            <div>VERIFIED BY POPULATION CENSUS AUTHORITY</div>
          </div>
        </div>
      </div>
    </div>
  );
};
