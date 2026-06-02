import React, { useEffect, useState } from "react";
import { Button, Card, Spinner, Alert } from "react-bootstrap";

import {
    getUsers,
    deleteUser,
    resetUserPassword
} from "../../api/userApi";

import UserTable from "../../components/users/UserTable";
import UserFormModal from "../../components/users/UserFormModal";
import ConfirmDeleteModal from "../../components/users/ConfirmDeleteModal";

const Users = () => {

    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [showForm, setShowForm] = useState(false);
    const [showDelete, setShowDelete] = useState(false);

    const [selectedUser, setSelectedUser] = useState(null);

    // =========================
    // LOAD USERS
    // =========================
    const loadUsers = async () => {
        try {
            setLoading(true);
            setError(null);

            const res = await getUsers();
            setUsers(res.data);

        } catch (err) {
            setError("Failed to load users. Please try again.");

        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    // =========================
    // EDIT USER
    // =========================
    const handleEdit = (user) => {
        setSelectedUser(user);
        setShowForm(true);
    };

    // =========================
    // DELETE USER
    // =========================
    const handleDelete = async () => {
        if (!selectedUser) return;

        try {
            await deleteUser(selectedUser.id);
            setShowDelete(false);
            setSelectedUser(null);
            loadUsers();

        } catch (err) {
            console.error("Delete failed", err);
        }
    };

    // =========================
    // RESET PASSWORD
    // =========================
    const handleResetPassword = async (user) => {

        if (!window.confirm("Reset password to support123?")) return;

        try {
            await resetUserPassword(user.id);
            alert("Password reset successfully");

        } catch (err) {
            console.error("Reset password failed", err);
            alert("Failed to reset password");
        }
    };

    return (
        <div className="container mt-4">

            {/* HEADER */}
            <Card className="mb-3">
                <Card.Body className="d-flex justify-content-between align-items-center">

                    <h4 className="mb-0">User Management</h4>

                    <Button
                        onClick={() => {
                            setSelectedUser(null);
                            setShowForm(true);
                        }}
                    >
                        + Create User
                    </Button>

                </Card.Body>
            </Card>

            {/* ERROR */}
            {error && (
                <Alert variant="danger">
                    {error}
                </Alert>
            )}

            {/* TABLE */}
            <Card>
                <Card.Body>

                    {loading ? (
                        <div className="text-center py-4">
                            <Spinner animation="border" />
                        </div>

                    ) : (
                        <UserTable
                            users={users}
                            onEdit={handleEdit}
                            onDelete={(user) => {
                                setSelectedUser(user);
                                setShowDelete(true);
                            }}
                            onResetPassword={handleResetPassword}
                        />
                    )}

                </Card.Body>
            </Card>

            {/* CREATE / EDIT MODAL */}
            <UserFormModal
                show={showForm}
                onHide={() => setShowForm(false)}
                user={selectedUser}
                onSuccess={() => {
                    setShowForm(false);
                    loadUsers();
                }}
            />

            {/* DELETE CONFIRM MODAL */}
            <ConfirmDeleteModal
                show={showDelete}
                onHide={() => {
                    setShowDelete(false);
                    setSelectedUser(null);
                }}
                onConfirm={handleDelete}
            />

        </div>
    );
};

export default Users;