'use client';

import React, { useState, useMemo } from 'react';
import { CensusRecord } from '@/lib/types';
import { 
  checkVoterEligibility, 
  getAssignedPollingStation, 
  generateVoterId, 
  calculateElectionStats,
  exportElectoralRollCSV,
  OFFICIAL_POLLING_STATIONS
} from '@/lib/electionData';
import { 
  Vote, 
  Users, 
  UserCheck, 
  ShieldCheck, 
  AlertCircle, 
  Search, 
  Filter, 
  Download, 
  Printer, 
  IdCard, 
  MapPin, 
  CheckCircle2, 
  Sparkles,
  Zap,
  Building2,
  Accessibility
} from 'lucide-react';

interface Props {
  records: CensusRecord[];
  onViewVoterCard: (record: CensusRecord) => void;
  onMarkAsVoted: (recordId: string) => void;
  onBatchRegisterVoters?: () => void;
}

export const ElectoralRollView: React.FC<Props> = ({
  records,
  onViewVoterCard,
  onMarkAsVoted,
  onBatchRegisterVoters
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [eligibilityFilter, setEligibilityFilter] = useState<'all' | 'eligible' | 'ineligible' | 'voted' | 'not-voted'>('eligible');
  const [pollingStationFilter, setPollingStationFilter] = useState<string>('all');
  const [genderFilter, setGenderFilter] = useState<string>('all');

  const stats = useMemo(() => calculateElectionStats(records), [records]);

  // Filtered dataset
  const filteredVoters = useMemo(() => {
    return records.filter(r => {
      const eligibility = checkVoterEligibility(r);
      const ps = getAssignedPollingStation(r);
      const vrn = r.voterIdNumber || generateVoterId(r);

      // Search match
      const query = searchQuery.trim().toLowerCase();
      const matchesSearch = !query || 
        r.fullName.toLowerCase().includes(query) ||
        r.id.toLowerCase().includes(query) ||
        vrn.toLowerCase().includes(query) ||
        (r.nationalId && r.nationalId.toLowerCase().includes(query)) ||
        (r.tribe && r.tribe.toLowerCase().includes(query)) ||
        (r.community && r.community.toLowerCase().includes(query));

      if (!matchesSearch) return false;

      // Eligibility Filter
      if (eligibilityFilter === 'eligible' && !eligibility.isEligible) return false;
      if (eligibilityFilter === 'ineligible' && eligibility.isEligible) return false;
      if (eligibilityFilter === 'voted' && (!eligibility.isEligible || !r.hasVoted)) return false;
      if (eligibilityFilter === 'not-voted' && (!eligibility.isEligible || r.hasVoted)) return false;

      // Polling Station Filter
      if (pollingStationFilter !== 'all' && ps.id !== pollingStationFilter) return false;

      // Gender Filter
      if (genderFilter !== 'all' && r.gender !== genderFilter) return false;

      return true;
    });
  }, [records, searchQuery, eligibilityFilter, pollingStationFilter, genderFilter]);

  return (
    <div className="space-y-6">
      {/* Top Banner & Electoral KPIs */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-7 border border-slate-800 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center shadow-inner">
              <Vote className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-widest text-emerald-400 uppercase bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/30">
                  Statutory Electoral Registry
                </span>
                <span className="text-xs text-slate-400">• Constitution of South Sudan</span>
              </div>
              <h2 className="text-lg sm:text-2xl font-black text-white tracking-tight mt-0.5">
                Official Electoral Roll & Voter Register
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            <button
              type="button"
              onClick={() => exportElectoralRollCSV(records)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow transition-all"
            >
              <Download className="w-4 h-4" />
              Export Electoral Roll (.CSV)
            </button>
          </div>
        </div>

        {/* Electoral Stats Metric Grid */}
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Eligible Voters (18+)
            </div>
            <div className="text-xl font-black text-emerald-400 mt-1">
              {stats.totalEligible}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              of {records.length} total citizens
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Youth Voters (18–24)
            </div>
            <div className="text-xl font-black text-amber-400 mt-1">
              {stats.firstTimeVotersCount}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              First-time eligible wave
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Female Voters
            </div>
            <div className="text-xl font-black text-purple-400 mt-1">
              {stats.femaleVotersCount}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              {stats.totalEligible > 0 ? Math.round((stats.femaleVotersCount / stats.totalEligible) * 100) : 0}% of electorate
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Priority / Special Needs
            </div>
            <div className="text-xl font-black text-blue-400 mt-1">
              {stats.specialNeedsVotersCount}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Accessible booth priority
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Ballots Cast
            </div>
            <div className="text-xl font-black text-emerald-300 mt-1">
              {stats.totalVotesCast}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Verified voters in session
            </div>
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Turnout Rate
            </div>
            <div className="text-xl font-black text-amber-300 mt-1">
              {stats.turnoutPercentage}%
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Live participation
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Toolbar */}
      <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          {/* Search Box */}
          <div className="md:col-span-4 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Voter Name, VRN, Census ID, Tribe..."
              className="w-full pl-9 pr-3.5 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:ring-2 focus:ring-slate-900 focus:outline-hidden transition-all"
            />
          </div>

          {/* Eligibility Filter */}
          <div className="md:col-span-3">
            <select
              value={eligibilityFilter}
              onChange={(e) => setEligibilityFilter(e.target.value as any)}
              className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:ring-2 focus:ring-slate-900"
            >
              <option value="eligible">Eligible Electorate (18+)</option>
              <option value="all">All Census Records</option>
              <option value="ineligible">Underage & Ineligible (Youth &lt;18)</option>
              <option value="voted">Voted (Ballot Cast)</option>
              <option value="not-voted">Not Yet Voted</option>
            </select>
          </div>

          {/* Polling Station Filter */}
          <div className="md:col-span-3">
            <select
              value={pollingStationFilter}
              onChange={(e) => setPollingStationFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:ring-2 focus:ring-slate-900"
            >
              <option value="all">All Polling Stations ({OFFICIAL_POLLING_STATIONS.length})</option>
              {OFFICIAL_POLLING_STATIONS.map(ps => (
                <option key={ps.id} value={ps.id}>
                  {ps.code} - {ps.name}
                </option>
              ))}
            </select>
          </div>

          {/* Gender Filter */}
          <div className="md:col-span-2">
            <select
              value={genderFilter}
              onChange={(e) => setGenderFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:ring-2 focus:ring-slate-900"
            >
              <option value="all">All Genders</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
        </div>

        {/* Quick status bar */}
        <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 flex-wrap gap-2">
          <div>
            Showing <strong className="text-slate-900">{filteredVoters.length}</strong> voter records
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1 text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Eligible (Age 18+)
            </span>
            <span className="inline-flex items-center gap-1 text-purple-700">
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
              Ballot Cast
            </span>
            <span className="inline-flex items-center gap-1 text-amber-700">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              Underage &lt;18
            </span>
          </div>
        </div>
      </div>

      {/* Voter Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-4 py-3.5">Voter Registration No (VRN)</th>
                <th className="px-4 py-3.5">Full Legal Name</th>
                <th className="px-4 py-3.5">Age & Demographic</th>
                <th className="px-4 py-3.5">Tribe & Community</th>
                <th className="px-4 py-3.5">Assigned Polling Station</th>
                <th className="px-4 py-3.5">Electoral Status</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-normal text-slate-700">
              {filteredVoters.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400 text-xs">
                    No voter records found matching your filters. Try clearing your search or switching filters.
                  </td>
                </tr>
              ) : (
                filteredVoters.map((record) => {
                  const eligibility = checkVoterEligibility(record);
                  const ps = getAssignedPollingStation(record);
                  const vrn = record.voterIdNumber || generateVoterId(record);

                  return (
                    <tr 
                      key={record.id}
                      className={`hover:bg-slate-50/80 transition-colors ${record.hasVoted ? 'bg-purple-50/20' : ''}`}
                    >
                      {/* VRN & Census ID */}
                      <td className="px-4 py-3.5">
                        {eligibility.isEligible ? (
                          <div>
                            <span className="font-mono font-bold text-slate-900 text-xs block">
                              {vrn}
                            </span>
                            <span className="font-mono text-[10px] text-slate-400 block">
                              Ref: {record.id}
                            </span>
                          </div>
                        ) : (
                          <div>
                            <span className="font-mono text-amber-700 text-xs font-semibold block">
                              INELIGIBLE
                            </span>
                            <span className="font-mono text-[10px] text-slate-400 block">
                              Ref: {record.id}
                            </span>
                          </div>
                        )}
                      </td>

                      {/* Name & Priority Tag */}
                      <td className="px-4 py-3.5">
                        <div className="font-bold text-slate-900">
                          {record.fullName}
                        </div>
                        {record.hasSpecialNeedsOrDisability && (
                          <span className="inline-flex items-center gap-1 mt-0.5 text-[10px] font-semibold text-blue-700 bg-blue-50 px-1.5 py-0.2 rounded border border-blue-200">
                            <Accessibility className="w-3 h-3" />
                            Priority Assistance
                          </span>
                        )}
                      </td>

                      {/* Age & Demographic */}
                      <td className="px-4 py-3.5">
                        <div className="text-xs font-medium text-slate-800">
                          {record.age} Years • {record.gender}
                        </div>
                        <div className="text-[10px] text-slate-500">
                          {record.age >= 18 && record.age <= 24 ? (
                            <span className="text-emerald-600 font-semibold">Youth Voter (18-24)</span>
                          ) : record.age >= 60 ? (
                            <span className="text-slate-600 font-semibold">Senior Citizen</span>
                          ) : (
                            <span>Adult Electorate</span>
                          )}
                        </div>
                      </td>

                      {/* Tribe & Community */}
                      <td className="px-4 py-3.5">
                        <div className="text-xs font-semibold text-slate-800">
                          {record.tribe}
                        </div>
                        <div className="text-[10px] text-slate-500 truncate max-w-[150px]">
                          {record.community}
                        </div>
                      </td>

                      {/* Assigned Polling Station */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-1 font-bold text-xs text-slate-900">
                          <span className="font-mono text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.2 rounded border border-slate-200">
                            {ps.code}
                          </span>
                          <span className="truncate max-w-[180px]" title={ps.name}>
                            {ps.name}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{ps.constituency}</span>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3.5">
                        {!eligibility.isEligible ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            <AlertCircle className="w-3 h-3" />
                            Underage ({record.age}y)
                          </span>
                        ) : record.hasVoted ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-300">
                            <CheckCircle2 className="w-3 h-3" />
                            Ballot Cast
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                            <UserCheck className="w-3 h-3" />
                            Registered
                          </span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3.5 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          {eligibility.isEligible && (
                            <button
                              type="button"
                              onClick={() => onViewVoterCard(record)}
                              className="p-1.5 text-emerald-700 hover:text-emerald-900 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition-colors"
                              title="Generate Official Voter Card"
                            >
                              <IdCard className="w-4 h-4" />
                            </button>
                          )}

                          {eligibility.isEligible && !record.hasVoted && (
                            <button
                              type="button"
                              onClick={() => onMarkAsVoted(record.id)}
                              className="px-2.5 py-1 text-xs font-bold text-white bg-slate-900 hover:bg-purple-800 rounded-lg shadow-2xs transition-colors flex items-center gap-1"
                              title="Mark as Voted"
                            >
                              <Vote className="w-3 h-3 text-emerald-400" />
                              Vote
                            </button>
                          )}
                        </div>
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
  );
};
