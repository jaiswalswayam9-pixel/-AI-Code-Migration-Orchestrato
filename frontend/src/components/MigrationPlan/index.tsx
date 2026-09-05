import React, { useEffect, useState } from 'react';
import { migrationApi } from '../../services/migrationApi';
import type { MigrationPlanStep } from '../../types/migration';

interface MigrationPlanProps {
  migrationId: string;
}

export default function MigrationPlan({ migrationId }: MigrationPlanProps) {
  const [plan, setPlan] = useState<MigrationPlanStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    migrationApi.plan(migrationId)
      .then(res => setPlan(res.plan))
      .catch(err => setError(err.message || 'Failed to load plan'))
      .finally(() => setLoading(false));
  }, [migrationId]);

  if (loading) return <div className="text-gray-500 p-4">Loading plan...</div>;
  if (error) return <div className="text-red-500 p-4">Error: {error}</div>;
  if (plan.length === 0) return <div className="text-gray-500 p-4">No plan available yet.</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h3 className="text-xl font-bold mb-6 text-gray-900">Migration Plan</h3>
      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-200 before:to-transparent">
        {plan.map((step, index) => (
          <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-blue-100 text-blue-600 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
              {step.step_number}
            </div>
            <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-gray-50 p-4 rounded border border-gray-200">
              <div className="font-bold text-gray-800">{step.name}</div>
              <div className="text-sm text-gray-600 mt-1">{step.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
