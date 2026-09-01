'use client';

import React, { useState, useMemo } from 'react';
import { CensusRecord, HouseholdSummary } from '@/lib/types';
import { 
  Building2, 
  Users, 
  UserPlus, 
  MapPin, 
  Sparkles, 
  Search, 
  ChevronRight, 
  FileText, 
  CheckCircle2, 
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

interface Props {
  records: CensusRecord[];
  onAddMemberToHousehold: (householdId: string, community: string, stateOrRegion: string) => void;
  onViewRecord: (record: CensusRecord) => void;
}

export const HouseholdUnitView: React.FC<Props> = ({
  records,
  onAddMemberToHousehold,
  onViewRecord
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedHouseholdId, setSelectedHouseholdId] = useState<string | null>(null);

  // Group records into households
  const households: HouseholdSummary[] = useMemo(() => {
    const map = new Map<string, CensusRecord[]>();
    
    records.forEach(r => {
      const hhId = r.householdId || 'HH-UNASSIGNED';
      if (!map.has(hhId)) {
        map.set(hhId, []);
      }
      map.get(hhId)!.push(r);
    });

    const list: HouseholdSummary[] = [];

    map.forEach((members, householdId) => {
      const head = members.find(m => m.isHouseholdHead) || members[0];
      list.push({
        householdId,
        headName: head ? head.fullName : 'No Head Listed',
        community: head ? head.community : 'Various',
        stateOrRegion: head ? head.stateOrRegion : 'Various',
        membersCount: members.length,
        members,
        primaryTribe: head ? head.tribe : (members[0]?.tribe || 'Unspecified')
      });
    });

    return list.sort((a, b) => b.membersCount - a.membersCount);
  }, [records]);

  // Filter households by search
  const filteredHouseholds = useMemo(() => {
    if (!searchTerm.trim()) return households;
    const q = searchTerm.toLowerCase();
    return households.filter(h => 
      h.householdId.toLowerCase().includes(q) ||
      h.headName.toLowerCase().includes(q) ||
      h.community.toLowerCase().includes(q) ||
      h.primaryTribe.toLowerCase().includes(q) ||
      h.members.some(m => m.fullName.toLowerCase().includes(q))
    );
  }, [households, searchTerm]);

  // Selected household
  const activeHousehold = useMemo(() => {
    if (selectedHouseholdId) {
      return households.find(h => h.householdId === selectedHouseholdId) || households[0];
    }
    return households[0] || null;
  }, [households, selectedHouseholdId]);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center font-bold">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Households</div>
            <div className="text-2xl font-bold text-slate-900">{households.length} Units</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Average Family Size</div>
            <div className="text-2xl font-bold text-slate-900">
              {(records.length / (households.length || 1)).toFixed(1)} Persons
            </div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center font-bold">
            <MapPin className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Communities Covered</div>
            <div className="text-2xl font-bold text-slate-900">
              {new Set(households.map(h => h.community)).size} Localities
            </div>
          </div>
        </div>
      </div>

      {/* Main Household Browser Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Household List (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/90 shadow-sm p-4 sm:p-5 flex flex-col h-[650px]">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2">
              <Building2 className="w-4 h-4 text-purple-600" />
              Household Directory ({filteredHouseholds.length})
            </h3>
          </div>

          {/* Search Box */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              id="household-search-input"
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by HH number, head name, or village..."
              className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-600 placeholder:text-slate-400"
            />
          </div>

          {/* Household Cards List */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {filteredHouseholds.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-xs">
                No household units matched search.
              </div>
            ) : (
              filteredHouseholds.map((hh) => {
                const isActive = activeHousehold?.householdId === hh.householdId;
                return (
                  <div
                    key={hh.householdId}
                    id={`hh-card-${hh.householdId}`}
                    onClick={() => setSelectedHouseholdId(hh.householdId)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      isActive 
                        ? 'bg-purple-50/80 border-purple-300 ring-1 ring-purple-300 shadow-xs' 
                        : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-900 border border-purple-200">
                          {hh.householdId}
                        </span>
                        <span className="font-bold text-slate-900 text-xs sm:text-sm truncate max-w-[170px]">
                          {hh.headName}
                        </span>
                      </div>
                      <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                        <Users className="w-3 h-3" />
                        {hh.membersCount} {hh.membersCount === 1 ? 'member' : 'members'}
                      </span>
                    </div>

                    <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                      <div className="flex items-center gap-1 truncate max-w-[200px]">
                        <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                        <span className="truncate">{hh.community}</span>
                      </div>
                      <div className="font-medium text-emerald-800 shrink-0">
                        {hh.primaryTribe}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Side: Detailed Household Roster (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 flex flex-col h-[650px] overflow-y-auto">
          {activeHousehold ? (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold bg-purple-900 text-white px-2.5 py-0.5 rounded-lg">
                      {activeHousehold.householdId}
                    </span>
                    <h3 className="font-bold text-slate-900 text-lg">
                      {activeHousehold.headName}&apos;s Family Unit
                    </h3>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-blue-600" />
                      {activeHousehold.community}, {activeHousehold.stateOrRegion}
                    </span>
                    <span>•</span>
                    <span className="text-emerald-700 font-semibold">
                      {activeHousehold.primaryTribe}
                    </span>
                  </div>
                </div>

                <button
                  id="add-member-to-current-hh-btn"
                  type="button"
                  onClick={() => onAddMemberToHousehold(
                    activeHousehold.householdId,
                    activeHousehold.community,
                    activeHousehold.stateOrRegion
                  )}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-white bg-purple-800 hover:bg-purple-700 rounded-xl transition-colors shadow-xs self-start sm:self-auto"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  + Add Member to this HH
                </button>
              </div>

              {/* Members List */}
              <div className="space-y-3">
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Enumerated Household Members ({activeHousehold.members.length})
                </div>

                {activeHousehold.members.map((member) => (
                  <div
                    key={member.id}
                    className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">
                          {member.fullName}
                        </span>
                        {member.isHouseholdHead && (
                          <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded-full bg-amber-100 text-amber-900 border border-amber-300">
                            Household Head
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-0.5 text-xs text-slate-600">
                        <div>
                          <span className="text-slate-400">Role:</span> {member.householdRole}
                        </div>
                        <div>
                          <span className="text-slate-400">Age/Gender:</span> {member.age} yrs, {member.gender}
                        </div>
                        <div>
                          <span className="text-slate-400">Marital:</span> {member.maritalStatus}
                        </div>
                        <div>
                          <span className="text-slate-400">Education:</span> {member.educationLevel}
                        </div>
                        <div>
                          <span className="text-slate-400">Trade:</span> {member.primaryOccupation || member.employmentStatus}
                        </div>
                        <div>
                          <span className="text-slate-400">ID:</span> <span className="font-mono">{member.id}</span>
                        </div>
                      </div>
                    </div>

                    <button
                      id={`view-member-slip-${member.id}`}
                      type="button"
                      onClick={() => onViewRecord(member)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 rounded-lg transition-colors shadow-2xs self-end sm:self-center"
                    >
                      <FileText className="w-3.5 h-3.5 text-slate-600" />
                      View Slip
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
              Select a household unit to inspect members and demographics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
