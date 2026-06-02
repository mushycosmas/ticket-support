import React from "react";

const Footer = () => {
    return (
        <div className="bg-dark text-white text-center py-2">
            © {new Date().getFullYear()} Ticket Support System
        </div>
    );
};

export default Footer;