import React from "react";
import { Button, Table } from "react-bootstrap";

const TeamTable = ({ teams, onEdit, onDelete }) => {
    return (
        <Table bordered hover responsive>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Actions</th>
                </tr>
            </thead>

            <tbody>
                {teams.length > 0 ? (
                    teams.map((team) => (
                        <tr key={team.id}>
                            <td>{team.id}</td>
                            <td>{team.name}</td>
                            <td>{team.description}</td>

                            <td>
                                <Button
                                    size="sm"
                                    className="me-2"
                                    onClick={() => onEdit(team)}
                                >
                                    Edit
                                </Button>

                                <Button
                                    size="sm"
                                    variant="danger"
                                    onClick={() => onDelete(team)}
                                >
                                    Delete
                                </Button>
                            </td>
                        </tr>
                    ))
                ) : (
                    <tr>
                        <td colSpan="4" className="text-center">
                            No teams found
                        </td>
                    </tr>
                )}
            </tbody>
        </Table>
    );
};

export default TeamTable;