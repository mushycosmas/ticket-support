import React, { useEffect, useState } from "react";
import { Button, Card, Spinner } from "react-bootstrap";

import { getTeams, deleteTeam } from "../../api/teamApi";
import TeamTable from "../../components/teams/TeamTable";
import TeamFormModal from "../../components/teams/TeamFormModal";
import ConfirmDeleteModal from "../../components/teams/ConfirmDeleteModal";

const Teams = () => {

    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);

    const [showForm, setShowForm] = useState(false);
    const [showDelete, setShowDelete] = useState(false);

    const [selectedTeam, setSelectedTeam] = useState(null);

    const loadTeams = async () => {
        setLoading(true);
        const res = await getTeams();
        setTeams(res.data);
        setLoading(false);
    };

    useEffect(() => {
        loadTeams();
    }, []);

    const handleDelete = async () => {
        await deleteTeam(selectedTeam.id);
        setShowDelete(false);
        loadTeams();
    };

    return (
        <div className="container mt-4">

            <Card className="mb-3">
                <Card.Body className="d-flex justify-content-between">
                    <h4>Teams</h4>

                    <Button onClick={() => {
                        setSelectedTeam(null);
                        setShowForm(true);
                    }}>
                        + Add Team
                    </Button>
                </Card.Body>
            </Card>

            <Card>
                <Card.Body>

                    {loading ? (
                        <Spinner />
                    ) : (
                        <TeamTable
                            teams={teams}
                            onEdit={(team) => {
                                setSelectedTeam(team);
                                setShowForm(true);
                            }}
                            onDelete={(team) => {
                                setSelectedTeam(team);
                                setShowDelete(true);
                            }}
                        />
                    )}

                </Card.Body>
            </Card>

            <TeamFormModal
                show={showForm}
                onHide={() => setShowForm(false)}
                team={selectedTeam}
                onSuccess={loadTeams}
            />

            <ConfirmDeleteModal
                show={showDelete}
                onHide={() => setShowDelete(false)}
                onConfirm={handleDelete}
            />

        </div>
    );
};

export default Teams;