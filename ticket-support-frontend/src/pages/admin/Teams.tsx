import React, { useEffect, useState } from "react";

import { getTeams, deleteTeam } from "../../api/teamApi";
import TeamTable from "../../components/teams/TeamTable";
import TeamFormModal from "../../components/teams/TeamFormModal";
import ConfirmDeleteModal from "../../components/teams/ConfirmDeleteModal";

type Team = {
  id: number;
  name: string;
  description?: string;
};

const Teams: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  // =====================
  // LOAD TEAMS
  // =====================
  const loadTeams = async () => {
    try {
      setLoading(true);
      const res = await getTeams();
      setTeams(res.data);
    } catch (err) {
      console.error("Failed to load teams", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTeams();
  }, []);

  // =====================
  // DELETE TEAM
  // =====================
  const handleDelete = async () => {
    if (!selectedTeam) return;

    try {
      await deleteTeam(selectedTeam.id);
      setShowDelete(false);
      setSelectedTeam(null);
      loadTeams();
    } catch (err) {
      console.error("Failed to delete team", err);
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* HEADER */}
      <div className="bg-white shadow rounded-lg mb-4">
        <div className="flex justify-between items-center p-4">
          <h2 className="text-2xl font-semibold text-gray-800">Teams</h2>

          <button
            onClick={() => {
              setSelectedTeam(null);
              setShowForm(true);
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            + Add Team
          </button>
        </div>
      </div>

      {/* CONTENT */}
      <div className="bg-white shadow rounded-lg p-4">
        {loading ? (
          <div className="flex justify-center py-10">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <TeamTable
            teams={teams}
            onEdit={(team: Team) => {
              setSelectedTeam(team);
              setShowForm(true);
            }}
            onDelete={(team: Team) => {
              setSelectedTeam(team);
              setShowDelete(true);
            }}
          />
        )}
      </div>

      {/* FORM MODAL */}
      <TeamFormModal
        show={showForm}
        onHide={() => setShowForm(false)}
        team={selectedTeam}
        onSuccess={loadTeams}
      />

      {/* DELETE MODAL */}
      <ConfirmDeleteModal
        show={showDelete}
        onHide={() => setShowDelete(false)}
        onConfirm={handleDelete}
      />
    </div>
  );
};

export default Teams;