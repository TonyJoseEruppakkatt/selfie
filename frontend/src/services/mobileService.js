
import api from "./api";

export const getMyListings = async (page = 1, pageSize = 20) => {
  const response = await api.get("/api/mobiles/my-listings", {
    params: {
      page,
      page_size: pageSize,
    },
  });

  return response.data;
};

export const deleteMobile = async (mobileId) => {
  const response = await api.delete(`/api/mobiles/${mobileId}`);
  return response.data;
};

export const getBuyerRequests = async () => {
  const response = await api.get("/api/purchase-requests/buyer");
  return response.data;
};


export const getSellerRequests = async () => {
  const response = await api.get("/api/purchase-requests/seller");
  return response.data;
};

export const updatePurchaseRequestStatus = async (
  requestId,
  status
) => {
  const response = await api.patch(
    `/api/purchase-requests/${requestId}/status`,
    { status }
  );

  return response.data;
};

