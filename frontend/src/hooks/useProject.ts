import { useEffect, useState } from "react";
import { projectApi } from "../services/projectApi";
import type { Project } from "../types/project";

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    setLoading(true);
    projectApi
      .list()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(refresh, []);

  return { projects, loading, error, refresh };
}
