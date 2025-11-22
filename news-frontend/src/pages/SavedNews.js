import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getBookmarks, removeBookmark } from "../api";

const fallbackImg = "https://placehold.co/600x400?text=No+Image";

const DEFAULT_FOLDERS = [
  "Technology",
  "Business",
  "Politics",
  "Sports",
  "Entertainment",
  "Science",
  "Health",
  "Unsorted",
];

const FOLDER_KEYWORDS = {
  Technology: ["tech", "ai", "technology", "software", "hardware"],
  Business: ["market", "business", "finance", "stock", "company"],
  Politics: ["politics", "election", "government", "policy"],
  Sports: ["football", "cricket", "sports", "tournament"],
  Entertainment: ["movie", "film", "music", "tv", "series"],
  Science: ["research", "study", "scientist", "space", "nasa"],
  Health: ["health", "medical", "disease", "covid", "fitness"],
};

function prettyDate(ts) {
  if (!ts) return "-";
  return new Date(ts).toLocaleString();
}

function autoCategorize(text = "") {
  const lower = text.toLowerCase();
  let best = "Unsorted";
  let max = 0;

  for (const [folder, words] of Object.entries(FOLDER_KEYWORDS)) {
    let score = 0;
    words.forEach((w) => lower.includes(w) && score++);
    if (score > max) {
      max = score;
      best = folder;
    }
  }

  return best;
}

function getLoggedInUser() {
  const email = localStorage.getItem("user_email");
  const token = localStorage.getItem("token");
  return token && email ? { email } : null;
}

export default function SavedNews() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [bookmarks, setBookmarks] = useState([]);
  const [folders, setFolders] = useState(DEFAULT_FOLDERS);
  const [filterFolder, setFilterFolder] = useState("All");
  const [searchTxt, setSearchTxt] = useState("");
  const [loading, setLoading] = useState(true);

  const [confirm, setConfirm] = useState({
    show: false,
    message: "",
    action: null,
  });

  const [newFolder, setNewFolder] = useState("");
  const [renameTarget, setRenameTarget] = useState(null);
  const [renameValue, setRenameValue] = useState("");

  // --------------------------------------------------
  // LOAD SAVED BOOKMARKS
  // --------------------------------------------------
  useEffect(() => {
    const logged = getLoggedInUser();
    setUser(logged);

    if (!logged) {
      setLoading(false);
      return;
    }

    const loadBookmarks = async () => {
      try {
        const response = await getBookmarks(logged.email);
        const rows = response.data || [];

        const parsed = rows.map((row) => {
          const a = row.article || {};

          const image =
            a.image ||
            a.image_url ||
            a.urlToImage ||
            a.thumbnail ||
            a.img ||
            a.picture ||
            fallbackImg;

          return {
            title: a.title || "",
            description: a.description || "",
            url: row.article_url,
            image,
            savedAt: new Date(row.created_at).getTime(),
            folder:
              a.folder ||
              autoCategorize(`${a.title || ""} ${a.description || ""}`),
            source: a.source?.name || a.source || "Unknown",
          };
        });

        const folderSet = new Set(DEFAULT_FOLDERS);
        parsed.forEach((item) => folderSet.add(item.folder));

        setFolders([...folderSet]);
        setBookmarks(parsed);
      } catch (err) {
        console.error("❌ Error loading bookmarks:", err);
      }

      setLoading(false);
    };

    loadBookmarks();
  }, []);

  // --------------------------------------------------
  // CONFIRM DIALOG
  // --------------------------------------------------
  const askConfirm = (msg, action) => {
    setConfirm({ show: true, message: msg, action });
  };

  // --------------------------------------------------
  // REMOVE BOOKMARK
  // --------------------------------------------------
  const removeItem = (url) => {
    askConfirm("Remove this saved article?", async () => {
      try {
        await removeBookmark(user.email, url);
        setBookmarks((prev) => prev.filter((b) => b.url !== url));
      } catch (err) {
        console.error("❌ Remove failed:", err);
      }
    });
  };

  // --------------------------------------------------
  // FOLDER ACTIONS
  // --------------------------------------------------
  const moveItem = (url, folder) => {
    setBookmarks((prev) =>
      prev.map((b) => (b.url === url ? { ...b, folder } : b))
    );
  };

  const createFolder = () => {
    const name = newFolder.trim();
    if (!name) return alert("Folder name required.");
    if (folders.includes(name)) return alert("Already exists.");
    setFolders((f) => [...f, name]);
    setNewFolder("");
  };

  const renameFolder = () => {
    const name = renameValue.trim();
    if (!name) return;
    if (folders.includes(name) && name !== renameTarget)
      return alert("Already exists.");

    setFolders((prev) =>
      prev.map((f) => (f === renameTarget ? name : f))
    );

    setBookmarks((prev) =>
      prev.map((b) =>
        b.folder === renameTarget ? { ...b, folder: name } : b
      )
    );

    setRenameTarget(null);
    setRenameValue("");
  };

  const deleteFolder = (folder) => {
    askConfirm(`Delete folder "${folder}"?`, () => {
      setFolders((prev) => prev.filter((f) => f !== folder));
      setBookmarks((prev) =>
        prev.map((b) =>
          b.folder === folder ? { ...b, folder: "Unsorted" } : b
        )
      );
    });
  };

  // --------------------------------------------------
  // FILTER & SEARCH
  // --------------------------------------------------
  const filtered = bookmarks.filter((b) => {
    if (filterFolder !== "All" && b.folder !== filterFolder) return false;
    const q = searchTxt.toLowerCase();
    return `${b.title} ${b.description}`.toLowerCase().includes(q);
  });

  const grouped = filtered.reduce((acc, item) => {
    acc[item.folder] = acc[item.folder] || [];
    acc[item.folder].push(item);
    return acc;
  }, {});

  // --------------------------------------------------
  // UI STATES
  // --------------------------------------------------
  if (loading) return <div className="p-10">Loading...</div>;

  if (!user)
    return (
      <div className="p-10 text-center">
        <h1 className="text-3xl font-bold mb-4">Saved Articles</h1>
        <p>You must log in to view bookmarks.</p>
        <button
          onClick={() => navigate("/login")}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded"
        >
          Login
        </button>
      </div>
    );

  if (bookmarks.length === 0)
    return (
      <div className="p-10 text-center">
        <h1 className="text-3xl font-bold mb-4">Saved Articles</h1>
        <p>No saved articles.</p>
        <img
          src="https://cdn-icons-png.flaticon.com/512/4076/4076508.png"
          className="w-40 mx-auto mt-6 opacity-70"
          alt = " "
        />
      </div>
    );

  // --------------------------------------------------
  // MAIN UI
  // --------------------------------------------------
  return (
    <div className="p-6 max-w-7xl mx-auto">

      {/* HEADER */}
      <div className="flex justify-between mb-6">
        <h1 className="text-3xl font-bold">
          Saved <span className="text-indigo-600">Articles</span>
        </h1>

        <div className="flex gap-3">
          <input
            className="border px-3 py-2 rounded"
            placeholder="Search..."
            value={searchTxt}
            onChange={(e) => setSearchTxt(e.target.value)}
          />

          <select
            className="border px-3 py-2 rounded"
            value={filterFolder}
            onChange={(e) => setFilterFolder(e.target.value)}
          >
            <option value="All">All</option>
            {folders.map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
        </div>
      </div>

      {/* FOLDER MANAGER */}
      <div className="bg-white p-4 shadow rounded mb-8">

        <h2 className="font-semibold text-lg mb-3">Manage Folders</h2>

        <div className="flex gap-3 mb-4">
          <input
            className="border px-3 py-2 rounded"
            placeholder="New folder"
            value={newFolder}
            onChange={(e) => setNewFolder(e.target.value)}
          />
          <button
            onClick={createFolder}
            className="bg-indigo-600 text-white px-4 py-2 rounded"
          >
            Create
          </button>
        </div>

        {/* Folder List */}
        <div className="flex flex-wrap gap-2">
          {folders.map((f) => (
            <div
              key={f}
              className="bg-gray-100 px-3 py-1 rounded flex items-center gap-2"
            >
              <span
                className={`cursor-pointer ${
                  filterFolder === f ? "font-bold text-indigo-700" : ""
                }`}
                onClick={() => setFilterFolder(f)}
              >
                {f}
              </span>

              <button
                className="text-xs"
                onClick={() => {
                  setRenameTarget(f);
                  setRenameValue(f);
                }}
              >
                Rename
              </button>

              {!DEFAULT_FOLDERS.includes(f) && (
                <button
                  className="text-xs text-red-500"
                  onClick={() => deleteFolder(f)}
                >
                  Delete
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Rename */}
        {renameTarget && (
          <div className="mt-3 flex gap-2">
            <input
              className="border px-3 py-2 rounded"
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
            />

            <button
              onClick={renameFolder}
              className="px-3 py-2 bg-green-600 text-white rounded"
            >
              Save
            </button>

            <button
              onClick={() => setRenameTarget(null)}
              className="px-3 py-2 border rounded"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* ARTICLE LIST */}
      {Object.entries(grouped).map(([folder, items]) => (
        <div key={folder} className="bg-white p-5 shadow rounded mb-10">

          <h3 className="text-xl font-bold mb-4">
            {folder}{" "}
            <span className="text-gray-500 text-sm">({items.length})</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((a) => (
              <div
                key={a.url}
                className="border rounded shadow bg-white overflow-hidden"
              >
                <img
                  src={a.image}
                  onError={(e) => (e.target.src = fallbackImg)}
                  className="w-full h-40 object-cover"
                  alt = " "
                />

                <div className="p-4">
                  <h4 className="font-semibold">{a.title}</h4>

                  <p className="text-sm text-gray-600 mt-1 line-clamp-3">
                    {a.description}
                  </p>

                  <p className="text-xs text-gray-500 mt-2">
                    Saved: {prettyDate(a.savedAt)}
                  </p>

                  <div className="flex justify-between items-center mt-4">
                    <select
                      className="border px-2 py-1 rounded"
                      value={a.folder}
                      onChange={(e) => moveItem(a.url, e.target.value)}
                    >
                      {folders.map((f) => (
                        <option key={f}>{f}</option>
                      ))}
                    </select>

                    <button
                      onClick={() => removeItem(a.url)}
                      className="px-3 py-1 bg-red-600 text-white text-xs rounded"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* CONFIRM MODAL */}
      {confirm.show && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow max-w-sm text-center">
            <p className="text-lg mb-6">{confirm.message}</p>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => {
                  confirm.action && confirm.action();
                  setConfirm({ show: false });
                }}
                className="bg-red-600 text-white px-4 py-2 rounded"
              >
                Yes
              </button>

              <button
                onClick={() => setConfirm({ show: false })}
                className="px-4 py-2 border rounded"
              >
                No
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
