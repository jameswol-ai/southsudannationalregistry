'use client';

import React, { useMemo } from 'react';
import { CensusRecord } from '@/lib/types';
import { 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';
import { 
  Users, 
  Building2, 
  MapPin, 
  Sparkles, 
  GraduationCap, 
  Briefcase, 
  TrendingUp, 
  PieChart as PieIcon, 
  Layers 
} from 'lucide-react';

interface Props {
  records: CensusRecord[];
}

const COLORS = [
  '#0f766e', // teal-700
  '#0284c7', // sky-600
  '#8b5cf6', // violet-500
  '#f59e0b', // amber-500
  '#ec4899', // pink-500
  '#10b981', // emerald-500
  '#6366f1', // indigo-500
  '#f97316', // orange-500
  '#64748b', // slate-500
  '#14b8a6', // teal-500
];

export const DemographicAnalytics: React.FC<Props> = ({ records }) => {
  // 1. Core Summary Metrics
  const metrics = useMemo(() => {
    const totalCount = records.length;
    const households = new Set(records.map(r => r.householdId).filter(Boolean));
    const maleCount = records.filter(r => r.gender === 'Male').length;
    const femaleCount = records.filter(r => r.gender === 'Female').length;
    const otherCount = records.filter(r => r.gender === 'Other').length;
    const literateCount = records.filter(r => r.isLiterate).length;

    const totalAge = records.reduce((sum, r) => sum + r.age, 0);
    const avgAge = totalCount > 0 ? (totalAge / totalCount).toFixed(1) : '0';
    const literacyRate = totalCount > 0 ? Math.round((literateCount / totalCount) * 100) : 0;

    const uniqueTribes = new Set(records.map(r => r.tribe).filter(Boolean));
    const uniqueCommunities = new Set(records.map(r => r.community).filter(Boolean));

    return {
      totalCount,
      totalHouseholds: households.size,
      maleCount,
      femaleCount,
      otherCount,
      avgAge,
      literacyRate,
      tribesCount: uniqueTribes.size,
      communitiesCount: uniqueCommunities.size
    };
  }, [records]);

  // 2. Tribe Distribution Data
  const tribeData = useMemo(() => {
    const counts: { [key: string]: number } = {};
    records.forEach(r => {
      const t = r.tribe || 'Unspecified';
      counts[t] = (counts[t] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([name, count]) => ({
        name,
        count,
        percentage: ((count / (records.length || 1)) * 100).toFixed(1)
      }))
      .sort((a, b) => b.count - a.count);
  }, [records]);

  // 3. Community Distribution Data
  const communityData = useMemo(() => {
    const counts: { [key: string]: number } = {};
    records.forEach(r => {
      const c = r.community || 'Unspecified';
      counts[c] = (counts[c] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([name, count]) => ({
        name,
        count,
        percentage: ((count / (records.length || 1)) * 100).toFixed(1)
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8); // Top 8 communities
  }, [records]);

  // 4. Age Bracket Cohorts
  const ageCohortData = useMemo(() => {
    let child = 0; // 0-14
    let youth = 0; // 15-24
    let adult = 0; // 25-54
    let senior = 0; // 55+

    records.forEach(r => {
      if (r.age <= 14) child++;
      else if (r.age <= 24) youth++;
      else if (r.age <= 54) adult++;
      else senior++;
    });

    const total = records.length || 1;

    return [
      { name: 'Children (0-14)', count: child, percentage: ((child / total) * 100).toFixed(1) },
      { name: 'Youth (15-24)', count: youth, percentage: ((youth / total) * 100).toFixed(1) },
      { name: 'Adults (25-54)', count: adult, percentage: ((adult / total) * 100).toFixed(1) },
      { name: 'Elders (55+)', count: senior, percentage: ((senior / total) * 100).toFixed(1) },
    ];
  }, [records]);

  // 5. Gender Data for Pie
  const genderPieData = useMemo(() => {
    return [
      { name: 'Male', value: metrics.maleCount, color: '#0284c7' },
      { name: 'Female', value: metrics.femaleCount, color: '#ec4899' },
      ...(metrics.otherCount > 0 ? [{ name: 'Other', value: metrics.otherCount, color: '#8b5cf6' }] : [])
    ];
  }, [metrics]);

  // 6. Education Levels Data
  const educationData = useMemo(() => {
    const counts: { [key: string]: number } = {};
    records.forEach(r => {
      const ed = r.educationLevel || 'None / Informal';
      // Shorten label for chart
      const label = ed.replace(' (Grades 1-8)', '').replace(' (Grades 9-12)', '').replace(' (Master/PhD)', '');
      counts[label] = (counts[label] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
  }, [records]);

  // 7. Employment Sector Data
  const employmentData = useMemo(() => {
    const counts: { [key: string]: number } = {};
    records.forEach(r => {
      const emp = r.employmentStatus || 'Unspecified';
      counts[emp] = (counts[emp] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);
  }, [records]);

  return (
    <div className="space-y-6">
      {/* Top Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        {/* Total Population */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Enumerated</span>
            <Users className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.totalCount.toLocaleString()}</div>
          <div className="text-[11px] text-emerald-700 font-medium mt-1">
            Registered Individuals
          </div>
        </div>

        {/* Households */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Households</span>
            <Building2 className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.totalHouseholds}</div>
          <div className="text-[11px] text-purple-700 font-medium mt-1">
            Avg {(metrics.totalCount / (metrics.totalHouseholds || 1)).toFixed(1)} persons/HH
          </div>
        </div>

        {/* Gender Balance */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Gender Balance</span>
            <TrendingUp className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {metrics.femaleCount > 0 ? (metrics.maleCount / metrics.femaleCount).toFixed(2) : metrics.maleCount}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            {metrics.maleCount}M / {metrics.femaleCount}F
          </div>
        </div>

        {/* Average Age */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Median / Avg Age</span>
            <Layers className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.avgAge} <span className="text-xs font-normal text-slate-500">yrs</span></div>
          <div className="text-[11px] text-amber-700 font-medium mt-1">
            Young demographic
          </div>
        </div>

        {/* Literacy Rate */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Literacy Rate</span>
            <GraduationCap className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.literacyRate}%</div>
          <div className="text-[11px] text-emerald-700 font-medium mt-1">
            Can read & write
          </div>
        </div>

        {/* Cultural Diversity */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Tribes & Comm.</span>
            <Sparkles className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.tribesCount} <span className="text-xs font-normal text-slate-500">tribes</span></div>
          <div className="text-[11px] text-rose-700 font-medium mt-1">
            Across {metrics.communitiesCount} settlements
          </div>
        </div>
      </div>

      {/* Main Charts Row 1: Tribe Distribution + Community Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tribe / Ethnic Group Breakdown */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                Ethnic & Tribe Representation
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Proportion of population categorized by native tribal affiliation
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded">
              {metrics.tribesCount} Ethnic Groups
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={tribeData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  tick={{ fontSize: 11, fill: '#1e293b' }} 
                  width={110}
                />
                <Tooltip 
                  formatter={(value: any, name: any, item: any) => [`${value} persons (${item.payload.percentage}%)`, 'Count']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {tribeData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Community & Settlement Breakdown */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                Community & Village Settlements
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Top geographic settlements by enumerated population volume
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded">
              {metrics.communitiesCount} Localities
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={communityData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  tick={{ fontSize: 11, fill: '#1e293b' }} 
                  width={130}
                />
                <Tooltip 
                  formatter={(value: any, name: any, item: any) => [`${value} residents (${item.payload.percentage}%)`, 'Residents']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#0284c7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Age Cohorts & Gender Ratios */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Age Structure Pyramid */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2">
                <Users className="w-4 h-4 text-purple-600" />
                Age Structure & Cohort Breakdown
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Demographic age distribution across life stages
              </p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ageCohortData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#1e293b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip 
                  formatter={(value: any, name: any, item: any) => [`${value} persons (${item.payload.percentage}%)`, 'Population']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]}>
                  {ageCohortData.map((_, index) => (
                    <Cell key={`age-${index}`} fill={['#38bdf8', '#818cf8', '#a855f7', '#f43f5e'][index % 4]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gender Breakdown Donut */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2 pb-4 mb-4 border-b border-slate-100">
              <PieIcon className="w-4 h-4 text-pink-600" />
              Sex & Gender Composition
            </h3>
            
            <div className="h-48 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={genderPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {genderPieData.map((entry, index) => (
                      <Cell key={`gender-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: any, name: any) => [`${value} (${((Number(value) / (records.length || 1)) * 100).toFixed(1)}%)`, name]}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs pt-3 border-t border-slate-100">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-sky-600"></span>
              <span className="text-slate-600 font-medium">Male: {metrics.maleCount} ({((metrics.maleCount / (metrics.totalCount || 1)) * 100).toFixed(1)}%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-pink-500"></span>
              <span className="text-slate-600 font-medium">Female: {metrics.femaleCount} ({((metrics.femaleCount / (metrics.totalCount || 1)) * 100).toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Education & Livelihood Sectors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Education Level */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-emerald-600" />
                Educational Attainment
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Highest formal level completed by population members
              </p>
            </div>
            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded">
              {metrics.literacyRate}% Literate
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={educationData} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis 
                  dataKey="name" 
                  angle={-15} 
                  textAnchor="end" 
                  tick={{ fontSize: 10, fill: '#1e293b' }} 
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip 
                  formatter={(value: any) => [`${value} individuals`, 'Total']}
                  contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#0f766e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Livelihoods & Employment */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm tracking-tight uppercase flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-amber-600" />
                Primary Economic Sectors
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Distribution of occupations, farming, pastoralism & commerce
              </p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={employmentData} margin={{ top: 10, right: 20, left: 0, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis 
                  dataKey="name" 
                  angle={-15} 
                  textAnchor="end" 
                  tick={{ fontSize: 10, fill: '#1e293b' }} 
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip 
                  formatter={(value: any) => [`${value} individuals`, 'Total']}
                  contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
