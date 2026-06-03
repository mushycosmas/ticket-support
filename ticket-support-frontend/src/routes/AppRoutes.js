import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";
import ProtectedRoute from "./ProtectedRoute";

// Auth
import Login from "../pages/Login";

// Dashboard
import Dashboard from "../pages/Dashboard";

// Tickets
import Tickets from "../pages/tickets/Tickets";
import TicketDetails from "../pages/tickets/TicketDetails";

// Admin
import Users from "../pages/admin/Users";
import Teams from "../pages/admin/Teams";
import Categories from "../pages/admin/Categories";
import Priorities from "../pages/admin/Priorities";
import KnowledgeBase from "../pages/admin/KnowledgeBase";

// Team Lead
import TeamTickets from "../pages/team/TeamTickets";
import TeamAgents from "../pages/team/TeamAgents";

// Reports
import Reports from "../pages/reports/Reports";
import Analytics from "../pages/reports/Analytics";

// System
import Settings from "../pages/system/Settings";
import SystemLogs from "../pages/system/SystemLogs";

//locations
import Regions from "../pages/admin/locations/Regions";
import Districts from "../pages/admin/locations/Districts";
import Wards from "../pages/admin/locations/Wards";

function AppRoutes() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* Protected Routes */}
                <Route
                    element={
                        <ProtectedRoute>
                            <MainLayout />
                        </ProtectedRoute>
                    }
                >
                    {/* Dashboard */}
                    <Route path="/dashboard" element={<Dashboard />} />

                    {/* Tickets */}
                    <Route path="/tickets" element={<Tickets />} />
                    <Route path="/tickets/my" element={<Tickets />} />
                    <Route path="/tickets/assigned" element={<Tickets />} />
                    <Route path="/tickets/unassigned" element={<Tickets />} />
                    <Route path="/tickets/open" element={<Tickets />} />
                    <Route path="/tickets/in-progress" element={<Tickets />} />
                    <Route path="/tickets/resolved" element={<Tickets />} />
                    <Route path="/tickets/closed" element={<Tickets />} />

                    {/* Team Lead */}
                    <Route path="/team/tickets" element={<TeamTickets />} />
                    <Route path="/team/agents" element={<TeamAgents />} />

                    {/* Administration */}
                    <Route path="/admin/users" element={<Users />} />
                    <Route path="/admin/teams" element={<Teams />} />
                    <Route path="/admin/categories" element={<Categories />} />
                    <Route path="/admin/priorities" element={<Priorities />} />

                    {/* Locations */}
                    <Route path="/admin/locations/regions" element={<Regions />} />
                    <Route path="/admin/locations/districts" element={<Districts />} />
                    <Route path="/admin/locations/wards" element={<Wards />} />
                    <Route
                        path="/admin/knowledge-base"
                        element={<KnowledgeBase />}
                    />

                    {/* Reports */}
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/analytics" element={<Analytics />} />

                    {/* System */}
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/logs" element={<SystemLogs />} />
                </Route>

                {/* 404 */}
                <Route
                    path="*"
                    element={<Navigate to="/dashboard" replace />}
                />
            </Routes>
        </BrowserRouter>
    );
}

export default AppRoutes;