
import api from "./api";

export const getDashboardSummary = async () => {
  const response = await api.get("/api/mobiles/dashboard/summary");
  return response.data;
};
