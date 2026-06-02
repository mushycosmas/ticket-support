import React from "react";
import { Outlet } from "react-router-dom";

import Header from "./partials/Header";
import Sidebar from "./partials/Sidebar";
import Footer from "./partials/Footer";

const MainLayout = () => {
    return (
        <div className="d-flex flex-column vh-100">

            {/* HEADER */}
            <Header />

            <div className="d-flex flex-grow-1">

                {/* SIDEBAR */}
                <Sidebar />

                {/* MAIN CONTENT */}
                <main className="flex-grow-1 p-3 bg-light">
                    <Outlet />   {/* 🔥 FIX IS HERE */}
                </main>

            </div>

            {/* FOOTER */}
            <Footer />

        </div>
    );
};

export default MainLayout;