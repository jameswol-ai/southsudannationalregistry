'use client';

import React from 'react';
import { CensusRecord } from '@/lib/types';
import { checkVoterEligibility, getAssignedPollingStation, generateVoterId } from '@/lib/electionData';
import { 
  X, 
  Printer, 
  ShieldCheck, 
  Vote, 
  MapPin, 
  QrCode, 
  Fingerprint, 
  UserCheck, 
  CheckCircle2, 
  Building2,
  AlertTriangle
} from 'lucide-react';

interface Props {
  record: CensusRecord | null;
  isOpen: boolean;
  onClose: () => void;
  onMarkAsVoted?: (recordId: string) => void;
}

export const VoterCardModal: React.FC<Props> = ({
  record,
  isOpen,
  onClose,
  onMarkAsVoted
}) => {
  if (!isOpen || !record) return null;

  const eligibility = checkVoterEligibility(record);
  const pollingStation = getAssignedPollingStation(record);
  const voterId = record.voterIdNumber || generateVoterId(record);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs overflow-y-auto">
      <div 
        id="voter-card-modal"
        className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden my-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white print:hidden">
          <div className="flex items-center gap-2.5">
            <Vote className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="font-bold text-sm tracking-wide uppercase">
                National Electoral Commission
              </h3>
              <p className="text-[11px] text-slate-400">
                Official Digital Voter Identity Credential & Card
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-sm transition-all"
            >
              <Printer className="w-3.5 h-3.5" />
              Print Card
            </button>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 sm:p-8 space-y-6">
          {!eligibility.isEligible ? (
            <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900">
              <div className="flex items-center gap-2.5 font-bold text-sm mb-2 text-amber-800">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                Voter Registration Ineligible
              </div>
              <p className="text-xs text-amber-700 leading-relaxed mb-3">
                This individual does not currently meet the statutory qualifications for the electoral roll:
              </p>
              <ul className="list-disc list-inside text-xs space-y-1 text-amber-800 font-medium">
                {eligibility.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          ) : (
            <>
              {/* THE OFFICIAL VOTER CARD (Front & Back Layout) */}
              <div 
                id="printable-voter-card"
                className="relative rounded-2xl bg-gradient-to-br from-emerald-950 via-slate-900 to-slate-950 text-white p-6 sm:p-7 shadow-xl border-2 border-emerald-500/40 overflow-hidden"
              >
                {/* Background Guilloche / Security Pattern Watermark */}
                <div className="absolute inset-0 opacity-5 pointer-events-none flex items-center justify-center">
                  <div className="w-96 h-96 rounded-full border-8 border-dashed border-white"></div>
                </div>

                {/* Card Header */}
                <div className="relative z-10 flex items-start justify-between pb-4 border-b border-slate-700/80 gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400 font-black text-xl shadow-inner">
                      NEC
                    </div>
                    <div>
                      <div className="text-[10px] font-bold tracking-widest text-emerald-400 uppercase">
                        Republic of South Sudan • Electoral Commission
                      </div>
                      <h2 className="text-base sm:text-lg font-extrabold text-white tracking-tight uppercase">
                        Voter Registration Card
                      </h2>
                      <div className="text-[11px] text-slate-300 font-medium">
                        General Elections & Referendum Act
                      </div>
                    </div>
                  </div>

                  {/* Security Chip & Status */}
                  <div className="text-right">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      AUTHENTICATED
                    </span>
                    <div className="text-[10px] text-slate-400 font-mono mt-1">
                      EXP: 2030-DEC
                    </div>
                  </div>
                </div>

                {/* Card Middle Section: Avatar + Details + QR */}
                <div className="relative z-10 grid grid-cols-1 sm:grid-cols-12 gap-6 pt-5">
                  {/* Photo & Biometric Box (3 cols) */}
                  <div className="sm:col-span-4 flex flex-col items-center justify-center">
                    <div className="w-28 h-32 rounded-xl bg-slate-800 border-2 border-emerald-400/40 shadow-inner flex flex-col items-center justify-center p-2 relative overflow-hidden">
                      <div className="w-16 h-16 rounded-full bg-emerald-900/60 border border-emerald-400/30 flex items-center justify-center text-xl font-bold text-emerald-200">
                        {record.fullName.charAt(0)}
                      </div>
                      <span className="text-[10px] text-slate-300 font-semibold mt-2 text-center truncate max-w-full px-1">
                        {record.fullName}
                      </span>
                      {/* Biometric Seal Badge */}
                      <div className="absolute bottom-1 right-1 bg-emerald-500 text-slate-950 p-1 rounded-full shadow">
                        <Fingerprint className="w-3.5 h-3.5" />
                      </div>
                    </div>
                    <div className="mt-2 text-center">
                      <span className="text-[9px] font-mono tracking-wider text-slate-400 uppercase block">
                        Biometrics Enrolled
                      </span>
                    </div>
                  </div>

                  {/* Particulars (8 cols) */}
                  <div className="sm:col-span-8 space-y-3 text-xs">
                    {/* VRN & Full Name */}
                    <div>
                      <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                        Voter Registration Number (VRN)
                      </div>
                      <div className="font-mono text-base sm:text-lg font-black tracking-widest text-white">
                        {voterId}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <div className="text-[10px] text-slate-400 font-semibold uppercase">
                          Full Legal Name
                        </div>
                        <div className="font-bold text-white text-sm truncate">
                          {record.fullName}
                        </div>
                      </div>

                      <div>
                        <div className="text-[10px] text-slate-400 font-semibold uppercase">
                          Age / Gender
                        </div>
                        <div className="font-bold text-white">
                          {record.age} Years • {record.gender}
                        </div>
                      </div>
                    </div>

                    {/* Constituency & Polling Station */}
                    <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 space-y-1">
                      <div className="flex items-center gap-1.5 text-[10px] font-bold text-amber-400 uppercase">
                        <MapPin className="w-3.5 h-3.5" />
                        Assigned Polling Station
                      </div>
                      <div className="font-bold text-slate-100 text-xs truncate">
                        {record.pollingStationName || pollingStation.name}
                      </div>
                      <div className="text-[10px] text-slate-400 flex items-center justify-between">
                        <span>Code: <strong className="text-white font-mono">{pollingStation.code}</strong></span>
                        <span>{record.constituency || pollingStation.constituency}</span>
                      </div>
                    </div>

                    {/* Community & Census Ref */}
                    <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                      <div>
                        <span className="text-[9px] text-slate-400 uppercase block">Community / State</span>
                        <span className="font-medium truncate block">{record.community}, {record.stateOrRegion}</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-400 uppercase block">Census Ref ID</span>
                        <span className="font-mono font-medium text-emerald-300">{record.id}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Footer Barcode & Security Strip */}
                <div className="relative z-10 mt-5 pt-3 border-t border-slate-700/80 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <QrCode className="w-8 h-8 text-emerald-400 shrink-0" />
                    <div className="text-[9px] text-slate-400 font-mono">
                      SECURE QR VERIFICATION HASH: {voterId}-SEC-2026
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-right">
                    {record.hasVoted ? (
                      <span className="px-2.5 py-1 rounded-lg bg-purple-500/30 text-purple-300 border border-purple-400/40 text-[11px] font-bold">
                        ✓ BALLOT CAST
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-[10px] font-bold">
                        ELIGIBLE TO VOTE
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 print:hidden">
                <div className="text-xs text-slate-500 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Valid for all National, Parliamentary, and Local Council Elections.</span>
                </div>

                <div className="flex items-center gap-2">
                  {onMarkAsVoted && !record.hasVoted && (
                    <button
                      type="button"
                      onClick={() => {
                        onMarkAsVoted(record.id);
                      }}
                      className="px-4 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs shadow-sm transition-colors flex items-center gap-1.5"
                    >
                      <Vote className="w-3.5 h-3.5" />
                      Mark Indelible Ink / Cast Ballot
                    </button>
                  )}
                  
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
