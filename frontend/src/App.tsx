import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import UploadProject from "./pages/UploadProject";
import ProjectDetails from "./pages/ProjectDetails";
import Migration from "./pages/Migration";
import Results from "./pages/Results";
import Report from "./pages/Report";

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b border-gray-200 px-8 py-4 shadow-sm">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <Link to="/" className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <span className="text-2xl">🔄</span>
              AI Code Migration Orchestrator
            </Link>
            <div className="flex items-center gap-6">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `text-sm font-medium transition ${isActive ? "text-blue-600" : "text-gray-600 hover:text-gray-900"}`
                }
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/upload"
                className={({ isActive }) =>
                  `text-sm font-medium transition ${isActive ? "text-blue-600" : "text-gray-600 hover:text-gray-900"}`
                }
              >
                Upload Project
              </NavLink>
            </div>
          </div>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadProject />} />
            <Route path="/projects/:projectId" element={<ProjectDetails />} />
            <Route path="/migrations/:migrationId" element={<Migration />} />
            <Route path="/results/:migrationId" element={<Results />} />
            <Route path="/report/:migrationId" element={<Report />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
