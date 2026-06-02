import React from "react";
import Header from "./partials/Header";
import Sidebar from "./partials/Sidebar";
import Footer from "./partials/Footer";

const MainLayout = ({ children }) => {
    return (
        <div className="d-flex flex-column vh-100">

            {/* HEADER */}
            <Header />

            <div className="d-flex flex-grow-1">

                {/* SIDEBAR */}
                <Sidebar />

                {/* MAIN CONTENT */}
                <main className="flex-grow-1 p-3 bg-light">
                    {children}
                </main>

            </div>

            {/* FOOTER */}
            <Footer />

        </div>
    );
};

export default MainLayout;