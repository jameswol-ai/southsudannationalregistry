'use client';

import React from 'react';
import { 
  Building2, 
  Users, 
  UserPlus, 
  BarChart3, 
  Zap, 
  Database, 
  ShieldCheck, 
  Layers,
  Sparkles,
  MapPin,
  Vote
} from 'lucide-react';

export type ActiveTab = 
  | 'registry' 
  | 'admin-hierarchy'
  | 'voters' 
  | 'polling-stations' 
  | 'election-day' 
  | 'households' 
  | 'form' 
  | 'analytics' 
  | 'quick-field';

interface Props {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  totalRecords: number;
  totalHouseholds: number;
  totalTribes: number;
  totalEligibleVoters: number;
  totalVotesCast: number;
  totalCounties?: number;
  onOpenExportModal: () => void;
}

export const Navbar: React.FC<Props> = ({
  activeTab,
  onTabChange,
  totalRecords,
  totalHouseholds,
  totalTribes,
  totalEligibleVoters,
  totalVotesCast,
  totalCounties,
  onOpenExportModal
}) => {
  const tabs = [
    { id: 'registry' as ActiveTab, label: 'Citizen Registry', icon: Users, badge: totalRecords },
    { id: 'admin-hierarchy' as ActiveTab, label: 'Counties, Payams & Bomas', icon: MapPin, badge: totalCounties || 10 },
    { id: 'voters' as ActiveTab, label: 'Electoral Roll', icon: Vote, badge: totalEligibleVoters },
    { id: 'polling-stations' as ActiveTab, label: 'Polling Stations', icon: Building2, badge: 10 },
    { id: 'election-day' as ActiveTab, label: 'Live Ballot Simulation', icon: Zap, badge: totalVotesCast > 0 ? `${totalVotesCast} Voted` : undefined },
    { id: 'households' as ActiveTab, label: 'Household Units', icon: Layers, badge: totalHouseholds },
    { id: 'form' as ActiveTab, label: 'New Enumeration', icon: UserPlus },
    { id: 'analytics' as ActiveTab, label: 'Demographics & Reports', icon: BarChart3 },
    { id: 'quick-field' as ActiveTab, label: 'Field Rapid Mode', icon: Sparkles },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs">
      {/* Top Banner with Brand and Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-lg tracking-tighter shadow-md">
            <span className="text-emerald-400 font-serif">SS</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-slate-900 text-base sm:text-lg tracking-tight">
                South Sudan National Registry
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                <ShieldCheck className="w-3 h-3" />
                Civil & Electoral Commission
              </span>
            </div>
            <p className="text-xs text-slate-500">
              National population census, administrative hierarchy, households & electoral rolls
            </p>
          </div>
        </div>

        {/* Live Counters & Data Management Button */}
        <div className="flex items-center gap-3 sm:gap-4 flex-wrap">
          {/* Stats Bar */}
          <div className="hidden lg:flex items-center gap-3 px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <div className="flex items-center gap-1.5 font-medium text-slate-700">
              <Users className="w-3.5 h-3.5 text-emerald-600" />
              <span><strong className="text-slate-900">{totalRecords}</strong> Persons</span>
            </div>
            <div className="h-3 w-px bg-slate-300"></div>
            <div className="flex items-center gap-1.5 font-medium text-slate-700">
              <Building2 className="w-3.5 h-3.5 text-purple-600" />
              <span><strong className="text-slate-900">{totalHouseholds}</strong> Households</span>
            </div>
            <div className="h-3 w-px bg-slate-300"></div>
            <div className="flex items-center gap-1.5 font-medium text-slate-700">
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              <span><strong className="text-slate-900">{totalTribes}</strong> Tribes</span>
            </div>
          </div>

          {/* Export / Backup button */}
          <button
            id="open-export-modal-btn"
            type="button"
            onClick={onOpenExportModal}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl transition-colors shadow-2xs"
          >
            <Database className="w-3.5 h-3.5 text-slate-600" />
            Backup & Export
          </button>
        </div>
      </div>

      {/* Tabs Row */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center space-x-1 sm:space-x-2 overflow-x-auto no-scrollbar border-t border-slate-100">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              id={`nav-tab-${tab.id}`}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2 px-3.5 sm:px-4 py-3 text-xs sm:text-sm font-semibold border-b-2 transition-all whitespace-nowrap ${
                isActive
                  ? 'border-slate-900 text-slate-900 bg-slate-50/70'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-600' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
              {typeof tab.badge === 'number' && (
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-700'
                }`}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </header>
  );
};
