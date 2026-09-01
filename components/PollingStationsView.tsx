'use client';

import React, { useState, useMemo } from 'react';
import { CensusRecord, PollingStation } from '@/lib/types';
import { 
  OFFICIAL_POLLING_STATIONS, 
  getAssignedPollingStation, 
  checkVoterEligibility,
  generateVoterId 
} from '@/lib/electionData';
import { 
  Building2, 
  MapPin, 
  Users, 
  Vote, 
  Printer, 
  Accessibility, 
  ShieldCheck, 
  CheckCircle2, 
  Search, 
  ArrowRight,
  Layers
} from 'lucide-react';

interface Props {
  records: CensusRecord[];
  onViewVoterCard: (record: CensusRecord) => void;
  onMarkAsVoted: (recordId: string) => void;
}

export const PollingStationsView: React.FC<Props> = ({
  records,
  onViewVoterCard,
  onMarkAsVoted
}) => {
  const [selectedStationId, setSelectedStationId] = useState<string>(OFFICIAL_POLLING_STATIONS[0].id);
  const [rosterSearch, setRosterSearch] = useState('');

  // Compute registered voters and votes per station
  const stationStats = useMemo(() => {
    const map = new Map<string, { totalAssigned: number; totalVoted: number; specialNeedsCount: number; records: CensusRecord[] }>();

    OFFICIAL_POLLING_STATIONS.forEach(ps => {
      map.set(ps.id, { totalAssigned: 0, totalVoted: 0, specialNeedsCount: 0, records: [] });
    });

    records.forEach(r => {
      const eligibility = checkVoterEligibility(r);
      if (eligibility.isEligible) {
        const ps = getAssignedPollingStation(r);
        const existing = map.get(ps.id) || { totalAssigned: 0, totalVoted: 0, specialNeedsCount: 0, records: [] };
        existing.totalAssigned += 1;
        if (r.hasVoted) existing.totalVoted += 1;
        if (r.hasSpecialNeedsOrDisability) existing.specialNeedsCount += 1;
        existing.records.push(r);
        map.set(ps.id, existing);
      }
    });

    return map;
  }, [records]);

  const activeStation = useMemo(() => {
    return OFFICIAL_POLLING_STATIONS.find(ps => ps.id === selectedStationId) || OFFICIAL_POLLING_STATIONS[0];
  }, [selectedStationId]);

  const activeRoster = useMemo(() => {
    const data = stationStats.get(activeStation.id);
    if (!data) return [];
    
    const query = rosterSearch.trim().toLowerCase();
    if (!query) return data.records;

    return data.records.filter(r => 
      r.fullName.toLowerCase().includes(query) ||
      (r.voterIdNumber && r.voterIdNumber.toLowerCase().includes(query)) ||
      r.id.toLowerCase().includes(query) ||
      (r.tribe && r.tribe.toLowerCase().includes(query))
    );
  }, [stationStats, activeStation, rosterSearch]);

  const activeData = stationStats.get(activeStation.id) || { totalAssigned: 0, totalVoted: 0, specialNeedsCount: 0, records: [] };
  const stationTurnout = activeData.totalAssigned > 0 ? Math.round((activeData.totalVoted / activeData.totalAssigned) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-7 border border-slate-800 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/20 text-purple-400 border border-purple-500/40 flex items-center justify-center shadow-inner">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[10px] font-bold tracking-widest text-purple-400 uppercase">
                Electoral Logistics & Polling Infrastructure
              </div>
              <h2 className="text-lg sm:text-2xl font-black text-white tracking-tight">
                Constituency & Polling Stations Directory
              </h2>
            </div>
          </div>

          <div className="text-xs text-slate-400">
            <span><strong>{OFFICIAL_POLLING_STATIONS.length}</strong> Official Voting Centers Provisioned</span>
          </div>
        </div>
      </div>

      {/* Grid: Station Selector Cards (Left 5 cols) + Active Station Roster (Right 7 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Stations List */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-600" />
            Select Polling Station
          </h3>

          <div className="space-y-2.5 max-h-[700px] overflow-y-auto pr-1">
            {OFFICIAL_POLLING_STATIONS.map((ps) => {
              const data = stationStats.get(ps.id) || { totalAssigned: 0, totalVoted: 0, specialNeedsCount: 0 };
              const isSelected = ps.id === selectedStationId;
              const turnout = data.totalAssigned > 0 ? Math.round((data.totalVoted / data.totalAssigned) * 100) : 0;

              return (
                <div
                  key={ps.id}
                  onClick={() => setSelectedStationId(ps.id)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-purple-400/40'
                      : 'bg-white text-slate-800 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded ${
                          isSelected ? 'bg-purple-500/30 text-purple-300 border border-purple-400/30' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {ps.code}
                        </span>
                        {ps.isAccessible && (
                          <span className={`inline-flex items-center gap-1 text-[10px] font-medium ${isSelected ? 'text-emerald-300' : 'text-emerald-600'}`}>
                            <Accessibility className="w-3 h-3" />
                            Accessible
                          </span>
                        )}
                      </div>
                      <h4 className="font-bold text-xs sm:text-sm mt-1.5 leading-snug">
                        {ps.name}
                      </h4>
                      <p className={`text-[11px] mt-0.5 ${isSelected ? 'text-slate-400' : 'text-slate-500'}`}>
                        {ps.constituency} • {ps.stateOrRegion}
                      </p>
                    </div>

                    <div className="text-right shrink-0">
                      <div className={`text-base font-extrabold ${isSelected ? 'text-emerald-400' : 'text-emerald-600'}`}>
                        {data.totalAssigned}
                      </div>
                      <div className={`text-[9px] uppercase tracking-wider ${isSelected ? 'text-slate-400' : 'text-slate-500'}`}>
                        Voters
                      </div>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="mt-3 pt-2.5 border-t border-slate-200/40 dark:border-slate-800 flex items-center justify-between text-[11px]">
                    <span className={isSelected ? 'text-slate-300' : 'text-slate-600'}>
                      Ballots Cast: <strong className={isSelected ? 'text-white' : 'text-slate-900'}>{data.totalVoted}</strong> ({turnout}%)
                    </span>
                    <span className={`font-mono text-[10px] ${isSelected ? 'text-slate-400' : 'text-slate-500'}`}>
                      Cap: {ps.capacity}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Active Station Details & Presiding Officer Roster */}
        <div className="lg:col-span-7 space-y-4">
          {/* Station Card Header */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-black bg-slate-900 text-white px-2.5 py-0.5 rounded-md">
                    {activeStation.code}
                  </span>
                  <span className="text-xs font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200">
                    {activeStation.constituency}
                  </span>
                </div>
                <h3 className="text-base sm:text-lg font-black text-slate-900 mt-1">
                  {activeStation.name}
                </h3>
                <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-2">
                  <span>{activeStation.wardOrBoma}, {activeStation.countyOrPayam}, {activeStation.stateOrRegion}</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => window.print()}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors shrink-0 print:hidden"
              >
                <Printer className="w-3.5 h-3.5" />
                Print Station Register
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="mt-4 grid grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
                <div className="text-[10px] font-bold text-slate-500 uppercase">Assigned Voters</div>
                <div className="text-lg font-black text-slate-900 mt-0.5">{activeData.totalAssigned}</div>
              </div>
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200/70">
                <div className="text-[10px] font-bold text-emerald-700 uppercase">Ballots Cast</div>
                <div className="text-lg font-black text-emerald-800 mt-0.5">{activeData.totalVoted}</div>
              </div>
              <div className="p-3 rounded-xl bg-purple-50 border border-purple-200/70">
                <div className="text-[10px] font-bold text-purple-700 uppercase">Turnout Rate</div>
                <div className="text-lg font-black text-purple-800 mt-0.5">{stationTurnout}%</div>
              </div>
            </div>
          </div>

          {/* Polling Station Voter Register Table */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4 text-emerald-600" />
                Presiding Officer Voter Register ({activeRoster.length})
              </h4>

              {/* Roster Search */}
              <div className="relative w-full sm:w-64">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={rosterSearch}
                  onChange={(e) => setRosterSearch(e.target.value)}
                  placeholder="Search station register..."
                  className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:bg-white focus:outline-hidden"
                />
              </div>
            </div>

            <div className="border border-slate-200 rounded-xl overflow-hidden max-h-[420px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[9px] tracking-wider sticky top-0">
                  <tr>
                    <th className="px-3 py-2.5">VRN / Ref</th>
                    <th className="px-3 py-2.5">Voter Name</th>
                    <th className="px-3 py-2.5">Age / Sex</th>
                    <th className="px-3 py-2.5">Indelible Ink / Ballot</th>
                    <th className="px-3 py-2.5 text-right">Card</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {activeRoster.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-slate-400 text-xs">
                        No eligible voters assigned to this station matching your filter.
                      </td>
                    </tr>
                  ) : (
                    activeRoster.map((voter) => {
                      const vrn = voter.voterIdNumber || generateVoterId(voter);
                      return (
                        <tr key={voter.id} className="hover:bg-slate-50">
                          <td className="px-3 py-2.5">
                            <span className="font-mono font-bold text-slate-900 block">{vrn}</span>
                            <span className="font-mono text-[9px] text-slate-400">{voter.id}</span>
                          </td>
                          <td className="px-3 py-2.5">
                            <div className="font-bold text-slate-900">{voter.fullName}</div>
                            <div className="text-[10px] text-slate-500">{voter.tribe}</div>
                          </td>
                          <td className="px-3 py-2.5 text-[11px]">
                            {voter.age} yrs • {voter.gender}
                          </td>
                          <td className="px-3 py-2.5">
                            {voter.hasVoted ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold bg-purple-100 text-purple-800">
                                <CheckCircle2 className="w-3 h-3 text-purple-600" />
                                Marked & Voted
                              </span>
                            ) : (
                              <button
                                type="button"
                                onClick={() => onMarkAsVoted(voter.id)}
                                className="px-2 py-0.5 rounded bg-slate-900 text-white hover:bg-purple-800 text-[10px] font-bold transition-colors"
                              >
                                Mark Ink
                              </button>
                            )}
                          </td>
                          <td className="px-3 py-2.5 text-right">
                            <button
                              type="button"
                              onClick={() => onViewVoterCard(voter)}
                              className="px-2 py-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded border border-emerald-200 transition-colors"
                            >
                              Voter Card
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
