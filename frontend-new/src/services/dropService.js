import api from "./api";

export const getDrop = async (dropId) => {
  const response = await api.get(`/drops/${dropId}`);
  return response.data;
};

export const getDropStock = async (dropId) => {
  const response = await api.get(`/drops/${dropId}/stock`);
  return response.data;
};

export const reserveDrop = async (dropId, userId) => {
  const response = await api.post(`/drops/${dropId}/reserve`, {
    user_id: userId,
  });

  return response.data;
};