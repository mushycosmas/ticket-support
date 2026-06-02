import React from "react";
import { Button, Table, Badge } from "react-bootstrap";

const UserTable = ({ users, onEdit, onDelete ,onResetPassword}) => {
    return (
        <Table striped bordered hover responsive>

            <thead>
                <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Team</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>

            <tbody>

                {users && users.length > 0 ? (
                    users.map((user, index) => (
                        <tr key={user.id}>

                            {/* INDEX */}
                            <td>{index + 1}</td>

                            {/* NAME */}
                            <td>
                                {user.first_name} {user.last_name}
                            </td>

                            {/* EMAIL */}
                            <td>{user.email}</td>

                            {/* ROLE */}
                            <td>
                                <Badge bg={
                                    user.role === "ADMIN" ? "dark" :
                                    user.role === "MANAGER" ? "primary" :
                                    user.role === "TEAM_LEAD" ? "info" :
                                    user.role === "AGENT" ? "success" :
                                    user.role === "QA" ? "warning" :
                                    "secondary"
                                }>
                                    {user.role}
                                </Badge>
                            </td>

                            {/* TEAM */}
                            <td>
                                {user.team_name ? (
                                    <Badge bg="secondary">
                                        {user.team_name}
                                    </Badge>
                                ) : (
                                    <span className="text-muted">No Team</span>
                                )}
                            </td>

                            {/* STATUS */}
                            <td>
                                {user.is_active ? (
                                    <Badge bg="success">Active</Badge>
                                ) : (
                                    <Badge bg="danger">Inactive</Badge>
                                )}
                            </td>

                            {/* ACTIONS */}
                          <td>

    <Button
        size="sm"
        className="me-2"
        variant="info"
        onClick={() => onEdit(user)}
    >
        Edit
    </Button>

    <Button
        size="sm"
        className="me-2"
        variant="warning"
        onClick={() => onResetPassword(user)}
    >
        Reset Password
    </Button>

    <Button
        size="sm"
        variant="danger"
        onClick={() => onDelete(user)}
    >
        Delete
    </Button>

</td>

                        </tr>
                    ))
                ) : (
                    <tr>
                        <td colSpan="7" className="text-center py-3">
                            No users found
                        </td>
                    </tr>
                )}

            </tbody>

        </Table>
    );
};

export default UserTable;