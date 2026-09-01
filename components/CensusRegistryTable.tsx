'use client';

import React, { useState, useMemo } from 'react';
import { CensusRecord } from '@/lib/types';
import { exportToCSV } from '@/lib/storage';
import { 
  Search, 
  Filter, 
  FileText, 
  Edit3, 
  Trash2, 
  Download, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  ArrowUpDown, 
  Users, 
  Building2, 
  MapPin, 
  Sparkles,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
  Plus
} from 'lucide-react';

interface Props {
  records: CensusRecord[];
  onViewCertificate: (record: CensusRecord) => void;
  onEditRecord: (record: CensusRecord) => void;
  onDeleteRecord: (id: string) => void;
  onBatchDeleteRecords?: (ids: string[]) => void;
  onClearRegistry?: () => void;
  onResetDefaultData?: () => void;
  onAddNew: () => void;
}

export const CensusRegistryTable: React.FC<Props> = ({
  records,
  onViewCertificate,
  onEditRecord,
  onDeleteRecord,
  onBatchDeleteRecords,
  onClearRegistry,
  onResetDefaultData,
  onAddNew
}) => {
  // Search and Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTribe, setSelectedTribe] = useState<string>('ALL');
  const [selectedCommunity, setSelectedCommunity] = useState<string>('ALL');
  const [selectedGender, setSelectedGender] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedAgeGroup, setSelectedAgeGroup] = useState<string>('ALL');

  // Sorting
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'age' | 'tribe' | 'community'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Selected records for batch deletion or export
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const [deleteConfirmTarget, setDeleteConfirmTarget] = useState<CensusRecord | null>(null);
  const [isBulkDeleteModalOpen, setIsBulkDeleteModalOpen] = useState(false);
  const [isWipeRegistryModalOpen, setIsWipeRegistryModalOpen] = useState(false);
  const [wipeConfirmText, setWipeConfirmText] = useState('');

  // Distinct Filter options
  const uniqueTribes = useMemo(() => {
    return Array.from(new Set(records.map(r => r.tribe).filter(Boolean))).sort();
  }, [records]);

  const uniqueCommunities = useMemo(() => {
    return Array.from(new Set(records.map(r => r.community).filter(Boolean))).sort();
  }, [records]);

  // Filtering Logic
  const filteredRecords = useMemo(() => {
    return records.filter(record => {
      // Search match
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const matchesName = record.fullName.toLowerCase().includes(query);
        const matchesId = record.id.toLowerCase().includes(query);
        const matchesNationalId = (record.nationalId || '').toLowerCase().includes(query);
        const matchesTribe = record.tribe.toLowerCase().includes(query);
        const matchesComm = record.community.toLowerCase().includes(query);
        const matchesHh = record.householdId.toLowerCase().includes(query);
        const matchesEnum = (record.enumeratorName || '').toLowerCase().includes(query);

        if (!matchesName && !matchesId && !matchesNationalId && !matchesTribe && !matchesComm && !matchesHh && !matchesEnum) {
          return false;
        }
      }

      // Tribe filter
      if (selectedTribe !== 'ALL' && record.tribe !== selectedTribe) {
        return false;
      }

      // Community filter
      if (selectedCommunity !== 'ALL' && record.community !== selectedCommunity) {
        return false;
      }

      // Gender filter
      if (selectedGender !== 'ALL' && record.gender !== selectedGender) {
        return false;
      }

      // Verification Status filter
      if (selectedStatus !== 'ALL' && record.verificationStatus !== selectedStatus) {
        return false;
      }

      // Age bracket filter
      if (selectedAgeGroup !== 'ALL') {
        const age = record.age;
        if (selectedAgeGroup === '0-14' && !(age >= 0 && age <= 14)) return false;
        if (selectedAgeGroup === '15-24' && !(age >= 15 && age <= 24)) return false;
        if (selectedAgeGroup === '25-54' && !(age >= 25 && age <= 54)) return false;
        if (selectedAgeGroup === '55+' && !(age >= 55)) return false;
      }

      return true;
    });
  }, [records, searchTerm, selectedTribe, selectedCommunity, selectedGender, selectedStatus, selectedAgeGroup]);

  // Sorted Records
  const sortedRecords = useMemo(() => {
    return [...filteredRecords].sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'name') {
        comparison = a.fullName.localeCompare(b.fullName);
      } else if (sortBy === 'age') {
        comparison = a.age - b.age;
      } else if (sortBy === 'tribe') {
        comparison = a.tribe.localeCompare(b.tribe);
      } else if (sortBy === 'community') {
        comparison = a.community.localeCompare(b.community);
      } else if (sortBy === 'date') {
        comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [filteredRecords, sortBy, sortOrder]);

  // Paginated records
  const totalPages = Math.ceil(sortedRecords.length / pageSize) || 1;
  const paginatedRecords = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedRecords.slice(start, start + pageSize);
  }, [sortedRecords, currentPage, pageSize]);

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(new Set(paginatedRecords.map(r => r.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleToggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  };

  const handleSortChange = (newSort: 'date' | 'name' | 'age' | 'tribe' | 'community') => {
    if (sortBy === newSort) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSort);
      setSortOrder('asc');
    }
  };

  const handleExportFiltered = () => {
    exportToCSV(filteredRecords);
  };

  return (
    <div className="space-y-4">
      {/* Search & Action Bar */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-4 sm:p-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[280px]">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              id="census-search-input"
              type="text"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Search by name, National ID, tribe, community, household ID, or enumerator..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 bg-slate-50/50"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-slate-400 hover:text-slate-700"
              >
                Clear
              </button>
            )}
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2.5 flex-wrap">
            {records.length > 0 && onClearRegistry && (
              <button
                id="wipe-registry-trigger-btn"
                type="button"
                onClick={() => {
                  setWipeConfirmText('');
                  setIsWipeRegistryModalOpen(true);
                }}
                className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-xl transition-colors shadow-2xs"
                title="Delete or Wipe all records from the Census Registry"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                Delete All ({records.length})
              </button>
            )}

            <button
              id="export-csv-table-btn"
              type="button"
              onClick={handleExportFiltered}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl transition-colors shadow-xs"
            >
              <Download className="w-3.5 h-3.5 text-slate-600" />
              Export Filtered ({filteredRecords.length})
            </button>

            <button
              id="add-new-person-table-btn"
              type="button"
              onClick={onAddNew}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-xl transition-colors shadow-xs active:scale-[0.99]"
            >
              <Plus className="w-4 h-4 text-emerald-400" />
              New Enumeration
            </button>
          </div>
        </div>

        {/* Filter Badges / Dropdowns */}
        <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs">
          {/* Tribe Filter */}
          <div>
            <label className="block font-semibold text-slate-600 mb-1 text-[11px] uppercase tracking-wider">
              Tribe / Ethnicity
            </label>
            <select
              id="filter-tribe-select"
              value={selectedTribe}
              onChange={(e) => {
                setSelectedTribe(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-800 focus:ring-1 focus:ring-slate-900 text-xs"
            >
              <option value="ALL">All Tribes ({records.length})</option>
              {uniqueTribes.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* Community Filter */}
          <div>
            <label className="block font-semibold text-slate-600 mb-1 text-[11px] uppercase tracking-wider">
              Community / Settlement
            </label>
            <select
              id="filter-community-select"
              value={selectedCommunity}
              onChange={(e) => {
                setSelectedCommunity(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-800 focus:ring-1 focus:ring-slate-900 text-xs"
            >
              <option value="ALL">All Communities</option>
              {uniqueCommunities.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Gender Filter */}
          <div>
            <label className="block font-semibold text-slate-600 mb-1 text-[11px] uppercase tracking-wider">
              Gender
            </label>
            <select
              id="filter-gender-select"
              value={selectedGender}
              onChange={(e) => {
                setSelectedGender(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-800 focus:ring-1 focus:ring-slate-900 text-xs"
            >
              <option value="ALL">All Genders</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Age Bracket */}
          <div>
            <label className="block font-semibold text-slate-600 mb-1 text-[11px] uppercase tracking-wider">
              Age Group
            </label>
            <select
              id="filter-age-select"
              value={selectedAgeGroup}
              onChange={(e) => {
                setSelectedAgeGroup(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-800 focus:ring-1 focus:ring-slate-900 text-xs"
            >
              <option value="ALL">All Ages</option>
              <option value="0-14">Children (0 - 14 yrs)</option>
              <option value="15-24">Youth (15 - 24 yrs)</option>
              <option value="25-54">Adults (25 - 54 yrs)</option>
              <option value="55+">Seniors (55+ yrs)</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block font-semibold text-slate-600 mb-1 text-[11px] uppercase tracking-wider">
              Verification Status
            </label>
            <select
              id="filter-status-select"
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-800 focus:ring-1 focus:ring-slate-900 text-xs"
            >
              <option value="ALL">All Statuses</option>
              <option value="Verified">Verified</option>
              <option value="Pending Review">Pending Review</option>
              <option value="Flagged">Flagged</option>
            </select>
          </div>
        </div>

        {/* Active Filter Tags */}
        {(selectedTribe !== 'ALL' || selectedCommunity !== 'ALL' || selectedGender !== 'ALL' || selectedStatus !== 'ALL' || selectedAgeGroup !== 'ALL' || searchTerm) && (
          <div className="mt-3 flex items-center gap-2 flex-wrap text-xs pt-2 border-t border-slate-100">
            <span className="text-slate-500 font-medium">Filtered by:</span>
            {searchTerm && (
              <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-800 border border-slate-200">
                Search: &ldquo;{searchTerm}&rdquo;
              </span>
            )}
            {selectedTribe !== 'ALL' && (
              <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                Tribe: {selectedTribe}
              </span>
            )}
            {selectedCommunity !== 'ALL' && (
              <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-800 border border-blue-200">
                Community: {selectedCommunity}
              </span>
            )}
            {selectedGender !== 'ALL' && (
              <span className="px-2 py-0.5 rounded-md bg-purple-50 text-purple-800 border border-purple-200">
                Gender: {selectedGender}
              </span>
            )}
            {selectedAgeGroup !== 'ALL' && (
              <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200">
                Age: {selectedAgeGroup}
              </span>
            )}
            {selectedStatus !== 'ALL' && (
              <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-800 border border-slate-300">
                Status: {selectedStatus}
              </span>
            )}
            <button
              type="button"
              onClick={() => {
                setSearchTerm('');
                setSelectedTribe('ALL');
                setSelectedCommunity('ALL');
                setSelectedGender('ALL');
                setSelectedStatus('ALL');
                setSelectedAgeGroup('ALL');
              }}
              className="text-xs text-red-600 hover:text-red-700 underline font-semibold ml-auto"
            >
              Reset All Filters
            </button>
          </div>
        )}
      </div>

      {/* Bulk Action Bar for Selected Records */}
      {selectedIds.size > 0 && (
        <div className="bg-slate-900 text-white px-5 py-3 rounded-2xl flex flex-wrap items-center justify-between gap-3 shadow-lg border border-slate-800 animate-in fade-in duration-150">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-emerald-500 text-slate-950 font-bold text-xs flex items-center justify-center">
              {selectedIds.size}
            </span>
            <span className="font-semibold text-xs sm:text-sm">
              {selectedIds.size} record{selectedIds.size > 1 ? 's' : ''} selected in registry
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                const selectedList = records.filter(r => selectedIds.has(r.id));
                exportToCSV(selectedList);
              }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl transition-colors border border-slate-700"
            >
              <Download className="w-3.5 h-3.5 text-emerald-400" />
              Export Selected
            </button>

            {onBatchDeleteRecords && (
              <button
                id="bulk-delete-btn"
                type="button"
                onClick={() => setIsBulkDeleteModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-rose-600 hover:bg-rose-700 text-white rounded-xl transition-colors shadow-2xs"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Delete Selected ({selectedIds.size})
              </button>
            )}

            <button
              type="button"
              onClick={() => setSelectedIds(new Set())}
              className="text-xs text-slate-400 hover:text-white px-2 py-1 underline font-medium"
            >
              Deselect All
            </button>
          </div>
        </div>
      )}

      {/* Main Table Container */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm border-collapse">
            <thead>
              <tr className="bg-slate-900 text-white font-semibold text-xs uppercase tracking-wider">
                <th className="py-3.5 px-4 w-10">
                  <input
                    type="checkbox"
                    checked={paginatedRecords.length > 0 && paginatedRecords.every(r => selectedIds.has(r.id))}
                    onChange={handleSelectAll}
                    className="w-4 h-4 rounded border-slate-400 text-emerald-500 focus:ring-emerald-400"
                  />
                </th>
                <th className="py-3.5 px-4">
                  <button
                    type="button"
                    onClick={() => handleSortChange('name')}
                    className="inline-flex items-center gap-1 hover:text-emerald-300 transition-colors uppercase"
                  >
                    Name & Identity
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="py-3.5 px-4">
                  <button
                    type="button"
                    onClick={() => handleSortChange('tribe')}
                    className="inline-flex items-center gap-1 hover:text-emerald-300 transition-colors uppercase"
                  >
                    Tribe & Clan
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="py-3.5 px-4">
                  <button
                    type="button"
                    onClick={() => handleSortChange('community')}
                    className="inline-flex items-center gap-1 hover:text-emerald-300 transition-colors uppercase"
                  >
                    Community / Location
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="py-3.5 px-4">
                  <button
                    type="button"
                    onClick={() => handleSortChange('age')}
                    className="inline-flex items-center gap-1 hover:text-emerald-300 transition-colors uppercase"
                  >
                    Demographics
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="py-3.5 px-4">Household & Role</th>
                <th className="py-3.5 px-4">Occupation / Education</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedRecords.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <div className="max-w-md mx-auto space-y-2">
                      <Users className="w-10 h-10 mx-auto text-slate-400" />
                      <p className="font-semibold text-slate-800 text-base">No census records matched your criteria</p>
                      <p className="text-xs text-slate-500">
                        Try adjusting your filters or register a new individual into the population registry.
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                paginatedRecords.map((record) => {
                  const isSelected = selectedIds.has(record.id);
                  return (
                    <tr 
                      key={record.id}
                      className={`hover:bg-slate-50/90 transition-colors ${isSelected ? 'bg-emerald-50/40' : ''}`}
                    >
                      {/* Checkbox */}
                      <td className="py-3 px-4">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleToggleSelect(record.id)}
                          className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                        />
                      </td>

                      {/* Name & ID */}
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-900">{record.fullName}</div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="font-mono text-[11px] font-semibold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                            {record.id}
                          </span>
                          {record.nationalId && (
                            <span className="text-[11px] text-slate-500 font-mono">
                              ID: {record.nationalId}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Tribe & Clan */}
                      <td className="py-3 px-4">
                        <div className="font-semibold text-slate-900 flex items-center gap-1.5">
                          <Sparkles className="w-3 h-3 text-amber-600 shrink-0" />
                          <span>{record.tribe}</span>
                        </div>
                        {record.subTribeOrClan && (
                          <div className="text-[11px] text-slate-500 mt-0.5">
                            Clan: {record.subTribeOrClan}
                          </div>
                        )}
                        <div className="text-[11px] text-slate-500">
                          Lang: {record.nativeLanguage}
                        </div>
                      </td>

                      {/* Community / Location */}
                      <td className="py-3 px-4">
                        <div className="font-semibold text-slate-900 flex items-center gap-1.5">
                          <MapPin className="w-3 h-3 text-blue-600 shrink-0" />
                          <span>{record.community}</span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          {record.countyOrPayam}, {record.stateOrRegion}
                        </div>
                      </td>

                      {/* Demographics (Age/Gender/Marital) */}
                      <td className="py-3 px-4">
                        <div className="font-medium text-slate-900">
                          {record.age} yrs • {record.gender}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          {record.maritalStatus}
                        </div>
                      </td>

                      {/* Household */}
                      <td className="py-3 px-4">
                        <div className="inline-flex items-center gap-1 font-mono font-bold text-xs text-purple-900 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                          <Building2 className="w-3 h-3" />
                          {record.householdId}
                        </div>
                        <div className="text-[11px] text-slate-700 mt-0.5 font-medium">
                          {record.householdRole} {record.isHouseholdHead && '★ Head'}
                        </div>
                      </td>

                      {/* Occupation & Education */}
                      <td className="py-3 px-4">
                        <div className="font-medium text-slate-900 line-clamp-1">
                          {record.primaryOccupation || record.employmentStatus}
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          Edu: {record.educationLevel}
                        </div>
                      </td>

                      {/* Verification Status */}
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
                          record.verificationStatus === 'Verified' 
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                            : record.verificationStatus === 'Pending Review'
                            ? 'bg-amber-50 text-amber-700 border-amber-200'
                            : 'bg-red-50 text-red-700 border-red-200'
                        }`}>
                          {record.verificationStatus === 'Verified' && <CheckCircle2 className="w-3 h-3" />}
                          {record.verificationStatus === 'Pending Review' && <Clock className="w-3 h-3" />}
                          {record.verificationStatus === 'Flagged' && <AlertTriangle className="w-3 h-3" />}
                          {record.verificationStatus}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* View Certificate Slip */}
                          <button
                            id={`view-slip-btn-${record.id}`}
                            type="button"
                            onClick={() => onViewCertificate(record)}
                            title="View Official Certificate Slip"
                            className="p-1.5 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition-colors"
                          >
                            <FileText className="w-4 h-4" />
                          </button>

                          {/* Edit */}
                          <button
                            id={`edit-record-btn-${record.id}`}
                            type="button"
                            onClick={() => onEditRecord(record)}
                            title="Edit Record"
                            className="p-1.5 text-slate-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>

                          {/* Delete */}
                          <button
                            id={`delete-record-btn-${record.id}`}
                            type="button"
                            onClick={() => setDeleteConfirmTarget(record)}
                            title="Delete Record"
                            className="p-1.5 text-slate-400 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
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

        {/* Table Footer & Pagination */}
        <div className="px-4 sm:px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <span>
              Showing <span className="font-semibold text-slate-900">{filteredRecords.length ? (currentPage - 1) * pageSize + 1 : 0}</span> to{' '}
              <span className="font-semibold text-slate-900">{Math.min(currentPage * pageSize, filteredRecords.length)}</span> of{' '}
              <span className="font-semibold text-slate-900">{filteredRecords.length}</span> registered persons
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500">Per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="px-2 py-1 bg-white border border-slate-300 rounded-md text-xs font-semibold"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>

            <div className="flex items-center gap-1">
              <button
                id="pagination-prev-btn"
                type="button"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                className="p-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed text-slate-700"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-2 font-medium">
                Page {currentPage} of {totalPages}
              </span>
              <button
                id="pagination-next-btn"
                type="button"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                className="p-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed text-slate-700"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 1. Modal: Single Record Deletion Confirmation */}
      {deleteConfirmTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="w-full max-w-md bg-white rounded-2xl p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center gap-3 text-rose-600">
              <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center shrink-0">
                <Trash2 className="w-5 h-5 text-rose-600" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base">Delete Census Record</h3>
                <p className="text-xs text-slate-500">This action removes the citizen from the national registry</p>
              </div>
            </div>

            <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200 text-xs space-y-1.5 text-slate-700">
              <div>
                <span className="text-slate-500 font-medium">Citizen Name: </span>
                <span className="font-bold text-slate-900">{deleteConfirmTarget.fullName}</span>
              </div>
              <div>
                <span className="text-slate-500 font-medium">Census ID / Document: </span>
                <span className="font-mono font-semibold">{deleteConfirmTarget.id} • {deleteConfirmTarget.nationalId || deleteConfirmTarget.passportNumber || 'No ID Ref'}</span>
              </div>
              <div>
                <span className="text-slate-500 font-medium">Location: </span>
                <span>{deleteConfirmTarget.community}, {deleteConfirmTarget.countyOrPayam} ({deleteConfirmTarget.stateOrRegion})</span>
              </div>
              <div>
                <span className="text-slate-500 font-medium">Household: </span>
                <span className="font-mono">{deleteConfirmTarget.householdId}</span> ({deleteConfirmTarget.householdRole})
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setDeleteConfirmTarget(null)}
                className="px-4 py-2 text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                id="confirm-single-delete-btn"
                type="button"
                onClick={() => {
                  onDeleteRecord(deleteConfirmTarget.id);
                  setDeleteConfirmTarget(null);
                }}
                className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl transition-colors shadow-xs"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Modal: Bulk Selection Deletion Confirmation */}
      {isBulkDeleteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="w-full max-w-md bg-white rounded-2xl p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center gap-3 text-rose-600">
              <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5 text-rose-600" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base">Bulk Delete {selectedIds.size} Records</h3>
                <p className="text-xs text-slate-500">Permanent removal of selected citizens from the registry</p>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              You are about to permanently delete <strong className="text-slate-900">{selectedIds.size}</strong> selected census profile{selectedIds.size > 1 ? 's' : ''}. Their associated voter rolls, household associations, and enumeration records will be removed.
            </p>

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setIsBulkDeleteModalOpen(false)}
                className="px-4 py-2 text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                id="confirm-bulk-delete-btn"
                type="button"
                onClick={() => {
                  if (onBatchDeleteRecords) {
                    onBatchDeleteRecords(Array.from(selectedIds));
                  }
                  setSelectedIds(new Set());
                  setIsBulkDeleteModalOpen(false);
                }}
                className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl transition-colors shadow-xs"
              >
                Delete {selectedIds.size} Records
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. Modal: Clear / Wipe Entire Registry Confirmation */}
      {isWipeRegistryModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="w-full max-w-lg bg-white rounded-2xl p-6 shadow-2xl border border-rose-200 space-y-4">
            <div className="flex items-center gap-3 text-rose-600">
              <div className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center shrink-0">
                <Trash2 className="w-6 h-6 text-rose-600" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base sm:text-lg">Wipe & Clear Entire Registry</h3>
                <p className="text-xs text-rose-600 font-semibold">Destructive Operation: Clears all {records.length} citizen records</p>
              </div>
            </div>

            <div className="bg-rose-50 border border-rose-200 rounded-xl p-3.5 text-xs text-rose-900 space-y-2">
              <p className="font-semibold">
                Warning: This will delete ALL {records.length} census profiles and electoral roll registers in this session.
              </p>
              <p className="text-[11px] text-rose-800">
                To prevent accidental deletion, type <strong className="font-mono uppercase bg-white px-1.5 py-0.5 rounded border border-rose-300">DELETE</strong> in the box below to unlock the confirmation button.
              </p>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Type &ldquo;DELETE&rdquo; to confirm:
              </label>
              <input
                id="wipe-registry-confirm-input"
                type="text"
                value={wipeConfirmText}
                onChange={(e) => setWipeConfirmText(e.target.value)}
                placeholder="Type DELETE here"
                className="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-rose-500 font-mono"
              />
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-100 gap-2 flex-wrap">
              {onResetDefaultData && (
                <button
                  type="button"
                  onClick={() => {
                    onResetDefaultData();
                    setIsWipeRegistryModalOpen(false);
                    setWipeConfirmText('');
                  }}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900 underline"
                >
                  Restore Demo Baseline Data Instead
                </button>
              )}

              <div className="flex items-center gap-2 ml-auto">
                <button
                  type="button"
                  onClick={() => {
                    setIsWipeRegistryModalOpen(false);
                    setWipeConfirmText('');
                  }}
                  className="px-4 py-2 text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  id="confirm-wipe-registry-btn"
                  type="button"
                  disabled={wipeConfirmText.trim().toUpperCase() !== 'DELETE'}
                  onClick={() => {
                    if (onClearRegistry) {
                      onClearRegistry();
                    }
                    setSelectedIds(new Set());
                    setIsWipeRegistryModalOpen(false);
                    setWipeConfirmText('');
                  }}
                  className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl transition-colors shadow-xs"
                >
                  Wipe Registry ({records.length})
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
