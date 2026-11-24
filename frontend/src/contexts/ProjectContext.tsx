import React, { createContext, useContext, useState, useEffect } from 'react';
import { Project, Document } from '../types';
import { projectsApi, documentsApi } from '../services/api';
import { useAuth } from './AuthContext';

interface ProjectContextType {
  projects: Project[];
  activeProject: Project | null;
  documents: Document[];
  loadingProjects: boolean;
  loadingDocs: boolean;
  selectProject: (project: Project) => void;
  refreshProjects: () => Promise<void>;
  refreshDocuments: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const refreshProjects = async () => {
    if (!user) return;
    try {
      setLoadingProjects(true);
      const data = await projectsApi.list();
      setProjects(data);
      if (data.length > 0 && !activeProject) {
        setActiveProject(data[0]);
      } else if (activeProject) {
        const updated = data.find((p) => p.id === activeProject.id);
        if (updated) setActiveProject(updated);
      }
    } catch (err) {
      console.error('Failed to load projects', err);
    } finally {
      setLoadingProjects(false);
    }
  };

  const refreshDocuments = async () => {
    if (!activeProject) {
      setDocuments([]);
      return;
    }
    try {
      setLoadingDocs(true);
      const data = await documentsApi.listByProject(activeProject.id);
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents', err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    if (user) {
      refreshProjects();
    } else {
      setProjects([]);
      setActiveProject(null);
      setDocuments([]);
    }
  }, [user]);

  useEffect(() => {
    if (activeProject) {
      refreshDocuments();
    }
  }, [activeProject?.id]);

  const selectProject = (project: Project) => {
    setActiveProject(project);
  };

  return (
    <ProjectContext.Provider
      value={{
        projects,
        activeProject,
        documents,
        loadingProjects,
        loadingDocs,
        selectProject,
        refreshProjects,
        refreshDocuments,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};
