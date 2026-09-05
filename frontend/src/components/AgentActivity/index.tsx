import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';

interface AgentActivityProps {
  migrationId: string;
}

export default function AgentActivity({ migrationId }: AgentActivityProps) {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    migrationApi.agents(migrationId)
      .then(res => setEvents(res.events || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="p-4 text-gray-500">Loading activity...</div>;
  if (events.length === 0) return <div className="p-4 text-gray-500">No agent activity logged.</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200 max-h-96 overflow-y-auto">
      <h3 className="text-xl font-bold mb-4 text-gray-900">Agent Activity Timeline</h3>
      <div className="space-y-4">
        {events.map((evt, idx) => (
          <div key={idx} className="flex gap-4 p-3 border-l-4 border-blue-500 bg-gray-50 rounded">
            <div className="text-xs text-gray-500 whitespace-nowrap pt-1">
              {new Date(evt.timestamp || Date.now()).toLocaleTimeString()}
            </div>
            <div>
              <div className="font-semibold text-sm text-gray-800">{evt.agent_name || 'System Agent'}</div>
              <div className="text-sm text-gray-700 mt-1">{evt.message || evt.action}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
