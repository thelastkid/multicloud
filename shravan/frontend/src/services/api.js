import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export const deployApplication = (data) => {
  return API.post("/deploy", data);
};