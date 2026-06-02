import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import Tickets from "../pages/Tickets";
import TicketDetails from "../pages/TicketDetails";

import Users from "../pages/admin/Users";
import Teams from "../pages/admin/Teams";

import ProtectedRoute from "../routes/ProtectedRoute";

function AppRoutes() {
    return (
        <BrowserRouter>

            <Routes>

                {/* ===================== */}
                {/* DEFAULT PAGE = LOGIN */}
                {/* ===================== */}
                <Route path="/" element={<Login />} />

                {/* ===================== */}
                {/* PROTECTED APP */}
                {/* ===================== */}
                <Route
                    element={
                        <ProtectedRoute>
                            <MainLayout />
                        </ProtectedRoute>
                    }
                >

                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/tickets" element={<Tickets />} />
                    <Route path="/tickets/:id" element={<TicketDetails />} />

                    <Route path="/admin/users" element={<Users />} />
                    <Route path="/admin/teams" element={<Teams />} />

                </Route>

                {/* fallback */}
                <Route path="*" element={<Navigate to="/" />} />

            </Routes>

        </BrowserRouter>
    );
}

export default AppRoutes;