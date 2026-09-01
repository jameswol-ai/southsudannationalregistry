'use client';

import React, { useState } from 'react';
import { CensusRecord, AdministrativeUnit } from '@/lib/types';
import { 
  getStoredAdministrativeUnits, 
  saveAdministrativeUnits,
  calculateAdministrativeSummaries 
} from '@/lib/administrativeData';
import { exportAdministrativeSummaryToCSV } from '@/lib/storage';
import { AdministrativeUnitModal } from './AdministrativeUnitModal';
import { 
  MapPin, 
  Building2, 
  Layers, 
  Users, 
  Home, 
  Search, 
  Plus, 
  Edit, 
  Trash2, 
  Download, 
  UserCheck, 
  ChevronRight, 
  ArrowUpDown,
  Filter,
  CheckCircle2,
  FileSpreadsheet
} from 'lucide-react';

interface Props {
  records: CensusRecord[];
  onEditPerson: (record: CensusRecord) => void;
  onNavigateToFormWithLocation?: (state: string, county: string, payam: string, boma: string) => void;
}

export const AdministrativeHierarchyView: React.FC<Props> = ({
  records,
  onEditPerson,
  onNavigateToFormWithLocation
}) => {
  const [adminUnits, setAdminUnits] = useState<AdministrativeUnit[]>(() => getStoredAdministrativeUnits());
  const [activeLevel, setActiveLevel] = useState<'County' | 'Payam' | 'Boma'>('County');
  const [searchTerm, setSearchTerm] = useState('');
  const [parentFilter, setParentFilter] = useState('ALL');
  
  // Selected unit for resident drilldown
  const [selectedUnitName, setSelectedUnitName] = useState<string | null>(null);
  
  // Modal state
  const [isUnitModalOpen, setIsUnitModalOpen] = useState(false);
  const [editingUnit, setEditingUnit] = useState<AdministrativeUnit | null>(null);
  const [modalDefaultType, setModalDefaultType] = useState<'County' | 'Payam' | 'Boma'>('County');

  // Compute summaries
  const summaries = calculateAdministrativeSummaries(records, adminUnits, activeLevel);

  // Filtered summaries
  const filteredSummaries = summaries.filter(s => {
    const matchesSearch = 
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.stateOrRegion && s.stateOrRegion.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (s.administratorName && s.administratorName.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesParent = 
      parentFilter === 'ALL' || 
      s.stateOrRegion === parentFilter || 
      s.countyOrPayam === parentFilter;

    return matchesSearch && matchesParent;
  });

  // Calculate high-level summary cards
  const totalCounted = records.length;
  const totalCounties = adminUnits.filter(u => u.type === 'County').length;
  const totalPayams = adminUnits.filter(u => u.type === 'Payam').length;
  const totalBomas = adminUnits.filter(u => u.type === 'Boma').length;
  const totalHouseholds = new Set(records.map(r => r.householdId).filter(Boolean)).size;

  // Filter options based on active level
  const parentOptions = Array.from(
    new Set(
      activeLevel === 'County' 
        ? adminUnits.filter(u => u.type === 'State').map(u => u.name)
        : activeLevel === 'Payam'
          ? adminUnits.filter(u => u.type === 'County').map(u => u.name)
          : adminUnits.filter(u => u.type === 'Payam').map(u => u.name)
    )
  );

  // Filter residents matching selected unit
  const selectedResidents = selectedUnitName
    ? records.filter(r => {
        if (activeLevel === 'County') {
          return (r.countyOrPayam && r.countyOrPayam.toLowerCase() === selectedUnitName.toLowerCase()) ||
                 (r.countyOrPayam && r.countyOrPayam.toLowerCase().includes(selectedUnitName.toLowerCase()));
        }
        if (activeLevel === 'Payam') {
          return (r.countyOrPayam && r.countyOrPayam.toLowerCase() === selectedUnitName.toLowerCase()) ||
                 (r.subCountyOrBoma && r.subCountyOrBoma.toLowerCase().includes(selectedUnitName.toLowerCase()));
        }
        if (activeLevel === 'Boma') {
          return (r.subCountyOrBoma && r.subCountyOrBoma.toLowerCase() === selectedUnitName.toLowerCase()) ||
                 (r.community && r.community.toLowerCase().includes(selectedUnitName.toLowerCase()));
        }
        return false;
      })
    : [];

  const handleSaveUnit = (savedUnit: AdministrativeUnit) => {
    let updated: AdministrativeUnit[];
    const exists = adminUnits.some(u => u.id === savedUnit.id);
    if (exists) {
      updated = adminUnits.map(u => u.id === savedUnit.id ? savedUnit : u);
    } else {
      updated = [savedUnit, ...adminUnits];
    }
    setAdminUnits(updated);
    saveAdministrativeUnits(updated);
  };

  const handleDeleteUnit = (id: string, name: string) => {
    if (confirm(`Are you sure you want to remove ${name} from the administrative units register?`)) {
      const updated = adminUnits.filter(u => u.id !== id);
      setAdminUnits(updated);
      saveAdministrativeUnits(updated);
      if (selectedUnitName === name) {
        setSelectedUnitName(null);
      }
    }
  };

  const handleOpenAddModal = (type: 'County' | 'Payam' | 'Boma') => {
    setEditingUnit(null);
    setModalDefaultType(type);
    setIsUnitModalOpen(true);
  };

  const handleOpenEditModal = (name: string) => {
    const found = adminUnits.find(u => u.name.toLowerCase() === name.toLowerCase() && u.type === activeLevel);
    if (found) {
      setEditingUnit(found);
      setModalDefaultType(activeLevel);
      setIsUnitModalOpen(true);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Stats */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-sm border border-slate-800 relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold uppercase tracking-wider mb-2 border border-emerald-500/30">
                <MapPin className="w-3.5 h-3.5" />
                Administrative Geographic Hierarchy
              </div>
              <h2 className="text-xl sm:text-2xl font-black tracking-tight text-white">
                Population Breakdown: Counties, Payams & Bomas
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 max-w-2xl mt-1">
                Manage territorial administrative units, monitor counted census density versus target projections, and edit local demographic records.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <button
                type="button"
                onClick={() => exportAdministrativeSummaryToCSV(summaries, activeLevel)}
                className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-bold bg-slate-800 hover:bg-slate-700 text-white rounded-xl border border-slate-700 transition-all shadow-xs"
              >
                <Download className="w-4 h-4 text-emerald-400" />
                Export {activeLevel}s CSV
              </button>

              <button
                type="button"
                onClick={() => handleOpenAddModal(activeLevel)}
                className="inline-flex items-center gap-2 px-4 py-2 text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl shadow-xs transition-all"
              >
                <Plus className="w-4 h-4" />
                Register New {activeLevel}
              </button>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-6 pt-6 border-t border-slate-800">
            <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50">
              <span className="text-[11px] font-medium text-slate-400 block">Total Enumerated</span>
              <span className="text-lg sm:text-xl font-extrabold text-white">
                {totalCounted.toLocaleString()}
              </span>
              <span className="text-[10px] text-emerald-400 block font-semibold">National Census</span>
            </div>

            <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50">
              <span className="text-[11px] font-medium text-slate-400 block">Total Counties</span>
              <span className="text-lg sm:text-xl font-extrabold text-white">
                {totalCounties}
              </span>
              <span className="text-[10px] text-blue-400 block font-semibold">Tier 1 Units</span>
            </div>

            <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50">
              <span className="text-[11px] font-medium text-slate-400 block">Total Payams</span>
              <span className="text-lg sm:text-xl font-extrabold text-white">
                {totalPayams}
              </span>
              <span className="text-[10px] text-purple-400 block font-semibold">Tier 2 Sub-counties</span>
            </div>

            <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50">
              <span className="text-[11px] font-medium text-slate-400 block">Total Bomas</span>
              <span className="text-lg sm:text-xl font-extrabold text-white">
                {totalBomas}
              </span>
              <span className="text-[10px] text-amber-400 block font-semibold">Tier 3 Grassroots</span>
            </div>

            <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50 col-span-2 sm:col-span-1">
              <span className="text-[11px] font-medium text-slate-400 block">Household Units</span>
              <span className="text-lg sm:text-xl font-extrabold text-white">
                {totalHouseholds}
              </span>
              <span className="text-[10px] text-slate-400 block">Avg ~{totalHouseholds > 0 ? (totalCounted / totalHouseholds).toFixed(1) : '0'} / HH</span>
            </div>
          </div>
        </div>
      </div>

      {/* Level Selector Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
          <button
            type="button"
            onClick={() => { setActiveLevel('County'); setParentFilter('ALL'); setSelectedUnitName(null); }}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 ${
              activeLevel === 'County'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200/80'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Building2 className="w-3.5 h-3.5 text-blue-600" />
            Counties ({totalCounties})
          </button>

          <button
            type="button"
            onClick={() => { setActiveLevel('Payam'); setParentFilter('ALL'); setSelectedUnitName(null); }}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 ${
              activeLevel === 'Payam'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200/80'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-purple-600" />
            Payams ({totalPayams})
          </button>

          <button
            type="button"
            onClick={() => { setActiveLevel('Boma'); setParentFilter('ALL'); setSelectedUnitName(null); }}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 ${
              activeLevel === 'Boma'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200/80'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <MapPin className="w-3.5 h-3.5 text-amber-600" />
            Bomas ({totalBomas})
          </button>
        </div>

        {/* Search & Parent Filter */}
        <div className="flex items-center gap-2">
          {parentOptions.length > 0 && (
            <select
              value={parentFilter}
              onChange={(e) => setParentFilter(e.target.value)}
              className="text-xs px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-700"
            >
              <option value="ALL">All Parent Divisions</option>
              {parentOptions.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          )}

          <div className="relative w-full sm:w-56">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={`Search ${activeLevel.toLowerCase()}s...`}
              className="w-full pl-8 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700"
            />
          </div>
        </div>
      </div>

      {/* Main Grid / Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Unit Summary Table - Spans 2 cols */}
        <div className={`space-y-3 ${selectedUnitName ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-slate-900">
                  {activeLevel} Demographic Register & Population Totals
                </h3>
                <p className="text-xs text-slate-500">
                  Showing {filteredSummaries.length} administrative {activeLevel.toLowerCase()}s
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-bold tracking-wider uppercase text-[10px]">
                    <th className="py-3 px-4">{activeLevel} Name</th>
                    <th className="py-3 px-3">Parent Region / County</th>
                    <th className="py-3 px-3 text-right">Counted Pop.</th>
                    <th className="py-3 px-3 text-right">Households</th>
                    <th className="py-3 px-3">Gender Ratio</th>
                    <th className="py-3 px-3 text-right">Eligible Voters</th>
                    <th className="py-3 px-3">Administrator</th>
                    <th className="py-3 px-4 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredSummaries.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-slate-400">
                        No {activeLevel.toLowerCase()}s match your search or filter.
                      </td>
                    </tr>
                  ) : (
                    filteredSummaries.map((summary) => {
                      const isSelected = selectedUnitName === summary.name;
                      const unitObj = adminUnits.find(u => u.name === summary.name && u.type === activeLevel);
                      const malePercent = summary.population > 0 ? Math.round((summary.maleCount / summary.population) * 100) : 50;

                      return (
                        <tr 
                          key={summary.name}
                          onClick={() => setSelectedUnitName(summary.name)}
                          className={`cursor-pointer transition-colors ${
                            isSelected 
                              ? 'bg-emerald-50/70 text-emerald-950 font-semibold' 
                              : 'hover:bg-slate-50/80 text-slate-700'
                          }`}
                        >
                          <td className="py-3.5 px-4 font-bold text-slate-900">
                            <div className="flex items-center gap-2">
                              <span className={`w-2 h-2 rounded-full ${
                                activeLevel === 'County' ? 'bg-blue-600' : activeLevel === 'Payam' ? 'bg-purple-600' : 'bg-amber-600'
                              }`} />
                              <span>{summary.name}</span>
                            </div>
                            {unitObj?.code && (
                              <span className="text-[10px] text-slate-400 font-mono block pl-4">
                                {unitObj.code}
                              </span>
                            )}
                          </td>

                          <td className="py-3.5 px-3 text-slate-600">
                            <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[11px]">
                              {summary.stateOrRegion || summary.countyOrPayam || 'National'}
                            </span>
                          </td>

                          <td className="py-3.5 px-3 text-right">
                            <span className="font-extrabold text-sm text-slate-900">
                              {summary.population}
                            </span>
                            {summary.targetPopulation && (
                              <span className="text-[10px] text-slate-400 block">
                                Target: {summary.targetPopulation.toLocaleString()}
                              </span>
                            )}
                          </td>

                          <td className="py-3.5 px-3 text-right font-medium">
                            {summary.householdsCount}
                          </td>

                          <td className="py-3.5 px-3">
                            <div className="w-24">
                              <div className="flex justify-between text-[10px] text-slate-500 mb-0.5">
                                <span>{summary.maleCount}M</span>
                                <span>{summary.femaleCount}F</span>
                              </div>
                              <div className="h-1.5 w-full bg-pink-200 rounded-full overflow-hidden flex">
                                <div 
                                  className="h-full bg-blue-500" 
                                  style={{ width: `${malePercent}%` }} 
                                />
                              </div>
                            </div>
                          </td>

                          <td className="py-3.5 px-3 text-right">
                            <span className="font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full border border-purple-200 text-[11px]">
                              {summary.votersEligibleCount} Voters
                            </span>
                          </td>

                          <td className="py-3.5 px-3 text-[11px] text-slate-600 max-w-[140px] truncate">
                            {summary.administratorName || 'Unassigned'}
                          </td>

                          <td className="py-3.5 px-4 text-center">
                            <div className="flex items-center justify-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                              <button
                                type="button"
                                title="Edit Administrative Unit Details"
                                onClick={() => handleOpenEditModal(summary.name)}
                                className="p-1.5 text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition-colors"
                              >
                                <Edit className="w-3.5 h-3.5" />
                              </button>

                              {unitObj && (
                                <button
                                  type="button"
                                  title="Delete Unit"
                                  onClick={() => handleDeleteUnit(unitObj.id, unitObj.name)}
                                  className="p-1.5 text-slate-400 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              )}

                              <button
                                type="button"
                                title="View Residents in this Unit"
                                onClick={() => setSelectedUnitName(summary.name)}
                                className={`p-1.5 rounded-lg transition-colors ${
                                  isSelected ? 'bg-emerald-700 text-white' : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                                }`}
                              >
                                <ChevronRight className="w-3.5 h-3.5" />
                              </button>
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

        {/* Drilldown Residents Panel (Opens when a unit is clicked) */}
        {selectedUnitName && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-4 flex flex-col max-h-[700px] overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 block">
                  {activeLevel} Residents Directory
                </span>
                <h3 className="font-extrabold text-slate-900 text-base">
                  {selectedUnitName}
                </h3>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                {selectedResidents.length} Citizens Counted
              </span>
            </div>

            {/* Residents List */}
            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 divide-y divide-slate-100">
              {selectedResidents.length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">
                  <p>No individual census records mapped directly to this {activeLevel.toLowerCase()} yet.</p>
                  <p className="mt-2 text-slate-500 font-medium">Use the Enumeration Form to add records or edit existing individuals.</p>
                </div>
              ) : (
                selectedResidents.map((person) => (
                  <div 
                    key={person.id}
                    className="pt-2.5 first:pt-0 flex items-center justify-between gap-3 text-xs"
                  >
                    <div>
                      <div className="font-bold text-slate-900 flex items-center gap-1.5">
                        <span>{person.fullName}</span>
                        {person.isHouseholdHead && (
                          <span className="text-[9px] bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded font-semibold">
                            Head
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-500 flex items-center gap-2 mt-0.5">
                        <span>{person.gender}, {person.age} yrs</span>
                        <span>&bull;</span>
                        <span className="truncate max-w-[120px]">{person.tribe}</span>
                        <span>&bull;</span>
                        <span className="font-mono text-[10px]">{person.householdId}</span>
                      </div>
                      {person.voterIdNumber && (
                        <span className="text-[10px] text-purple-700 font-mono font-medium block mt-0.5">
                          {person.voterIdNumber}
                        </span>
                      )}
                    </div>

                    {/* Quick Edit Trigger */}
                    <button
                      type="button"
                      onClick={() => onEditPerson(person)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors shrink-0"
                    >
                      <Edit className="w-3 h-3" />
                      Edit
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Quick Action to Register Resident in this unit */}
            <div className="pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => {
                  const stateVal = summaries.find(s => s.name === selectedUnitName)?.stateOrRegion || 'Central Equatoria';
                  const countyVal = activeLevel === 'County' ? selectedUnitName : '';
                  const payamVal = activeLevel === 'Payam' ? selectedUnitName : '';
                  const bomaVal = activeLevel === 'Boma' ? selectedUnitName : '';
                  if (onNavigateToFormWithLocation) {
                    onNavigateToFormWithLocation(stateVal, countyVal, payamVal, bomaVal);
                  }
                }}
                className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all text-center flex items-center justify-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5 text-emerald-400" />
                Enroll New Resident in {selectedUnitName}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Administrative Unit Modal */}
      <AdministrativeUnitModal
        isOpen={isUnitModalOpen}
        onClose={() => setIsUnitModalOpen(false)}
        unit={editingUnit}
        defaultType={modalDefaultType}
        onSave={handleSaveUnit}
      />
    </div>
  );
};
