import api from "./axios";

// =====================
// TEAMS API
// =====================

export const getTeams = () => api.get("/auth/teams/");

export const getTeam = (id) => api.get(`/auth/teams/${id}/`);

export const createTeam = (data) => api.post("/auth/teams/", data);

export const updateTeam = (id, data) =>
    api.patch(`/auth/teams/${id}/`, data);

export const deleteTeam = (id) =>
    api.delete(`/auth/teams/${id}/`);