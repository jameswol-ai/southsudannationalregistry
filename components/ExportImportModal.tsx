'use client';

import React, { useState } from 'react';
import { CensusRecord } from '@/lib/types';
import { 
  exportToCSV, 
  exportElectoralRollToCSV, 
  exportToJSON, 
  downloadCensusCSVTemplate,
  parseCSVToCensusRecords,
  resetToInitialRecords 
} from '@/lib/storage';
import { 
  X, 
  Download, 
  Upload, 
  RotateCcw, 
  FileSpreadsheet, 
  FileCode, 
  CheckCircle2, 
  AlertCircle,
  Database,
  Vote,
  FileDown,
  Info,
  ShieldCheck
} from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  records: CensusRecord[];
  onImportRecords: (records: CensusRecord[]) => void;
}

export const ExportImportModal: React.FC<Props> = ({
  isOpen,
  onClose,
  records,
  onImportRecords
}) => {
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [importWarnings, setImportWarnings] = useState<string[]>([]);
  const [importMode, setImportMode] = useState<'csv' | 'json'>('csv');

  if (!isOpen) return null;

  const handleJsonFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    setImportStatus(null);
    setImportWarnings([]);
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result as string;
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed) && parsed.length > 0) {
          onImportRecords(parsed);
          setImportStatus(`Successfully restored ${parsed.length} census records from JSON backup!`);
        } else {
          setErrorMessage('Invalid census JSON format. Expected an array of CensusRecord objects.');
        }
      } catch (err) {
        setErrorMessage('Failed to parse JSON file. Ensure it is a valid backup export.');
      }
    };
    reader.readAsText(file);
  };

  const handleCsvFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    setImportStatus(null);
    setImportWarnings([]);
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result as string;
        const result = parseCSVToCensusRecords(text);

        if (result.errors.length > 0) {
          setErrorMessage(result.errors.join(' | '));
          return;
        }

        if (result.records.length === 0) {
          setErrorMessage('No valid census records found in the provided CSV file.');
          return;
        }

        // Merge or replace options: we append or replace
        onImportRecords(result.records);
        setImportStatus(`Successfully ingested ${result.records.length} citizen & household records from CSV!`);
        if (result.warnings.length > 0) {
          setImportWarnings(result.warnings.slice(0, 3));
        }
      } catch (err) {
        setErrorMessage('Failed to process CSV file. Ensure it follows the official column format.');
      }
    };
    reader.readAsText(file);
  };

  const handleReset = () => {
    if (confirm('Reset census database to the default official initial dataset? Any custom additions will be replaced with the standard demo dataset.')) {
      const reset = resetToInitialRecords();
      onImportRecords(reset);
      setImportStatus('Census database reset to initial official national dataset (15 profiles).');
      setErrorMessage(null);
      setImportWarnings([]);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs">
      <div 
        id="export-import-modal"
        className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white shrink-0">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="font-bold text-sm tracking-wide uppercase">
                Census Data Portability, Import & Export
              </h3>
              <p className="text-[11px] text-slate-400">
                Official National Commission Data Exchange Protocol
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {importStatus && (
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs sm:text-sm flex items-center gap-2 font-medium">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{importStatus}</span>
            </div>
          )}

          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs sm:text-sm flex items-center gap-2 font-medium">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {importWarnings.length > 0 && (
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs space-y-1">
              <div className="font-bold flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-amber-600" />
                Import Notices:
              </div>
              {importWarnings.map((w, idx) => (
                <div key={idx} className="pl-4 text-[11px]">• {w}</div>
              ))}
            </div>
          )}

          {/* Export Options */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                1. Export Official Census & Voter Data ({records.length} Citizens)
              </h4>
              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                Ready for National Archiving
              </span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                id="export-full-csv-btn"
                onClick={() => exportToCSV(records)}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-emerald-500 bg-slate-50/70 hover:bg-emerald-50/50 transition-all text-left group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900 text-xs sm:text-sm group-hover:text-emerald-900 flex items-center gap-1.5">
                      <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                      Full Census CSV
                    </span>
                    <Download className="w-4 h-4 text-slate-400 group-hover:text-emerald-600" />
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-2">
                    Complete demographic, administrative (Counties, Payams, Bomas), contact, ID/Passport & occupation data.
                  </p>
                </div>
              </button>

              <button
                type="button"
                id="export-voters-csv-btn"
                onClick={() => exportElectoralRollToCSV(records)}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-purple-500 bg-slate-50/70 hover:bg-purple-50/50 transition-all text-left group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900 text-xs sm:text-sm group-hover:text-purple-900 flex items-center gap-1.5">
                      <Vote className="w-4 h-4 text-purple-600" />
                      Electoral Roll CSV
                    </span>
                    <Download className="w-4 h-4 text-slate-400 group-hover:text-purple-600" />
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-2">
                    Eligible voters list (18+), polling stations, Voter Registration Numbers & voting verification.
                  </p>
                </div>
              </button>

              <button
                type="button"
                id="export-json-backup-btn"
                onClick={() => exportToJSON(records)}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-blue-500 bg-slate-50/70 hover:bg-blue-50/50 transition-all text-left group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900 text-xs sm:text-sm group-hover:text-blue-900 flex items-center gap-1.5">
                      <FileCode className="w-4 h-4 text-blue-600" />
                      JSON Archive
                    </span>
                    <Download className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-2">
                    Raw JSON database format for lossless backup and platform transfers.
                  </p>
                </div>
              </button>
            </div>
          </div>

          {/* Ingest / Import Section */}
          <div className="pt-4 border-t border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                2. Import & Ingest Population Records
              </h4>
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
                <button
                  type="button"
                  onClick={() => setImportMode('csv')}
                  className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                    importMode === 'csv' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  CSV File
                </button>
                <button
                  type="button"
                  onClick={() => setImportMode('json')}
                  className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                    importMode === 'json' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  JSON Backup
                </button>
              </div>
            </div>

            {importMode === 'csv' ? (
              <div className="space-y-3">
                <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-emerald-300 hover:border-emerald-500 rounded-xl bg-emerald-50/30 hover:bg-emerald-50/60 cursor-pointer transition-colors">
                  <Upload className="w-8 h-8 text-emerald-600 mb-2" />
                  <span className="text-xs font-bold text-slate-800">Upload CSV Census Spreadsheet</span>
                  <span className="text-[11px] text-slate-500 mt-0.5">
                    Supports columns for Name, Age, Gender, ID/Passport, Phone, County, Payam, Boma, Occupation
                  </span>
                  <input
                    type="file"
                    accept=".csv,text/csv"
                    onChange={handleCsvFileUpload}
                    className="hidden"
                  />
                </label>

                <div className="flex items-center justify-between bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="text-xs">
                    <span className="font-bold text-slate-800 block">Need the standard spreadsheet format?</span>
                    <span className="text-[11px] text-slate-500">Download pre-structured CSV template with sample data</span>
                  </div>
                  <button
                    type="button"
                    id="download-csv-template-btn"
                    onClick={downloadCensusCSVTemplate}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-emerald-800 bg-white border border-emerald-300 hover:bg-emerald-50 rounded-lg shadow-2xs transition-colors"
                  >
                    <FileDown className="w-3.5 h-3.5 text-emerald-600" />
                    Download CSV Template
                  </button>
                </div>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-blue-300 hover:border-blue-500 rounded-xl bg-blue-50/30 hover:bg-blue-50/60 cursor-pointer transition-colors">
                <Upload className="w-8 h-8 text-blue-600 mb-2" />
                <span className="text-xs font-bold text-slate-800">Upload JSON Database Backup</span>
                <span className="text-[11px] text-slate-500 mt-0.5">Restores exported CensusRecord JSON arrays</span>
                <input
                  type="file"
                  accept=".json,application/json"
                  onChange={handleJsonFileUpload}
                  className="hidden"
                />
              </label>
            )}
          </div>

          {/* Reset Action */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-800 block">Database Factory Reset</span>
              <span className="text-[11px] text-slate-500 block">Restore initial official national baseline (15 diverse profiles)</span>
            </div>
            <button
              type="button"
              id="reset-database-btn"
              onClick={handleReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-rose-700 hover:bg-rose-50 rounded-lg border border-rose-200 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Demo Data
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-1.5 text-slate-500 text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Encrypted local file handling — no data transmitted externally</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 rounded-xl shadow-2xs transition-colors"
          >
            Close Window
          </button>
        </div>
      </div>
    </div>
  );
};
