'use client';

import React, { useState, useEffect } from 'react';
import { AdministrativeUnit } from '@/lib/types';
import { COMMON_REGIONS } from '@/lib/initialData';
import { getStoredAdministrativeUnits } from '@/lib/administrativeData';
import { X, Save, MapPin, Building2, Layers, AlertCircle } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  unit: AdministrativeUnit | null;
  defaultType?: 'County' | 'Payam' | 'Boma';
  onSave: (unit: AdministrativeUnit) => void;
}

export const AdministrativeUnitModal: React.FC<Props> = ({
  isOpen,
  onClose,
  unit,
  defaultType = 'County',
  onSave
}) => {
  if (!isOpen) return null;

  return (
    <AdministrativeUnitModalContent
      key={unit ? unit.id : `new-${defaultType}`}
      isOpen={isOpen}
      onClose={onClose}
      unit={unit}
      defaultType={defaultType}
      onSave={onSave}
    />
  );
};

const AdministrativeUnitModalContent: React.FC<Props> = ({
  onClose,
  unit,
  defaultType = 'County',
  onSave
}) => {
  const [formData, setFormData] = useState<Partial<AdministrativeUnit>>(() => {
    if (unit) {
      return { ...unit };
    }
    return {
      type: defaultType,
      stateOrRegion: COMMON_REGIONS[0],
      code: `${defaultType.substring(0, 3).toUpperCase()}-${Math.floor(100 + Math.random() * 900)}`,
      estimatedTargetPopulation: defaultType === 'County' ? 250000 : defaultType === 'Payam' ? 80000 : 25000
    };
  });
  const [errorNotice, setErrorNotice] = useState<string | null>(null);

  const existingUnits = getStoredAdministrativeUnits();
  const availableStates = Array.from(new Set([...COMMON_REGIONS, ...existingUnits.filter(u => u.type === 'State').map(u => u.name)]));
  const availableCounties = existingUnits.filter(u => u.type === 'County');
  const availablePayams = existingUnits.filter(u => u.type === 'Payam');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name?.trim()) {
      setErrorNotice('Unit Name is required.');
      return;
    }

    const type = formData.type || 'County';
    const id = unit ? unit.id : `${type.toUpperCase()}-${Date.now().toString(36).toUpperCase()}`;

    const saved: AdministrativeUnit = {
      id,
      type,
      name: formData.name.trim(),
      code: formData.code?.trim() || `${type.toUpperCase()}-${Math.floor(100 + Math.random() * 900)}`,
      parentId: formData.parentId,
      parentName: formData.parentName,
      stateOrRegion: formData.stateOrRegion || 'Central Equatoria',
      countyOrPayam: formData.countyOrPayam,
      subCountyOrBoma: formData.subCountyOrBoma,
      administratorTitle: formData.administratorTitle || (type === 'County' ? 'County Commissioner' : type === 'Payam' ? 'Payam Executive Director' : 'Boma Chief'),
      administratorName: formData.administratorName?.trim(),
      headquarters: formData.headquarters?.trim(),
      estimatedTargetPopulation: typeof formData.estimatedTargetPopulation === 'number' ? formData.estimatedTargetPopulation : undefined,
      notes: formData.notes?.trim()
    };

    onSave(saved);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs overflow-y-auto">
      <div 
        id="admin-unit-modal"
        className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-sm tracking-wide uppercase">
              {unit ? `Edit ${unit.type}: ${unit.name}` : `Register New ${formData.type || 'Administrative Unit'}`}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs sm:text-sm">
          {errorNotice && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{errorNotice}</span>
            </div>
          )}

          {/* Unit Type Selection */}
          <div className="grid grid-cols-3 gap-2">
            {(['County', 'Payam', 'Boma'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, type: t }))}
                className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                  formData.type === t
                    ? 'bg-emerald-800 text-white border-emerald-800 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Unit Name */}
            <div>
              <label htmlFor="admin-unit-name" className="block font-semibold text-slate-700 mb-1">
                {formData.type} Official Name *
              </label>
              <input
                id="admin-unit-name"
                type="text"
                required
                value={formData.name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder={`e.g. ${formData.type === 'County' ? 'Juba County' : formData.type === 'Payam' ? 'Munuki Payam' : 'Munuki Block A'}`}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
              />
            </div>

            {/* Code */}
            <div>
              <label htmlFor="admin-unit-code" className="block font-semibold text-slate-700 mb-1">
                Administrative Code
              </label>
              <input
                id="admin-unit-code"
                type="text"
                value={formData.code || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value }))}
                placeholder="e.g. COU-101 or PAY-101-01"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 font-mono"
              />
            </div>

            {/* Parent State */}
            <div>
              <label htmlFor="admin-unit-state" className="block font-semibold text-slate-700 mb-1">
                Parent State / Region *
              </label>
              <select
                id="admin-unit-state"
                value={formData.stateOrRegion || availableStates[0]}
                onChange={(e) => setFormData(prev => ({ ...prev, stateOrRegion: e.target.value }))}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
              >
                {availableStates.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            {/* Parent County for Payams/Bomas */}
            {formData.type !== 'County' && (
              <div>
                <label htmlFor="admin-unit-parentcounty" className="block font-semibold text-slate-700 mb-1">
                  Parent County
                </label>
                <select
                  id="admin-unit-parentcounty"
                  value={formData.countyOrPayam || ''}
                  onChange={(e) => {
                    const c = availableCounties.find(u => u.name === e.target.value);
                    setFormData(prev => ({
                      ...prev,
                      countyOrPayam: e.target.value,
                      parentId: c?.id,
                      parentName: c?.name
                    }));
                  }}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                >
                  <option value="">-- Select Parent County --</option>
                  {availableCounties.map(c => (
                    <option key={c.id} value={c.name}>{c.name} ({c.stateOrRegion})</option>
                  ))}
                </select>
              </div>
            )}

            {/* Parent Payam for Bomas */}
            {formData.type === 'Boma' && (
              <div className="sm:col-span-2">
                <label htmlFor="admin-unit-parentpayam" className="block font-semibold text-slate-700 mb-1">
                  Parent Payam
                </label>
                <select
                  id="admin-unit-parentpayam"
                  value={formData.subCountyOrBoma || ''}
                  onChange={(e) => {
                    const p = availablePayams.find(u => u.name === e.target.value);
                    setFormData(prev => ({
                      ...prev,
                      subCountyOrBoma: e.target.value,
                      parentId: p?.id || prev.parentId,
                      parentName: p?.name || prev.parentName
                    }));
                  }}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900 bg-white"
                >
                  <option value="">-- Select Parent Payam --</option>
                  {availablePayams.map(p => (
                    <option key={p.id} value={p.name}>{p.name} ({p.countyOrPayam})</option>
                  ))}
                </select>
              </div>
            )}

            {/* Administrator Title */}
            <div>
              <label htmlFor="admin-unit-title" className="block font-semibold text-slate-700 mb-1">
                Administrator Title
              </label>
              <input
                id="admin-unit-title"
                type="text"
                value={formData.administratorTitle || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, administratorTitle: e.target.value }))}
                placeholder={formData.type === 'County' ? 'County Commissioner' : formData.type === 'Payam' ? 'Payam Executive Director' : 'Boma Chief'}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
              />
            </div>

            {/* Administrator Name */}
            <div>
              <label htmlFor="admin-unit-adminname" className="block font-semibold text-slate-700 mb-1">
                Official Administrator / Leader Name
              </label>
              <input
                id="admin-unit-adminname"
                type="text"
                value={formData.administratorName || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, administratorName: e.target.value }))}
                placeholder="e.g. Hon. Charles Joseph Wani / Chief Simon Lado"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
              />
            </div>

            {/* Headquarters */}
            <div>
              <label htmlFor="admin-unit-hq" className="block font-semibold text-slate-700 mb-1">
                Administrative Headquarters / Office
              </label>
              <input
                id="admin-unit-hq"
                type="text"
                value={formData.headquarters || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, headquarters: e.target.value }))}
                placeholder="e.g. Juba Civic Complex, Munuki Hall"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
              />
            </div>

            {/* Estimated Target Population */}
            <div>
              <label htmlFor="admin-unit-targetpop" className="block font-semibold text-slate-700 mb-1">
                Projected Target Population
              </label>
              <input
                id="admin-unit-targetpop"
                type="number"
                min="0"
                value={formData.estimatedTargetPopulation ?? ''}
                onChange={(e) => setFormData(prev => ({ ...prev, estimatedTargetPopulation: parseInt(e.target.value, 10) || 0 }))}
                placeholder="e.g. 250000"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="admin-unit-notes" className="block font-semibold text-slate-700 mb-1">
              Geographic & Demographic Notes
            </label>
            <textarea
              id="admin-unit-notes"
              rows={2}
              value={formData.notes || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="Key boundary descriptions, major economic activities, seasonal settlement patterns..."
              className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-600 text-slate-900"
            />
          </div>

          {/* Buttons */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-5 py-2 text-xs font-bold text-white bg-emerald-800 hover:bg-emerald-900 rounded-xl shadow-xs transition-all"
            >
              <Save className="w-4 h-4" />
              {unit ? 'Update Unit' : `Create ${formData.type}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
