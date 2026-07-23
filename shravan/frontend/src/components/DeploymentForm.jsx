import { useState } from "react";
import "../styles/DeploymentForm.css";
import { deployApplication } from "../services/api";

function DeploymentForm({ setResult }) {
  const [formData, setFormData] = useState({
    application: "plant-api",
    cpu: 2,
    memory: 4,
    gpu: false,
    region: "India",
    priority: "medium",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const response = await deployApplication(formData);
    console.log(JSON.stringify(response.data, null, 2));
    setResult(response.data);
  } catch (error) {
    console.error("FULL ERROR:", error);

    if (error.response) {
        console.log("Status:", error.response.status);
        console.log("Data:", error.response.data);

        setResult({
            status: "failed",
            reason: error.response.data.reason || JSON.stringify(error.response.data),
        });
      } else {
        setResult({
            status: "failed",
            reason: error.message,
         });
       }
     }
    }

  return (
    <form className="deployment-form" onSubmit={handleSubmit}>
      <label>Application Name</label>
      <input
        type="text"
        name="application"
        value={formData.application}
        onChange={handleChange}
      />

      <label>CPU Cores</label>
      <input
        type="number"
        name="cpu"
        value={formData.cpu}
        onChange={handleChange}
      />

      <label>Memory (GB)</label>
      <input
        type="number"
        name="memory"
        value={formData.memory}
        onChange={handleChange}
      />

      <label>GPU Required</label>
      <select
           name="gpu"
            value={formData.gpu.toString()}
             onChange={(e) =>
        setFormData({
            ...formData,
           gpu: e.target.value === "true",
          })
         }
        >
       <option value="false">No</option>
       <option value="true">Yes</option>
        </select>

      <label>Deployment Region</label>
      <select
        name="region"
        value={formData.region}
        onChange={handleChange}
      >
        <option value="India">India</option>
        <option value="US">US</option>
        <option value="Europe">Europe</option>
      </select>

      <label>Deployment Priority</label>
      <select
        name="priority"
        value={formData.priority}
        onChange={handleChange}
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>

      <button type="submit">Deploy</button>
    </form>
  );
}

export default DeploymentForm;