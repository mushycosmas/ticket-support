import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import Dashboard from "../pages/Dashboard";
import Tickets from "../pages/Tickets";
import TicketDetails from "../pages/TicketDetails";

import Users from "../pages/admin/Users";
import Teams from "../pages/admin/Teams";

function AppRoutes() {
    return (
        <BrowserRouter>

            <MainLayout>

                <Routes>

                    <Route path="/" element={<Dashboard />} />
                    <Route path="/tickets" element={<Tickets />} />
                    <Route path="/tickets/:id" element={<TicketDetails />} />

                    <Route path="/admin/users" element={<Users />} />
                    <Route path="/admin/teams" element={<Teams />} />

                </Routes>

            </MainLayout>

        </BrowserRouter>
    );
}

export default AppRoutes;