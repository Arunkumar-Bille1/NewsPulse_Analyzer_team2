import React, { useState } from "react";
import { addBookmark, removeBookmark } from "../api";

export default function BookmarkButton({ userId, articleId }) {
  const [saved, setSaved] = useState(false);

  const toggle = async () => {
    if (!saved) {
      await addBookmark({ userId, articleId });
      setSaved(true);
    } else {
      await removeBookmark({ userId, articleId });
      setSaved(false);
    }
  };

  return (
    <button
      onClick={toggle}
      className={`px-3 py-2 rounded-md ${
        saved ? "bg-red-500 text-white" : "bg-gray-300"
      }`}
    >
      {saved ? "Bookmarked" : "Bookmark"}
    </button>
  );
}
