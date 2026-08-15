import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  UploadCloud, 
  Clock, 
  ShieldAlert, 
  AlertCircle, 
  Sparkles,
  ChevronRight,
  Layers,
  Loader2
} from 'lucide-react';
import { 
  fetchValidationReport, 
  triggerPublish, 
  fetchPublishRuns, 
  ValidationReport, 
  PublishRun 
} from '../api/client';

interface PublishPipelineProps {
  role: 'editor' | 'admin';
}

export const PublishPipeline: React.FC<PublishPipelineProps> = ({ role }) => {
  const queryClient = useQueryClient();
  const [publishFeedback, setPublishFeedback] = useState<{ status: 'success' | 'error'; message: string } | null>(null);

  const {
    data: report,
    isLoading: reportLoading,
    refetch: refetchReport,
  } = useQuery({
    queryKey: ['validation-report'],
    queryFn: fetchValidationReport,
  });

  const {
    data: publishRuns = [],
    isLoading: runsLoading,
    refetch: refetchRuns,
  } = useQuery({
    queryKey: ['publish-runs'],
    queryFn: fetchPublishRuns,
  });

  const publishMutation = useMutation({
    mutationFn: triggerPublish,
    onSuccess: (data) => {
      setPublishFeedback({
        status: 'success',
        message: `Catalogue Version ${data.catalogue_version} published atomically! (${data.shows_count} shows, ${data.episodes_count} episodes)`,
      });
      queryClient.invalidateQueries({ queryKey: ['publish-runs'] });
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : (detail?.error || 'Publishing failed.');
      setPublishFeedback({ status: 'error', message: msg });
    },
  });

  const handlePublishClick = () => {
    setPublishFeedback(null);
    publishMutation.mutate();
  };

  const isPublishDisabled = !report?.can_publish || role !== 'admin' || publishMutation.isPending;

  const getDisabledReason = () => {
    if (publishMutation.isPending) return 'Publishing in progress...';
    if (role !== 'admin') return 'Publishing is restricted to Admin role (Switch in Navbar)';
    if (!report?.can_publish) return `Blocked by ${report?.total_blockers} validation blocker(s)`;
    return '';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Catalogue Publish Pipeline</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Pre-flight data validation, atomic JSON serialization, and version history
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              refetchReport();
              refetchRuns();
            }}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Re-scan
          </button>

          <button
            onClick={handlePublishClick}
            disabled={isPublishDisabled}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold shadow-lg transition ${
              !isPublishDisabled
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-indigo-500/25 cursor-pointer'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
            }`}
          >
            {publishMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <UploadCloud className="w-4 h-4" />
            )}
            Publish Catalogue
          </button>
        </div>
      </div>

      {/* Disabled Reason Banner */}
      {isPublishDisabled && getDisabledReason() && (
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span><strong>Publishing Status:</strong> {getDisabledReason()}</span>
          </div>
          {role !== 'admin' && (
            <span className="text-[10px] text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
              Admin Required
            </span>
          )}
        </div>
      )}

      {/* Action Feedback Banner */}
      {publishFeedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-start gap-3 ${
            publishFeedback.status === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-red-950/40 border-red-500/40 text-red-200'
          }`}
        >
          {publishFeedback.status === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          )}
          <div>
            <h4 className="font-bold text-sm">
              {publishFeedback.status === 'success' ? 'Publish Success' : 'Publish Error'}
            </h4>
            <p className="mt-0.5 leading-relaxed">{publishFeedback.message}</p>
          </div>
        </div>
      )}

      {/* Pre-flight Validation Report Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div
              className={`p-2.5 rounded-xl ${
                report?.can_publish
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-950 text-amber-400 border border-amber-500/30'
              }`}
            >
              {report?.can_publish ? (
                <CheckCircle2 className="w-6 h-6" />
              ) : (
                <AlertTriangle className="w-6 h-6" />
              )}
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Pre-Flight Validation Report</h3>
              <p className="text-xs text-slate-400">
                {reportLoading ? 'Analyzing catalogue integrity...' : report?.summary}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs px-3 py-1 rounded-full font-semibold bg-red-950/60 text-red-400 border border-red-500/30">
              {report?.total_blockers || 0} Blockers
            </span>
            <span className="text-xs px-3 py-1 rounded-full font-semibold bg-amber-950/60 text-amber-400 border border-amber-500/30">
              {report?.total_warnings || 0} Warnings
            </span>
          </div>
        </div>

        {/* Grouped Issues */}
        {reportLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Scanning catalogue...</div>
        ) : report?.issues.length === 0 ? (
          <div className="p-8 bg-slate-950/60 rounded-xl text-center text-emerald-400 text-xs flex items-center justify-center gap-2">
            <CheckCircle2 className="w-4 h-4" /> All checks passed! No blockers detected.
          </div>
        ) : (
          <div className="space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Detected Issues Grouped by Show
            </h4>
            
            <div className="grid grid-cols-1 gap-3">
              {Object.entries(report?.grouped_by_show || {}).map(([showName, issues]) => (
                <div
                  key={showName}
                  className="bg-slate-950 rounded-xl p-4 border border-slate-800 space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-white flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      {showName}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {issues.length} issue(s)
                    </span>
                  </div>

                  <div className="space-y-2">
                    {issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg border text-xs space-y-1 ${
                          issue.severity === 'blocker'
                            ? 'bg-red-950/20 border-red-500/30 text-red-300'
                            : 'bg-amber-950/20 border-amber-500/30 text-amber-300'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold flex items-center gap-1.5">
                            <span className="px-1.5 py-0.2 text-[9px] rounded font-mono uppercase bg-slate-900 border border-slate-700">
                              {issue.code}
                            </span>
                            {issue.message}
                          </span>
                          <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-slate-900">
                            {issue.severity}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 pl-2 border-l-2 border-slate-700">
                          <strong>Fix Suggestion:</strong> {issue.fix_suggestion}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Publish Run History */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-lg font-bold text-white">Publish Run History</h3>
        
        {runsLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading publish logs...</div>
        ) : publishRuns.length === 0 ? (
          <div className="p-8 bg-slate-950/60 rounded-xl text-center text-slate-500 text-xs">
            No publish runs recorded yet. Click 'Publish Catalogue' above to create the first version.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="pb-3">Version</th>
                  <th className="pb-3">Published At</th>
                  <th className="pb-3">Published By</th>
                  <th className="pb-3">Shows / Episodes</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {publishRuns.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-800/30">
                    <td className="py-3 font-bold text-indigo-400">v{run.catalogue_version}</td>
                    <td className="py-3 text-slate-300">{new Date(run.published_at).toLocaleString()}</td>
                    <td className="py-3 text-slate-400">{run.published_by}</td>
                    <td className="py-3 text-slate-300">{run.shows_count} shows · {run.episodes_count} eps</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                        {run.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
