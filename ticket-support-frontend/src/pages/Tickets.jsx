import React, { useEffect, useState } from "react";
import { Card, Table, Button, Badge, Spinner } from "react-bootstrap";

import {
    getTickets,
    deleteTicket,
    resolveTicket,
    closeTicket
} from "../api/ticketApi";

import CreateTicketModal from "../components/tickets/CreateTicketModal";
import TicketViewModal from "../components/tickets/TicketViewModal";
import ConfirmModal from "../components/common/ConfirmModal";

const Tickets = () => {

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
            setTickets(res.data);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTickets();
    }, []);

    // =====================
    // DELETE
    // =====================
    const confirmDelete = (id) => {
        setDeleteId(id);
        setShowDelete(true);
    };

    const handleDelete = async () => {
        await deleteTicket(deleteId);
        setDeleteId(null);
        loadTickets();
    };

    // =====================
    // WORKFLOW ACTIONS
    // =====================
    const handleResolve = async (id) => {
        await resolveTicket(id);
        loadTickets();
    };

    const handleClose = async (id) => {
        await closeTicket(id);
        loadTickets();
    };

    // =====================
    // ROLE HELPERS
    // =====================
    const isAgentOwner = (ticket) => {
        return user?.role === "AGENT" && ticket.assigned_to === user?.id;
    };

    const canClose = () => {
        return user?.role === "ADMIN" || user?.role === "TEAM_LEAD";
    };

    return (
        <div className="container-fluid mt-4">

            {/* HEADER */}
            <Card className="mb-3">
                <Card.Body className="d-flex justify-content-between">
                    <h4>Tickets</h4>

                    {(user?.role === "ADMIN" || user?.role === "TEAM_LEAD") && (
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
                        <Spinner />
                    ) : (
                        <Table striped bordered hover>
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
                                {tickets.map(t => (
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

                                            {/* VIEW */}
                                            <Button
                                                size="sm"
                                                onClick={() => {
                                                    setSelectedTicket(t);
                                                    setShowView(true);
                                                }}
                                            >
                                                View
                                            </Button>

                                            {/* DELETE (ADMIN ONLY) */}
                                            {user?.role === "ADMIN" && (
                                                <Button
                                                    size="sm"
                                                    variant="danger"
                                                    onClick={() => confirmDelete(t.id)}
                                                >
                                                    Delete
                                                </Button>
                                            )}

                                            {/* ===================== */}
                                            {/* AGENT ACTIONS */}
                                            {/* ===================== */}
                                            {isAgentOwner(t) && t.status === "IN_PROGRESS" && (
                                                <Button
                                                    size="sm"
                                                    variant="warning"
                                                    onClick={() => handleResolve(t.id)}
                                                >
                                                    Resolve
                                                </Button>
                                            )}

                                            {/* ===================== */}
                                            {/* CLOSE ACTION */}
                                            {/* ===================== */}
                                            {canClose() && t.status === "RESOLVED" && (
                                                <Button
                                                    size="sm"
                                                    variant="success"
                                                    onClick={() => handleClose(t.id)}
                                                >
                                                    Close
                                                </Button>
                                            )}

                                        </td>

                                    </tr>
                                ))}
                            </tbody>

                        </Table>
                    )}

                </Card.Body>
            </Card>

            {/* MODALS */}
            <CreateTicketModal
                show={showCreate}
                onHide={() => setShowCreate(false)}
                onSuccess={loadTickets}
            />

            <TicketViewModal
                show={showView}
                onHide={() => setShowView(false)}
                ticket={selectedTicket}
                onRefresh={loadTickets}
            />

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