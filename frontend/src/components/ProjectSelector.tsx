import { useEffect, useState } from 'react';
import api from '../api/client';

interface Project {
  id: string;
  name: string;
  description: string;
}

interface ProjectSelectorProps {
  value?: string;
  onChange: (projectId: string | null) => void;
  placeholder?: string;
  allowAll?: boolean;
}

export const ProjectSelector = ({
  value,
  onChange,
  placeholder = 'Select a project',
  allowAll = true,
}: ProjectSelectorProps) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (err: any) {
      console.error('Error loading projects:', err);
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    onChange(selectedValue === '' ? null : selectedValue);
  };

  if (loading) {
    return (
      <select className="form-select" disabled>
        <option>Loading projects...</option>
      </select>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
        <button
          className="btn btn-sm btn-link"
          onClick={loadProjects}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <select
      className="form-select"
      value={value || ''}
      onChange={handleChange}
    >
      {allowAll && <option value="">All Projects</option>}
      {!allowAll && <option value="">{placeholder}</option>}
      {projects.map((project) => (
        <option key={project.id} value={project.id}>
          {project.name}
        </option>
      ))}
    </select>
  );
};
