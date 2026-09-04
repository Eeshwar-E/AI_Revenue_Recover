export function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    RECOVERED: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    ACTIVE: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    DETECTED: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    ESCALATED: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    STOPPED: 'bg-red-500/20 text-red-500/30 border-red-500/30',
    FAILED: 'bg-red-500/20 text-red-500/30 border-red-500/30',
    MANUAL_REVIEW: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    RETRY_PENDING: 'bg-cyan-500/20 text-cyan-400 border-cyan-400/30',
    ACTION_EXECUTED: 'bg-indigo-500/20 text-indigo-400 border-indigo-400/30',
    DIAGNOSING: 'bg-blue-500/20 text-blue-400 border-blue-400/30',
    STRATEGY_SELECTED: 'bg-indigo-500/20 text-indigo-400 border-indigo-400/30',
    POLICY_CHECK: 'bg-amber-500/20 text-amber-400 border-amber-400/30',
    ACTION_PENDING: 'bg-cyan-500/20 text-cyan-400 border-cyan-400/30',
    VERIFYING: 'bg-teal-500/20 text-teal-400 border-teal-400/30',
  };
  return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
}