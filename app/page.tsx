'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { CensusRecord } from '@/lib/types';
import { getStoredCensusRecords, saveCensusRecords, resetToInitialRecords } from '@/lib/storage';
import { calculateElectionStats, checkVoterEligibility } from '@/lib/electionData';
import { Navbar, ActiveTab } from '@/components/Navbar';
import { CensusRegistryTable } from '@/components/CensusRegistryTable';
import { EnumerationForm } from '@/components/EnumerationForm';
import { HouseholdUnitView } from '@/components/HouseholdUnitView';
import { DemographicAnalytics } from '@/components/DemographicAnalytics';
import { FieldQuickMode } from '@/components/FieldQuickMode';
import { CensusCertificateModal } from '@/components/CensusCertificateModal';
import { ExportImportModal } from '@/components/ExportImportModal';
import { ElectoralRollView } from '@/components/ElectoralRollView';
import { PollingStationsView } from '@/components/PollingStationsView';
import { ElectionDayLiveView } from '@/components/ElectionDayLiveView';
import { VoterCardModal } from '@/components/VoterCardModal';
import { AdminHierarchyView } from '@/components/AdminHierarchyView';
import { getStoredCounties } from '@/lib/adminHierarchy';

export default function CensusPage() {
  const [records, setRecords] = useState<CensusRecord[]>(() => {
    return getStoredCensusRecords();
  });
  const [activeTab, setActiveTab] = useState<ActiveTab>('registry');
  const [isClientLoaded, setIsClientLoaded] = useState(true);

  // Modals & Active Edit States
  const [selectedRecordForCert, setSelectedRecordForCert] = useState<CensusRecord | null>(null);
  const [selectedRecordForVoterCard, setSelectedRecordForVoterCard] = useState<CensusRecord | null>(null);
  const [editingRecord, setEditingRecord] = useState<CensusRecord | null>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  // Household member addition presets
  const [presetHouseholdId, setPresetHouseholdId] = useState<string | undefined>();
  const [presetCommunity, setPresetCommunity] = useState<string | undefined>();
  const [presetRegion, setPresetRegion] = useState<string | undefined>();

  // Subscribe to storage changes across sessions/tabs
  useEffect(() => {
    const handleStorageChange = () => {
      setRecords(getStoredCensusRecords());
    };

    window.addEventListener('census_data_changed', handleStorageChange);
    return () => {
      window.removeEventListener('census_data_changed', handleStorageChange);
    };
  }, []);

  // Save / Update Handler
  const handleSaveRecord = useCallback((record: CensusRecord) => {
    setRecords(prev => {
      const existsIndex = prev.findIndex(r => r.id === record.id);
      let updated: CensusRecord[];
      if (existsIndex >= 0) {
        updated = [...prev];
        updated[existsIndex] = record;
      } else {
        updated = [record, ...prev];
      }
      saveCensusRecords(updated);
      return updated;
    });

    if (editingRecord) {
      setEditingRecord(null);
      setActiveTab('registry');
    }
  }, [editingRecord]);

  // Batch update handler
  const handleBatchUpdateRecords = useCallback((updatedRecords: CensusRecord[]) => {
    setRecords(updatedRecords);
    saveCensusRecords(updatedRecords);
  }, []);

  // Fast Mark as Voted / Indelible Ink
  const handleMarkAsVoted = useCallback((recordId: string) => {
    setRecords(prev => {
      const updated = prev.map(r => {
        if (r.id === recordId) {
          return {
            ...r,
            hasVoted: true,
            votedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            votedBallotSelection: r.votedBallotSelection || 'CAND-01'
          };
        }
        return r;
      });
      saveCensusRecords(updated);
      return updated;
    });
  }, []);

  // Delete Single Record Handler
  const handleDeleteRecord = useCallback((id: string) => {
    setRecords(prev => {
      const updated = prev.filter(r => r.id !== id);
      saveCensusRecords(updated);
      return updated;
    });
  }, []);

  // Batch Delete Handler
  const handleBatchDeleteRecords = useCallback((ids: string[]) => {
    const idSet = new Set(ids);
    setRecords(prev => {
      const updated = prev.filter(r => !idSet.has(r.id));
      saveCensusRecords(updated);
      return updated;
    });
  }, []);

  // Clear/Wipe Entire Registry Handler
  const handleClearAllRegistry = useCallback(() => {
    setRecords([]);
    saveCensusRecords([]);
  }, []);

  // Bulk Import Handler
  const handleImportRecords = useCallback((imported: CensusRecord[]) => {
    setRecords(imported);
    saveCensusRecords(imported);
  }, []);

  // Start adding a member to an existing household unit
  const handleAddMemberToHousehold = (householdId: string, community: string, stateOrRegion: string) => {
    setEditingRecord(null);
    setPresetHouseholdId(householdId);
    setPresetCommunity(community);
    setPresetRegion(stateOrRegion);
    setActiveTab('form');
  };

  // Start editing a record
  const handleStartEdit = (record: CensusRecord) => {
    setEditingRecord(record);
    setPresetHouseholdId(undefined);
    setPresetCommunity(undefined);
    setPresetRegion(undefined);
    setActiveTab('form');
  };

  // Quick Stats for Navbar
  const totalHouseholds = useMemo(() => {
    return new Set(records.map(r => r.householdId).filter(Boolean)).size;
  }, [records]);

  const totalTribes = useMemo(() => {
    return new Set(records.map(r => r.tribe).filter(Boolean)).size;
  }, [records]);

  const electionStats = useMemo(() => {
    return calculateElectionStats(records);
  }, [records]);

  const totalCountiesCount = useMemo(() => {
    return getStoredCounties().length;
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 flex flex-col font-sans">
      {/* Top Header & Tab Navigation */}
      <Navbar
        activeTab={activeTab}
        onTabChange={(tab) => {
          if (tab !== 'form') {
            setEditingRecord(null);
            setPresetHouseholdId(undefined);
          }
          setActiveTab(tab);
        }}
        totalRecords={records.length}
        totalHouseholds={totalHouseholds}
        totalTribes={totalTribes}
        totalEligibleVoters={electionStats.totalEligible}
        totalVotesCast={electionStats.totalVotesCast}
        totalCounties={totalCountiesCount}
        onOpenExportModal={() => setIsExportModalOpen(true)}
      />

      {/* Main View Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {!isClientLoaded ? (
          <div className="flex items-center justify-center py-24 text-slate-500 text-sm">
            Loading Population Census & Electoral Portal...
          </div>
        ) : (
          <>
            {/* View 1: Census Registry Table */}
            {activeTab === 'registry' && (
              <CensusRegistryTable
                records={records}
                onViewCertificate={(rec) => setSelectedRecordForCert(rec)}
                onEditRecord={handleStartEdit}
                onDeleteRecord={handleDeleteRecord}
                onBatchDeleteRecords={handleBatchDeleteRecords}
                onClearRegistry={handleClearAllRegistry}
                onResetDefaultData={() => {
                  const reset = resetToInitialRecords();
                  setRecords(reset);
                }}
                onAddNew={() => {
                  setEditingRecord(null);
                  setPresetHouseholdId(undefined);
                  setActiveTab('form');
                }}
              />
            )}

            {/* View 1.5: Administrative Hierarchy: State Counties, Payams & Bomas */}
            {activeTab === 'admin-hierarchy' && (
              <AdminHierarchyView
                records={records}
                onBatchUpdateRecords={handleBatchUpdateRecords}
              />
            )}

            {/* View 2: Electoral Roll & Voter Register */}
            {activeTab === 'voters' && (
              <ElectoralRollView
                records={records}
                onViewVoterCard={(rec) => setSelectedRecordForVoterCard(rec)}
                onMarkAsVoted={handleMarkAsVoted}
              />
            )}

            {/* View 3: Polling Stations & Electoral Logistics */}
            {activeTab === 'polling-stations' && (
              <PollingStationsView
                records={records}
                onViewVoterCard={(rec) => setSelectedRecordForVoterCard(rec)}
                onMarkAsVoted={handleMarkAsVoted}
              />
            )}

            {/* View 4: Live Election Day Check-In & Ballot Simulation */}
            {activeTab === 'election-day' && (
              <ElectionDayLiveView
                records={records}
                onUpdateRecord={handleSaveRecord}
                onBatchUpdateRecords={handleBatchUpdateRecords}
                onViewVoterCard={(rec) => setSelectedRecordForVoterCard(rec)}
              />
            )}

            {/* View 5: Detailed Enumeration Form */}
            {activeTab === 'form' && (
              <EnumerationForm
                key={editingRecord ? editingRecord.id : `new-${presetHouseholdId || 'default'}`}
                existingRecord={editingRecord}
                existingRecords={records}
                onSave={handleSaveRecord}
                onCancel={() => {
                  setEditingRecord(null);
                  setPresetHouseholdId(undefined);
                  setActiveTab('registry');
                }}
                defaultHouseholdId={presetHouseholdId}
                defaultCommunity={presetCommunity}
                defaultStateOrRegion={presetRegion}
              />
            )}

            {/* View 6: Household Unit & Family Grouping View */}
            {activeTab === 'households' && (
              <HouseholdUnitView
                records={records}
                onAddMemberToHousehold={handleAddMemberToHousehold}
                onViewRecord={(rec) => setSelectedRecordForCert(rec)}
              />
            )}

            {/* View 7: Demographics & Analytics Dashboard */}
            {activeTab === 'analytics' && (
              <DemographicAnalytics records={records} />
            )}

            {/* View 8: Rapid Field Enumerator Mode */}
            {activeTab === 'quick-field' && (
              <FieldQuickMode
                existingRecords={records}
                onSaveRecord={handleSaveRecord}
              />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            <strong>National Population Census & Electoral Commission Portal</strong> • Official Demographic & Vital Registry
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Confidential & Protected Voter Records</span>
            <span>•</span>
            <span>Offline-Enabled Local Storage</span>
          </div>
        </div>
      </footer>

      {/* Census Certificate Slip Modal */}
      <CensusCertificateModal
        record={selectedRecordForCert}
        isOpen={!!selectedRecordForCert}
        onClose={() => setSelectedRecordForCert(null)}
        onEdit={handleStartEdit}
      />

      {/* Official Voter Identity Card Modal */}
      <VoterCardModal
        record={selectedRecordForVoterCard}
        isOpen={!!selectedRecordForVoterCard}
        onClose={() => setSelectedRecordForVoterCard(null)}
        onMarkAsVoted={handleMarkAsVoted}
      />

      {/* Export / Import Modal */}
      <ExportImportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        records={records}
        onImportRecords={handleImportRecords}
      />
    </div>
  );
}
