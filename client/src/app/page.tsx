'use client';

import { useEffect, useState } from 'react';
import { getFullAnalysis } from '../../lib/api';
import { Shield, AlertTriangle, CheckCircle, Clock, Users, FileText, Activity } from 'lucide-react';

interface Bidder {
  id: string;
  name: string;
  status: 'eligible' | 'ineligible' | 'manual_review';
  turnover: number | null;
  ocr_confidence: number;
  collusion_risk?: number;
  risk_level?: string;
  flags?: string[];
  rejection_reason?: string;
  review_reason?: string;
}

interface StarGraph {
  director: string;
  controlled_count: number;
  bidders: string[];
}

interface BidCluster {
  bidder_1: string;
  bidder_2: string;
  amount_1: number;
  amount_2: number;
  percent_difference: number;
  severity: string;
}

interface BenfordResult {
  total_bids: number;
  chi_square_statistic: number;
  is_suspicious: boolean;
  interpretation: string;
}

interface AnalysisData {
  tender: {
    bidders: Bidder[];
  };
  summary: {
    total_bidders: number;
    eligible: number;
    ineligible: number;
    manual_review: number;
    collusion_flags: number;
    risk_level: string;
  };
  detections: {
    star_graphs: StarGraph[];
    bid_clustering: BidCluster[];
    benfords_law: BenfordResult;
  };
}

export default function Dashboard() {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFullAnalysis().then((res: { data: AnalysisData }) => {
      setData(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-xl font-semibold text-gray-700">Loading BidShield...</div>
    </div>
  );
  
  if (!data) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-xl text-red-600">Error loading data</div>
    </div>
  );

  const { tender, summary, detections } = data;

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'eligible': return 'bg-emerald-100 text-emerald-900 border-emerald-300 font-semibold';
      case 'ineligible': return 'bg-rose-100 text-rose-900 border-rose-300 font-semibold';
      case 'manual_review': return 'bg-amber-100 text-amber-900 border-amber-300 font-semibold';
      default: return 'bg-gray-100 text-gray-900 border-gray-300';
    }
  };

  const getRiskBadge = (risk?: number) => {
    if (!risk) return <span className="text-gray-400 text-sm">—</span>;
    if (risk >= 70) return <span className="px-2 py-1 bg-rose-600 text-white rounded text-xs font-bold">RISK {risk}</span>;
    if (risk >= 40) return <span className="px-2 py-1 bg-orange-500 text-white rounded text-xs font-bold">RISK {risk}</span>;
    return <span className="px-2 py-1 bg-emerald-500 text-white rounded text-xs font-bold">RISK {risk}</span>;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-slate-900 text-white p-6">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <Shield className="w-10 h-10 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold tracking-tight">BidShield</h1>
            <p className="text-slate-400 text-sm">Government Procurement Fraud Detection</p>
          </div>
          <div className="ml-auto">
            <span className={`px-4 py-2 rounded-full text-sm font-bold ${
              summary.risk_level === 'HIGH' ? 'bg-red-500 text-white' : 'bg-emerald-500 text-white'
            }`}>
              {summary.risk_level} RISK
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-5 gap-4">
          <SummaryCard icon={<Users className="w-5 h-5"/>} label="Total Bidders" value={summary.total_bidders} color="blue" />
          <SummaryCard icon={<CheckCircle className="w-5 h-5"/>} label="Eligible" value={summary.eligible} color="green" />
          <SummaryCard icon={<AlertTriangle className="w-5 h-5"/>} label="Ineligible" value={summary.ineligible} color="red" />
          <SummaryCard icon={<Clock className="w-5 h-5"/>} label="Manual Review" value={summary.manual_review} color="yellow" />
          <SummaryCard icon={<Activity className="w-5 h-5"/>} label="Collusion Flags" value={summary.collusion_flags} color="purple" />
        </div>

        {/* Bidders Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-200 flex items-center gap-3">
            <FileText className="w-5 h-5 text-slate-600" />
            <h2 className="text-lg font-bold text-gray-900">Bidder Evaluation Results</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">ID</th>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">Company Name</th>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">Status</th>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">Turnover</th>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">OCR Confidence</th>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">Risk Score</th>
                  <th className="px-5 py-3 text-xs font-bold text-gray-600 uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {tender.bidders.map((bidder) => (
                  <tr key={bidder.id} className={bidder.collusion_risk ? 'bg-red-50/50' : 'hover:bg-gray-50'}>
                    <td className="px-5 py-4 font-mono text-sm text-gray-700">{bidder.id}</td>
                    <td className="px-5 py-4 font-semibold text-gray-900">{bidder.name}</td>
                    <td className="px-5 py-4">
                      <span className={`px-3 py-1 rounded-md text-xs border ${getStatusStyle(bidder.status)}`}>
                        {bidder.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-700 font-medium">
                      {bidder.turnover ? `₹${(bidder.turnover / 10000000).toFixed(1)}cr` : <span className="text-gray-400">—</span>}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-20 h-2.5 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              bidder.ocr_confidence > 0.9 ? 'bg-emerald-500' : 
                              bidder.ocr_confidence > 0.7 ? 'bg-amber-500' : 'bg-rose-500'
                            }`}
                            style={{ width: `${bidder.ocr_confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-700">{(bidder.ocr_confidence * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-5 py-4">{getRiskBadge(bidder.collusion_risk)}</td>
                    <td className="px-5 py-4 text-sm text-gray-600 max-w-xs">
                      {bidder.rejection_reason || bidder.review_reason || bidder.flags?.join(', ') || <span className="text-gray-400">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Fraud Detections Grid */}
        <div className="grid grid-cols-2 gap-6">
          {/* Star Graph Detection */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-600" />
              Star Graph Detections
            </h3>
            {detections.star_graphs.length > 0 ? (
              <div className="space-y-3">
                {detections.star_graphs.map((sg, i) => (
                  <div key={i} className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <p className="font-bold text-purple-900 text-sm">{sg.director}</p>
                    <p className="text-sm text-purple-700 mt-1">
                      Controls <span className="font-bold">{sg.controlled_count}</span> bidders: {sg.bidders.join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No star graph patterns detected</p>
            )}
          </div>

          {/* Bid Clustering */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
              Bid Clustering Alerts
            </h3>
            {detections.bid_clustering.length > 0 ? (
              <div className="space-y-3">
                {detections.bid_clustering.map((bc, i) => (
                  <div key={i} className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-bold text-orange-900 text-sm">{bc.bidder_1} ↔ {bc.bidder_2}</p>
                        <p className="text-sm text-orange-700 mt-1">
                          ₹{(bc.amount_1 / 10000000).toFixed(2)}cr vs ₹{(bc.amount_2 / 10000000).toFixed(2)}cr
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        bc.severity === 'HIGH' ? 'bg-red-200 text-red-900' : 'bg-orange-200 text-orange-900'
                      }`}>
                        {bc.severity}
                      </span>
                    </div>
                    <p className="text-xs text-orange-700 font-medium">Difference: {bc.percent_difference.toFixed(4)}%</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No bid clustering detected</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function SummaryCard({ icon, label, value, color }: { icon: React.ReactNode, label: string, value: number, color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-800 border-blue-200',
    green: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    red: 'bg-rose-50 text-rose-800 border-rose-200',
    yellow: 'bg-amber-50 text-amber-800 border-amber-200',
    purple: 'bg-purple-50 text-purple-800 border-purple-200',
  };

  return (
    <div className={`p-5 rounded-xl border ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-3 opacity-80">{icon}<span className="text-sm font-semibold">{label}</span></div>
      <div className="text-4xl font-bold">{value}</div>
    </div>
  );
}