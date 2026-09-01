'use client';

import React, { useState, useMemo } from 'react';
import { CensusRecord, Candidate } from '@/lib/types';
import { 
  INITIAL_CANDIDATES, 
  checkVoterEligibility, 
  getAssignedPollingStation, 
  generateVoterId,
  calculateElectionStats
} from '@/lib/electionData';
import { 
  Vote, 
  CheckCircle2, 
  Fingerprint, 
  AlertTriangle, 
  Search, 
  RotateCcw, 
  Sparkles, 
  TrendingUp, 
  ShieldCheck, 
  Award, 
  Zap, 
  Users, 
  UserCheck, 
  BarChart3,
  Flame
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, PieChart, Pie } from 'recharts';

interface Props {
  records: CensusRecord[];
  onUpdateRecord: (record: CensusRecord) => void;
  onBatchUpdateRecords: (records: CensusRecord[]) => void;
  onViewVoterCard: (record: CensusRecord) => void;
}

export const ElectionDayLiveView: React.FC<Props> = ({
  records,
  onUpdateRecord,
  onBatchUpdateRecords,
  onViewVoterCard
}) => {
  // Check-In Desk Search & Selection
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVoter, setSelectedVoter] = useState<CensusRecord | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [ballotCastSuccess, setBallotCastSuccess] = useState<string | null>(null);

  // Filter voters for lookup
  const lookupResults = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return [];
    return records.filter(r => 
      r.fullName.toLowerCase().includes(query) ||
      r.id.toLowerCase().includes(query) ||
      (r.voterIdNumber && r.voterIdNumber.toLowerCase().includes(query)) ||
      (r.nationalId && r.nationalId.toLowerCase().includes(query))
    ).slice(0, 6);
  }, [records, searchQuery]);

  // Tabulate votes per candidate directly from records
  const candidatesWithVotes = useMemo(() => {
    const voteMap = new Map<string, number>();
    INITIAL_CANDIDATES.forEach(c => voteMap.set(c.id, 0));

    records.forEach(r => {
      if (r.hasVoted && r.votedBallotSelection) {
        const count = voteMap.get(r.votedBallotSelection) || 0;
        voteMap.set(r.votedBallotSelection, count + 1);
      }
    });

    const list = INITIAL_CANDIDATES.map(c => ({
      ...c,
      votesCount: voteMap.get(c.id) || 0
    }));

    return list.sort((a, b) => b.votesCount - a.votesCount);
  }, [records]);

  const totalVotesCast = useMemo(() => {
    return records.filter(r => r.hasVoted).length;
  }, [records]);

  const stats = useMemo(() => calculateElectionStats(records), [records]);

  const leadingCandidate = candidatesWithVotes[0]?.votesCount > 0 ? candidatesWithVotes[0] : null;

  // Cast individual ballot
  const handleCastBallot = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedVoter || !selectedCandidateId) return;

    const eligibility = checkVoterEligibility(selectedVoter);
    if (!eligibility.isEligible) {
      alert('Voter is ineligible to vote.');
      return;
    }

    if (selectedVoter.hasVoted) {
      alert('Violation: Voter has already cast a ballot. Double voting is prohibited.');
      return;
    }

    const updated: CensusRecord = {
      ...selectedVoter,
      hasVoted: true,
      votedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      votedBallotSelection: selectedCandidateId,
      voterStatus: 'Registered'
    };

    onUpdateRecord(updated);
    setBallotCastSuccess(`Official ballot successfully cast for ${selectedVoter.fullName}! Indelible ink marked.`);
    setSelectedVoter(null);
    setSelectedCandidateId(null);
    setSearchQuery('');

    setTimeout(() => {
      setBallotCastSuccess(null);
    }, 4000);
  };

  // Simulate Turnout: randomly simulates voting for remaining eligible voters
  const handleSimulateTurnout = () => {
    const eligibleUnvoted = records.filter(r => checkVoterEligibility(r).isEligible && !r.hasVoted);
    if (eligibleUnvoted.length === 0) {
      alert('All eligible voters have already cast their ballots!');
      return;
    }

    const updatedList = records.map(r => {
      if (checkVoterEligibility(r).isEligible && !r.hasVoted) {
        // Random candidate selection with slight weighting
        const rand = Math.random();
        let chosenCandidate = INITIAL_CANDIDATES[0].id;
        if (rand < 0.40) chosenCandidate = INITIAL_CANDIDATES[0].id;
        else if (rand < 0.70) chosenCandidate = INITIAL_CANDIDATES[1].id;
        else if (rand < 0.88) chosenCandidate = INITIAL_CANDIDATES[2].id;
        else chosenCandidate = INITIAL_CANDIDATES[3].id;

        return {
          ...r,
          hasVoted: true,
          votedAt: 'Simulated 14:30',
          votedBallotSelection: chosenCandidate
        };
      }
      return r;
    });

    onBatchUpdateRecords(updatedList);
  };

  // Reset Election Simulation
  const handleResetElection = () => {
    if (confirm('Reset all voting records and turnout counters to 0? Registered voters will remain on the electoral roll.')) {
      const resetList = records.map(r => ({
        ...r,
        hasVoted: false,
        votedAt: undefined,
        votedBallotSelection: undefined
      }));
      onBatchUpdateRecords(resetList);
      setSelectedVoter(null);
      setSelectedCandidateId(null);
    }
  };

  // Turnout Demographic Data for Recharts
  const demographicTurnoutData = useMemo(() => {
    const youthVoted = records.filter(r => r.hasVoted && r.age >= 18 && r.age <= 24).length;
    const adultsVoted = records.filter(r => r.hasVoted && r.age >= 25 && r.age <= 54).length;
    const seniorsVoted = records.filter(r => r.hasVoted && r.age >= 55).length;

    return [
      { category: 'Youth (18-24)', count: youthVoted, color: '#10b981' },
      { category: 'Adults (25-54)', count: adultsVoted, color: '#3b82f6' },
      { category: 'Seniors (55+)', count: seniorsVoted, color: '#8b5cf6' },
    ];
  }, [records]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-7 border border-slate-800 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center shadow-inner">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-widest text-amber-400 uppercase bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-500/30">
                  Live Polling Day Operations
                </span>
                <span className="text-xs text-emerald-400 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  Polls Open
                </span>
              </div>
              <h2 className="text-lg sm:text-2xl font-black text-white tracking-tight mt-0.5">
                Election Day Check-In & Ballot Simulation
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <button
              type="button"
              onClick={handleSimulateTurnout}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow transition-all"
            >
              <Zap className="w-4 h-4" />
              Simulate Full Turnout
            </button>

            <button
              type="button"
              onClick={handleResetElection}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Ballots
            </button>
          </div>
        </div>

        {/* Live Counters */}
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Total Ballots Cast
            </div>
            <div className="text-2xl font-black text-emerald-400 mt-1">
              {totalVotesCast} <span className="text-xs font-normal text-slate-400">/ {stats.totalEligible}</span>
            </div>
            <div className="w-full bg-slate-700 h-2 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${stats.turnoutPercentage}%` }}
              ></div>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              National Turnout Rate
            </div>
            <div className="text-2xl font-black text-amber-400 mt-1">
              {stats.turnoutPercentage}%
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {stats.totalEligible - totalVotesCast} registered voters remaining
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Leading Candidate
            </div>
            <div className="text-sm font-extrabold text-white mt-1 truncate">
              {leadingCandidate ? leadingCandidate.name : 'Awaiting First Ballot'}
            </div>
            <div className="text-[11px] text-emerald-400 font-semibold mt-1">
              {leadingCandidate ? `${leadingCandidate.votesCount} Votes (${totalVotesCast > 0 ? Math.round((leadingCandidate.votesCount / totalVotesCast) * 100) : 0}%)` : '0 votes recorded'}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Electoral Integrity Status
            </div>
            <div className="flex items-center gap-1.5 text-sm font-bold text-emerald-300 mt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Indelible Ink Enforced
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Duplicate vote prevention active
            </div>
          </div>
        </div>
      </div>

      {/* Success Notification */}
      {ballotCastSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-300 text-emerald-900 text-xs sm:text-sm font-semibold flex items-center gap-2.5 shadow-sm">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>{ballotCastSuccess}</span>
        </div>
      )}

      {/* Main Grid: Voting Desk (7 cols) & Live Results Tabulation (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Voting Desk & Mock Ballot (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-xs space-y-6">
          {/* Desk Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-purple-50 text-purple-700 border border-purple-200">
                <Fingerprint className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-slate-900 text-sm sm:text-base tracking-tight">
                  Presiding Officer Check-In & Ballot Issuance
                </h3>
                <p className="text-xs text-slate-500">
                  Verify voter registration and cast secret ballot
                </p>
              </div>
            </div>
          </div>

          {/* Voter Search & Selector */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
              Step 1: Lookup Voter by Name, VRN, or Census ID
            </label>
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Type voter name (e.g. Deng, Taban, Achiro, Kiden)..."
                className="w-full pl-10 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:ring-2 focus:ring-slate-900 focus:outline-hidden"
              />
            </div>

            {/* Quick search dropdown results */}
            {lookupResults.length > 0 && (
              <div className="p-2 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 max-h-48 overflow-y-auto shadow-inner">
                {lookupResults.map(r => {
                  const eligibility = checkVoterEligibility(r);
                  const vrn = r.voterIdNumber || generateVoterId(r);

                  return (
                    <div
                      key={r.id}
                      onClick={() => {
                        setSelectedVoter(r);
                        setSearchQuery('');
                      }}
                      className="p-2.5 rounded-lg bg-white border border-slate-200/80 hover:border-emerald-500 hover:bg-emerald-50/40 cursor-pointer flex items-center justify-between text-xs transition-colors"
                    >
                      <div>
                        <div className="font-bold text-slate-900">{r.fullName}</div>
                        <div className="text-[11px] text-slate-500 font-mono">
                          {vrn} • {r.age} yrs • {r.tribe}
                        </div>
                      </div>
                      <div>
                        {r.hasVoted ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800">
                            Already Voted
                          </span>
                        ) : !eligibility.isEligible ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                            Ineligible ({r.age}y)
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            Eligible
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Selected Voter Banner */}
          {selectedVoter && (
            <div className="p-4 rounded-2xl bg-slate-900 text-white space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-wider block">
                    Active Voter at Desk
                  </span>
                  <h4 className="text-base font-black text-white">
                    {selectedVoter.fullName}
                  </h4>
                  <p className="text-xs text-slate-300">
                    VRN: <strong className="font-mono text-amber-300">{selectedVoter.voterIdNumber || generateVoterId(selectedVoter)}</strong> • {selectedVoter.age} yrs • {selectedVoter.gender}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => onViewVoterCard(selectedVoter)}
                  className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-xs font-semibold hover:bg-emerald-500/30 transition-colors"
                >
                  View Voter ID Card
                </button>
              </div>

              {selectedVoter.hasVoted ? (
                <div className="p-3 rounded-xl bg-purple-900/60 border border-purple-500/40 text-xs text-purple-200 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0" />
                  <span><strong>Indelible Ink Marked:</strong> This citizen has already voted at {selectedVoter.votedAt || 'earlier session'}. Ballot cannot be re-issued.</span>
                </div>
              ) : !checkVoterEligibility(selectedVoter).isEligible ? (
                <div className="p-3 rounded-xl bg-amber-900/60 border border-amber-500/40 text-xs text-amber-200 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>This citizen is under the legal voting age (18+ required).</span>
                </div>
              ) : (
                <div className="p-2.5 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Biometric Verified • Eligible to Mark Secret Ballot below</span>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Official Secret Ballot Box Simulator */}
          <form onSubmit={handleCastBallot} className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Step 2: Official Presidential Ballot Paper
              </label>
              <span className="text-[11px] text-slate-500">
                Select one candidate to stamp thumbprint
              </span>
            </div>

            {/* Candidate Ballot Slates */}
            <div className="space-y-2.5">
              {INITIAL_CANDIDATES.map((candidate) => {
                const isSelected = selectedCandidateId === candidate.id;
                const isVoterEligible = selectedVoter && checkVoterEligibility(selectedVoter).isEligible && !selectedVoter.hasVoted;

                return (
                  <div
                    key={candidate.id}
                    onClick={() => {
                      if (isVoterEligible) {
                        setSelectedCandidateId(candidate.id);
                      }
                    }}
                    className={`p-3.5 sm:p-4 rounded-2xl border-2 transition-all flex items-center justify-between gap-3 ${
                      !isVoterEligible ? 'opacity-60 cursor-not-allowed bg-slate-50 border-slate-200' :
                      isSelected 
                        ? 'border-emerald-600 bg-emerald-50/60 shadow-md ring-2 ring-emerald-500/20 cursor-pointer' 
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 cursor-pointer'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {/* Party Color Bar / Avatar */}
                      <div 
                        className="w-10 h-10 rounded-xl text-white font-black text-xs flex items-center justify-center shadow-xs shrink-0"
                        style={{ backgroundColor: candidate.color }}
                      >
                        {candidate.partyCode}
                      </div>

                      <div>
                        <h4 className="font-extrabold text-xs sm:text-sm text-slate-900">
                          {candidate.name}
                        </h4>
                        <div className="text-[11px] font-semibold text-slate-600">
                          {candidate.party}
                        </div>
                        <p className="text-[10px] text-slate-400 italic mt-0.5">
                          &ldquo;{candidate.slogan}&rdquo;
                        </p>
                      </div>
                    </div>

                    {/* Stamp / Checkbox Box */}
                    <div className="shrink-0 text-right">
                      {isSelected ? (
                        <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shadow">
                          <Fingerprint className="w-5 h-5" />
                        </div>
                      ) : (
                        <div className="w-9 h-9 rounded-xl border-2 border-dashed border-slate-300 flex items-center justify-center text-[10px] text-slate-400 font-bold">
                          VOTE
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Cast Ballot Action */}
            <button
              type="submit"
              disabled={!selectedVoter || !selectedCandidateId || selectedVoter.hasVoted || !checkVoterEligibility(selectedVoter).isEligible}
              className="w-full py-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-extrabold text-sm sm:text-base shadow-md transition-all flex items-center justify-center gap-2"
            >
              <Vote className="w-5 h-5" />
              Cast Secret Ballot & Mark Indelible Ink
            </button>
          </form>
        </div>

        {/* Live Results Tabulation Dashboard (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Candidate Standings & Vote Counts */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-600" />
                Live Presidential Results
              </h3>
              <span className="text-xs font-bold text-slate-500">
                {totalVotesCast} Votes Tallied
              </span>
            </div>

            {/* Candidate Standings list */}
            <div className="space-y-4">
              {candidatesWithVotes.map((candidate, index) => {
                const percentage = totalVotesCast > 0 ? Math.round((candidate.votesCount / totalVotesCast) * 100) : 0;
                const isLeader = index === 0 && candidate.votesCount > 0;

                return (
                  <div key={candidate.id} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-slate-900">
                        {isLeader && <Award className="w-3.5 h-3.5 text-amber-500" />}
                        <span>{candidate.name}</span>
                        <span className="text-[10px] text-slate-400 font-mono">({candidate.partyCode})</span>
                      </div>
                      <div className="font-black text-slate-900">
                        {candidate.votesCount} votes <span className="text-slate-500 font-normal">({percentage}%)</span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${percentage}%`,
                          backgroundColor: candidate.color
                        }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Recharts Bar Chart */}
            <div className="pt-4 border-t border-slate-100">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                Vote Share Visualizer
              </h4>
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={candidatesWithVotes}>
                    <XAxis dataKey="partyCode" stroke="#64748b" fontSize={10} />
                    <YAxis stroke="#64748b" fontSize={10} allowDecimals={false} />
                    <Tooltip 
                      formatter={(val) => [`${val} Votes`, 'Count']}
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '12px', fontSize: '12px' }}
                    />
                    <Bar dataKey="votesCount" radius={[6, 6, 0, 0]}>
                      {candidatesWithVotes.map((entry) => (
                        <Cell key={entry.id} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Demographic Turnout Breakdown */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-purple-600" />
              Turnout by Age Group
            </h4>

            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              {demographicTurnoutData.map(d => (
                <div key={d.category} className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-500 font-semibold">{d.category}</div>
                  <div className="text-base font-black text-slate-900 mt-0.5">{d.count}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
