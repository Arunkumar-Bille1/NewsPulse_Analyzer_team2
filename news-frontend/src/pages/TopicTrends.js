import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import axios from "axios";

function TopicTrends() {
  const [data, setData] = useState([]);
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    async function fetchTrends() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/topic-trends");
        const trendData = response.data; // expect array of objects with date and topics as keys

        if (trendData.length > 0) {
          setData(trendData);
          // Extract topic keys except 'date' for lines
          const keys = Object.keys(trendData[0]).filter(k => k !== 'date');
          setTopics(keys);
        }
      } catch (error) {
        console.error("Error fetching topic trends:", error);
      }
    }
    fetchTrends();
  }, []);

  return (
    <div className="p-5 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold mb-5">Topic Trends Over Time</h2>
      {data.length === 0 ? (
        <p>Loading topic trends...</p>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            {topics.map((topic) => (
              <Line
                key={topic}
                type="monotone"
                dataKey={topic}
                stroke={`#${Math.floor(Math.random()*16777215).toString(16)}`} // Random color
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default TopicTrends;
