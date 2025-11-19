import React, { useState } from "react";
import { addToCompare } from "../api";

export default function CompareButton({ userId, articleId }) {
  const [added, setAdded] = useState(false);

  const add = async () => {
    await addToCompare({ userId, articleId });
    setAdded(true);
  };

  return (
    <button
      onClick={add}
      className={`px-3 py-2 rounded-md ${
        added ? "bg-blue-500 text-white" : "bg-gray-300"
      }`}
    >
      {added ? "Added" : "Compare"}
    </button>
  );
}
