import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Card, Table, Button, Badge, Spinner } from "react-bootstrap";

import {
    getTickets,
    deleteTicket,
    resolveTicket,
    closeTicket
} from "../../api/ticketApi";

import CreateTicketModal from "../../components/tickets/CreateTicketModal";
import TicketViewModal from "../../components/tickets/TicketViewModal";
import ConfirmModal from "../../components/common/ConfirmModal";

const Tickets = () => {
    const location = useLocation();
    const user = JSON.parse(localStorage.getItem("user"));

    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    const [showCreate, setShowCreate] = useState(false);
    const [showView, setShowView] = useState(false);

    const [selectedTicket, setSelectedTicket] = useState(null);

    const [showDelete, setShowDelete] = useState(false);
    const [deleteId, setDeleteId] = useState(null);

    // =====================
    // LOAD TICKETS
    // =====================
   const loadTickets = async () => {
    setLoading(true);

    try {
        const res = await getTickets();

        let data = Array.isArray(res.data)
            ? res.data
            : res.data?.results || [];

        switch (location.pathname) {
            case "/tickets/assigned":
                data = data.filter(
                    (ticket) =>
                        ticket.assigned_to ||
                        ticket.assigned_to_id
                );
                break;

            case "/tickets/unassigned":
                data = data.filter(
                    (ticket) =>
                        !ticket.assigned_to &&
                        !ticket.assigned_to_id
                );
                break;

            case "/tickets/open":
                data = data.filter(
                    (ticket) =>
                        String(ticket.status).toUpperCase() === "OPEN"
                );
                break;

            case "/tickets/in-progress":
                data = data.filter(
                    (ticket) =>
                        String(ticket.status).toUpperCase() === "IN_PROGRESS"
                );
                break;

            case "/tickets/resolved":
                data = data.filter(
                    (ticket) =>
                        String(ticket.status).toUpperCase() === "RESOLVED"
                );
                break;

            case "/tickets/closed":
                data = data.filter(
                    (ticket) =>
                        String(ticket.status).toUpperCase() === "CLOSED"
                );
                break;

            default:
                break;
        }

        setTickets(data);
    } catch (err) {
        console.error(err?.response?.data || err);
    } finally {
        setLoading(false);
    }
};
    useEffect(() => {
        loadTickets();
    }, [location.pathname]);

    // =====================
    // DELETE
    // =====================
    const confirmDelete = (id) => {
        setDeleteId(id);
        setShowDelete(true);
    };

    const handleDelete = async () => {
        try {
            await deleteTicket(deleteId);
            setDeleteId(null);
            loadTickets();
        } catch (err) {
            console.error(err?.response?.data || err);
        }
    };

    // =====================
    // WORKFLOW ACTIONS
    // =====================
    const handleResolve = async (id) => {
        try {
            await resolveTicket(id);
            loadTickets();
        } catch (err) {
            console.error(err?.response?.data || err);
        }
    };

    const handleClose = async (id) => {
        try {
            await closeTicket(id);
            loadTickets();
        } catch (err) {
            console.error(err?.response?.data || err);
        }
    };

    // =====================
    // HELPERS
    // =====================
    const getAssignedId = (ticket) => {
        return (
            ticket.assigned_to_id ??
            ticket.assigned_to?.id ??
            ticket.assigned_to
        );
    };

    const isAssignedAgent = (ticket) => {
        if (user?.role !== "AGENT") return false;

        return Number(getAssignedId(ticket)) === Number(user?.id);
    };

    const canResolve = (ticket) => {
        return (
            isAssignedAgent(ticket) &&
            String(ticket.status).toUpperCase() === "IN_PROGRESS"
        );
    };

    const canClose = (ticket) => {
        return (
            (user?.role === "ADMIN" ||
                user?.role === "TEAM_LEAD") &&
            String(ticket.status).toUpperCase() === "RESOLVED"
        );
    };

    // =====================
    // PAGE TITLE
    // =====================
    const pageTitle = (() => {
    switch (location.pathname) {
        case "/tickets/assigned":
            return "Assigned Tickets";

        case "/tickets/unassigned":
            return "Unassigned Tickets";

        case "/tickets/open":
            return "Open Tickets";

        case "/tickets/in-progress":
            return "In Progress Tickets";

        case "/tickets/resolved":
            return "Resolved Tickets";

        case "/tickets/closed":
            return "Closed Tickets";

        default:
            return "All Tickets";
    }
})();

    return (
        <div className="container-fluid mt-4">

            {/* HEADER */}
            <Card className="mb-3">
                <Card.Body className="d-flex justify-content-between align-items-center">
                    <h4 className="mb-0">{pageTitle}</h4>

                    {(user?.role === "ADMIN" ||
                        user?.role === "TEAM_LEAD") && (
                        <Button onClick={() => setShowCreate(true)}>
                            + Create Ticket
                        </Button>
                    )}
                </Card.Body>
            </Card>

            {/* TABLE */}
            <Card>
                <Card.Body>

                    {loading ? (
                        <div className="text-center py-4">
                            <Spinner animation="border" />
                        </div>
                    ) : (
                        <Table striped bordered hover responsive>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Customer</th>
                                    <th>Title</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {tickets.length === 0 ? (
                                    <tr>
                                        <td
                                            colSpan="5"
                                            className="text-center"
                                        >
                                            No tickets found
                                        </td>
                                    </tr>
                                ) : (
                                    tickets.map((t) => (
                                        <tr key={t.id}>
                                            <td>{t.id}</td>
                                            <td>{t.customer_name}</td>
                                            <td>{t.title}</td>

                                            <td>
                                                <Badge bg="info">
                                                    {t.status}
                                                </Badge>
                                            </td>

                                            <td className="d-flex gap-1 flex-wrap">

                                                <Button
                                                    size="sm"
                                                    onClick={() => {
                                                        setSelectedTicket(t);
                                                        setShowView(true);
                                                    }}
                                                >
                                                    View
                                                </Button>

                                                {user?.role === "ADMIN" && (
                                                    <Button
                                                        size="sm"
                                                        variant="danger"
                                                        onClick={() =>
                                                            confirmDelete(
                                                                t.id
                                                            )
                                                        }
                                                    >
                                                        Delete
                                                    </Button>
                                                )}

                                                {canResolve(t) && (
                                                    <Button
                                                        size="sm"
                                                        variant="warning"
                                                        onClick={() =>
                                                            handleResolve(
                                                                t.id
                                                            )
                                                        }
                                                    >
                                                        Resolve
                                                    </Button>
                                                )}

                                                {canClose(t) && (
                                                    <Button
                                                        size="sm"
                                                        variant="success"
                                                        onClick={() =>
                                                            handleClose(
                                                                t.id
                                                            )
                                                        }
                                                    >
                                                        Close
                                                    </Button>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </Table>
                    )}

                </Card.Body>
            </Card>

            {/* CREATE MODAL */}
            <CreateTicketModal
                show={showCreate}
                onHide={() => setShowCreate(false)}
                onSuccess={loadTickets}
            />

            {/* VIEW MODAL */}
            <TicketViewModal
                show={showView}
                onHide={() => setShowView(false)}
                ticket={selectedTicket}
                onRefresh={loadTickets}
            />

            {/* DELETE CONFIRMATION */}
            <ConfirmModal
                show={showDelete}
                onHide={() => setShowDelete(false)}
                title="Delete Ticket"
                message="Are you sure you want to delete this ticket?"
                onConfirm={handleDelete}
            />
        </div>
    );
};

export default Tickets;