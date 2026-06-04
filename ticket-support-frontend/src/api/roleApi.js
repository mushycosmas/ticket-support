import api from "./axios";

// ======================
// ROLES API
// ======================

// GET ALL ROLES
export const getRoles = () => api.get("/roles/roles/");

// GET SINGLE ROLE
export const getRole = (id) => api.get(`/roles/roles/${id}/`);

// CREATE ROLE
export const createRole = (data) => api.post("/roles/roles/", data);

// UPDATE ROLE
export const updateRole = (id, data) =>
    api.put(`/roles/roles/${id}/`, data);

// PARTIAL UPDATE (optional)
export const patchRole = (id, data) =>
    api.patch(`/roles/roles/${id}/`, data);

// DELETE ROLE
export const deleteRole = (id) =>
    api.delete(`/roles/roles/${id}/`);