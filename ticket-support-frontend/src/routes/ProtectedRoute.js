import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children, allowedRoles }) => {

    const token = localStorage.getItem("token");
    const user = JSON.parse(localStorage.getItem("user"));

    // ❌ not logged in
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // ❌ role restriction (THIS IS THE MISSING PART)
    if (allowedRoles && !allowedRoles.includes(user?.role)) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
};

export default ProtectedRoute;