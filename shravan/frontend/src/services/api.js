import axios from "axios";

const API = axios.create({
  baseURL: "https://multicloud-api.onrender.com",
});

export const deployApplication = (data) => {
  return API.post("/deploy", data);
};